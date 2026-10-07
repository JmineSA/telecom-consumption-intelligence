# training/core/data_preparation.py
"""
PHASE 2. 

Data Preparation for Telecom Consumption Intelligence (Time-Series)

Pipeline:
1. Load users + daily_usage
2. Join and validate
3. Fix categorical typos only (NO imputation)
4. Build lag features (past-only fallbacks — no backfill from future)
5. Build calendar features
6. Create forecasting target (total_gb on day D+1)
7. Drop rows with NaN in critical columns (missingness is ~3% MCAR,
   below our 5% threshold, so dropping is cleaner than imputing)
8. Time-based split (train / val / test)
9. Save modelling dataset + split metadata
"""
import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
BASE_PATH = Path(__file__).parent.parent.parent / "data"

RAW_PATH = BASE_PATH / "raw"
PROCESSED_PATH = BASE_PATH / "processed"
CURATED_PATH = BASE_PATH / "curated"
EDA_PATH = BASE_PATH / "eda"

for p in [RAW_PATH, PROCESSED_PATH, CURATED_PATH, EDA_PATH]:
    p.mkdir(parents=True, exist_ok=True)

FORECAST_HORIZON = 1
TRAIN_FRAC = 0.70
VAL_FRAC = 0.15


# ------------------------------------------------------------------
# 1. LOAD
# ------------------------------------------------------------------
def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    users_file = RAW_PATH / "users.csv"
    usage_file = RAW_PATH / "daily_usage.parquet"

    if not users_file.exists() or not usage_file.exists():
        raise FileNotFoundError(
            f"Missing raw files. Expected:\n"
            f"  {users_file}\n"
            f"  {usage_file}\n"
            f"Run training/core/data_generator.py first."
        )

    users = pd.read_csv(users_file)
    usage = pd.read_parquet(usage_file)

    logger.info(f"Loaded users: {users.shape}")
    logger.info(f"Loaded daily_usage: {usage.shape}")

    return users, usage


# ------------------------------------------------------------------
# 2. CLEAN — typos only, no imputation
# ------------------------------------------------------------------
def clean_categoricals(usage: pd.DataFrame) -> pd.DataFrame:
    """
    Fix categorical typos only.

    Missing values are intentionally left in place — they are dropped
    later in main() after feature engineering, before the split.
    """
    usage = usage.copy()

    if "region" in usage.columns:
        usage["region"] = usage["region"].replace(
            {"gauteng": "Gauteng", "GP": "Gauteng"}
        )

    logger.info("Cleaned categorical typos (no imputation)")
    return usage


def drop_duplicates(usage: pd.DataFrame) -> pd.DataFrame:
    before = len(usage)
    usage = usage.drop_duplicates(subset=["user_id", "date"], keep="first")
    removed = before - len(usage)
    if removed > 0:
        logger.info(f"Dropped {removed:,} duplicate (user_id, date) rows")
    return usage


# ------------------------------------------------------------------
# 3. JOIN USERS + USAGE
# ------------------------------------------------------------------
def join_users(usage: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    user_cols = [
        "user_id",
        "contract_duration_months",
        "customer_tenure_months",
        "monthly_bill_zar",
        "support_calls_6months",
        "churn_probability",
        "churn_status",
    ]

    df = usage.merge(users[user_cols], on="user_id", how="left")
    logger.info(f"Joined users → shape: {df.shape}")
    return df


# ------------------------------------------------------------------
# 4. LAG FEATURES (past-only)
# ------------------------------------------------------------------
def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build lag and rolling features per user.

    Rule: every fallback uses ONLY past information.
    - lag_1d  : yesterday's value (defined for day >= 2)
    - lag_7d  : value 7 days ago  (defined for day >= 8)
    - rolling_7d_avg  : past 7 days average
    - rolling_30d_avg : past 30 days average

    For early days where lag_7d / rolling_30d aren't available,
    we fall back to lag_1d_total_gb (which IS known at prediction time).
    We do NOT backfill from future values.
    """
    df = df.sort_values(["user_id", "date"]).copy()
    group = df.groupby("user_id", sort=False)["total_gb"]

    # Lag features
    df["lag_1d_total_gb"] = group.shift(1)
    df["lag_7d_total_gb"] = group.shift(7)

    # Rolling averages (past-only via shift(1))
    df["rolling_7d_avg_gb"] = group.transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean()
    )
    df["rolling_30d_avg_gb"] = group.transform(
        lambda s: s.shift(1).rolling(30, min_periods=1).mean()
    )

    # Day-over-day change
    df["delta_1d_gb"] = df["lag_1d_total_gb"] - df["rolling_7d_avg_gb"]

    # Service-level lags
    for col in ["streaming_gb", "social_gb", "gaming_gb", "messaging_gb"]:
        df[f"lag_1d_{col}"] = df.groupby("user_id", sort=False)[col].shift(1)

    # ----------------------------------------------------------------
    # Past-only fallbacks 
    # ----------------------------------------------------------------
    # lag_7d and rolling_30d are undefined for early days.
    # Fall back to lag_1d — which IS available at prediction time.
    for col in ["lag_7d_total_gb", "rolling_30d_avg_gb"]:
        df[col] = df[col].fillna(df["lag_1d_total_gb"])

    df["delta_1d_gb"] = df["delta_1d_gb"].fillna(0.0)

    # Service lags: fill missing with 0.0 (no service usage recorded yet)
    for col in ["lag_1d_streaming_gb", "lag_1d_social_gb",
                "lag_1d_gaming_gb", "lag_1d_messaging_gb"]:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)

    logger.info("Added lag and rolling features (past-only fallbacks, no leakage)")
    return df


# ------------------------------------------------------------------
# 5. CALENDAR FEATURES
# ------------------------------------------------------------------
def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["day_of_month"] = df["date"].dt.day
    df["is_month_start"] = (df["day_of_month"] <= 3).astype(int)
    df["is_month_end"] = (df["day_of_month"] >= 28).astype(int)
    logger.info("Added calendar features")
    return df


# ------------------------------------------------------------------
# 6. TARGET: NEXT-DAY USAGE
# ------------------------------------------------------------------
def add_forecast_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["user_id", "date"]).copy()
    df["target_next_day_gb"] = (
        df.groupby("user_id", sort=False)["total_gb"].shift(-FORECAST_HORIZON)
    )

    before = len(df)
    df = df.dropna(subset=["target_next_day_gb"])
    logger.info(f"Dropped {before - len(df):,} rows without a next-day target")

    return df


# ------------------------------------------------------------------
# 7. TIME-BASED SPLIT
# ------------------------------------------------------------------
def time_based_split(df: pd.DataFrame):
    df = df.sort_values("date").copy()
    dates = np.sort(df["date"].unique())
    n_dates = len(dates)

    train_end = int(n_dates * TRAIN_FRAC)
    val_end = int(n_dates * (TRAIN_FRAC + VAL_FRAC))

    train_dates = dates[:train_end]
    val_dates = dates[train_end:val_end]
    test_dates = dates[val_end:]

    train = df[df["date"].isin(train_dates)].copy()
    val = df[df["date"].isin(val_dates)].copy()
    test = df[df["date"].isin(test_dates)].copy()

    logger.info(
        f"Time-based split → train: {len(train):,} | "
        f"val: {len(val):,} | test: {len(test):,}"
    )
    logger.info(
        f"Train dates: {pd.Timestamp(train_dates[0]).date()} → "
        f"{pd.Timestamp(train_dates[-1]).date()}"
    )
    logger.info(
        f"Val dates:   {pd.Timestamp(val_dates[0]).date()} → "
        f"{pd.Timestamp(val_dates[-1]).date()}"
    )
    logger.info(
        f"Test dates:  {pd.Timestamp(test_dates[0]).date()} → "
        f"{pd.Timestamp(test_dates[-1]).date()}"
    )

    return train, val, test


# ------------------------------------------------------------------
# 8. SAVE
# ------------------------------------------------------------------
def save_outputs(df, train, val, test):
    full_file = PROCESSED_PATH / "modelling_dataset.parquet"
    df.to_parquet(full_file, index=False)
    logger.info(f"Saved modelling dataset: {full_file}")

    train.to_parquet(PROCESSED_PATH / "train.parquet", index=False)
    val.to_parquet(PROCESSED_PATH / "val.parquet", index=False)
    test.to_parquet(PROCESSED_PATH / "test.parquet", index=False)
    logger.info("Saved train / val / test splits")

    df.sample(min(5000, len(df))).to_csv(
        CURATED_PATH / "sample.csv", index=False
    )
    df.sample(min(1000, len(df))).to_csv(
        EDA_PATH / "eda_sample.csv", index=False
    )

    metadata = {
        "prepared_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "columns": df.columns.tolist(),
        "target": "target_next_day_gb",
        "forecast_horizon_days": FORECAST_HORIZON,
        "split": {
            "train_rows": int(len(train)),
            "val_rows": int(len(val)),
            "test_rows": int(len(test)),
            "train_dates": [
                str(train["date"].min().date()),
                str(train["date"].max().date()),
            ],
            "val_dates": [
                str(val["date"].min().date()),
                str(val["date"].max().date()),
            ],
            "test_dates": [
                str(test["date"].min().date()),
                str(test["date"].max().date()),
            ],
        },
        "target_stats": {
            "mean": float(df["target_next_day_gb"].mean()),
            "std": float(df["target_next_day_gb"].std()),
            "min": float(df["target_next_day_gb"].min()),
            "max": float(df["target_next_day_gb"].max()),
        },
        "leakage_policy": {
            "imputation": "none — rows with missing categoricals are dropped",
            "lag_fallbacks": "past-only — early days use lag_1d as proxy",
            "missingness_threshold": "5% (below this, drop rather than impute)",
        },
    }
    with open(PROCESSED_PATH / "preparation_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved preparation metadata")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("DATA PREPARATION — START")
    logger.info("=" * 60)

    users, usage = load_raw_data()
    usage = clean_categoricals(usage)
    usage = drop_duplicates(usage)
    df = join_users(usage, users)

    df = add_lag_features(df)
    df = add_calendar_features(df)
    df = add_forecast_target(df)

    # Drop rows without lag_1d (first day per user — no history yet)
    before = len(df)
    df = df.dropna(subset=["lag_1d_total_gb"])
    logger.info(f"Dropped {before - len(df):,} rows without lag_1d features")

    # ----------------------------------------------------------------
    # Drop rows with NaN in critical columns.
    #
    # Decision: missingness is ~3% MCAR (injected by the generator), which
    # is below our 5% drop threshold. Dropping is cleaner than imputing
    # and eliminates any imputation-leakage questions.
    # ----------------------------------------------------------------
    critical_cols = [
        "age_group",
        "network_type",
        "region",
        "lag_1d_total_gb",
        "rolling_7d_avg_gb",
        "rolling_30d_avg_gb",
        "target_next_day_gb",
    ]
    before = len(df)
    df = df.dropna(subset=critical_cols)
    dropped = before - len(df)
    pct = dropped / before * 100 if before else 0
    logger.info(
        f"Dropped {dropped:,} rows ({pct:.2f}%) with NaN in critical columns"
    )

    # Safety net — should be no-op but catches anything unexpected
    before = len(df)
    df = df.dropna()
    if before != len(df):
        logger.info(f"Dropped {before - len(df):,} additional rows with residual NaN")
    else:
        logger.info("No residual NaN remaining")

    train, val, test = time_based_split(df)
    save_outputs(df, train, val, test)

    logger.info("=" * 60)
    logger.info("DATA PREPARATION — COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Final shape: {df.shape}")


if __name__ == "__main__":
    main()