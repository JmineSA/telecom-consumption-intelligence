"""Feature building. Mirrors training/core/data_preparation.py so uploads match training."""
import pandas as pd

from .config import TARGET


def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["date"]
    df["day_of_week"] = d.dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["day_of_month"] = d.dt.day
    df["is_month_start"] = (df["day_of_month"] <= 3).astype(int)
    df["is_month_end"] = (df["day_of_month"] >= 28).astype(int)
    if "day_index" not in df.columns:
        df["day_index"] = (d - d.min()).dt.days + 1
    return df


def add_target(df: pd.DataFrame) -> pd.DataFrame:
    """Next-day usage per customer. The last day of each customer stays empty (it is the forecast)."""
    df = df.sort_values(["user_id", "date"]).reset_index(drop=True)
    df[TARGET] = df.groupby("user_id", sort=False)["total_gb"].shift(-1)
    return df


def add_lags(df: pd.DataFrame) -> pd.DataFrame:
    """Lag and rolling features. Past information only, no leakage."""
    df = df.sort_values(["user_id", "date"]).reset_index(drop=True)
    g = df.groupby("user_id", sort=False)["total_gb"]
    shifted = g.shift(1)
    by_user = shifted.groupby(df["user_id"], sort=False)
    df["lag_1d_total_gb"] = shifted
    df["lag_7d_total_gb"] = g.shift(7)
    df["rolling_7d_avg_gb"] = by_user.rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    df["rolling_30d_avg_gb"] = by_user.rolling(30, min_periods=1).mean().reset_index(level=0, drop=True)
    df["delta_1d_gb"] = df["lag_1d_total_gb"] - df["rolling_7d_avg_gb"]
    for col in ["streaming_gb", "social_gb", "gaming_gb", "messaging_gb"]:
        df[f"lag_1d_{col}"] = df.groupby("user_id", sort=False)[col].shift(1)
    for col in ["lag_7d_total_gb", "rolling_30d_avg_gb"]:
        df[col] = df[col].fillna(df["lag_1d_total_gb"])
    df["delta_1d_gb"] = df["delta_1d_gb"].fillna(0.0)
    for col in ["lag_1d_streaming_gb", "lag_1d_social_gb", "lag_1d_gaming_gb", "lag_1d_messaging_gb"]:
        df[col] = df[col].fillna(0.0)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_lags(df)
    df = add_calendar(df)
    df = add_target(df)
    return df
