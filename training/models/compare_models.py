
"""
Compare a focused set of regressors on the same time-based split.

Only the fast, production-viable models are included — slow "classic"
GradientBoosting and generic RandomForest are omitted because they
don't offer accuracy gains that justify their training time.

Output: reports/model_comparison.csv + reports/model_comparison.md
"""

import sys
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
src_root = project_root / "src"
if src_root.exists():
    sys.path.insert(0, str(src_root))
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

from training.pipelines.preprocessing_pipeline import build_pipeline

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMRegressor
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False


TARGET = "target_next_day_gb"
PROCESSED = project_root / "data" / "processed"
REPORTS_DIR = project_root / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------------
# FOCUSED CANDIDATES — fast, production-viable
# ------------------------------------------------------------------
def get_candidates():
    models = {
        # Baseline — cheap, interpretable, tells us how much non-linearity matters
        "Ridge": Ridge(alpha=1.0, random_state=42),

        # Primary candidate — chosen in yesterday's comparison
        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=400,
            max_depth=6,
            learning_rate=0.05,
            min_samples_leaf=20,
            l2_regularization=1.0,
            random_state=42,
        ),
    }

    # Optional: if the libs are installed, add them for context
    if HAS_XGB:
        models["XGBoost"] = XGBRegressor(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            n_jobs=-1,
            random_state=42,
            tree_method="hist",
        )

    if HAS_LGBM:
        models["LightGBM"] = LGBMRegressor(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            n_jobs=-1,
            random_state=42,
            verbose=-1,
        )

    return models


def compute_metrics(y_true, y_pred):
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
        "mape": float(
            np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-6, None))) * 100
        ),
    }


def main():
    print("=" * 70)
    print("MODEL COMPARISON — MOBILE DATA CONSUMPTION FORECASTER (D+1)")
    print("=" * 70)
    print(f"XGBoost available:  {HAS_XGB}")
    print(f"LightGBM available: {HAS_LGBM}")

    train = pd.read_parquet(PROCESSED / "train.parquet")
    val = pd.read_parquet(PROCESSED / "val.parquet")
    test = pd.read_parquet(PROCESSED / "test.parquet")
    print(f"\nTrain: {train.shape} | Val: {val.shape} | Test: {test.shape}")

    drop_cols = [TARGET, "user_id", "date"]
    X_train = train.drop(columns=[c for c in drop_cols if c in train.columns])
    y_train = train[TARGET]
    X_val = val.drop(columns=[c for c in drop_cols if c in val.columns])
    y_val = val[TARGET]
    X_test = test.drop(columns=[c for c in drop_cols if c in test.columns])
    y_test = test[TARGET]

    results = []
    candidates = get_candidates()

    for name, model in candidates.items():
        print("\n" + "-" * 60)
        print(f"Training: {name}")
        print("-" * 60)
        sys.stdout.flush()

        pipeline = Pipeline(steps=[
            ("preprocessor", build_pipeline()),
            ("regressor", model),
        ])

        t0 = time.time()
        try:
            pipeline.fit(X_train, y_train)
        except KeyboardInterrupt:
            print("  SKIPPED (user interrupted)")
            continue
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")
            continue
        train_time = time.time() - t0

        try:
            y_train_pred = pipeline.predict(X_train)
            y_val_pred = pipeline.predict(X_val)
            y_test_pred = pipeline.predict(X_test)
        except Exception as e:
            print(f"  PREDICT FAILED: {type(e).__name__}: {e}")
            continue

        train_m = compute_metrics(y_train, y_train_pred)
        val_m = compute_metrics(y_val, y_val_pred)
        test_m = compute_metrics(y_test, y_test_pred)

        print(f"  Train R²: {train_m['r2']:.4f} | Val R²: {val_m['r2']:.4f} | Test R²: {test_m['r2']:.4f}")
        print(f"  Test MAE: {test_m['mae']:.4f} GB | Test MAPE: {test_m['mape']:.2f}%")
        print(f"  Train time: {train_time:.1f}s")
        sys.stdout.flush()

        results.append({
            "model": name,
            "train_time_s": round(train_time, 1),
            "train_rmse": round(train_m["rmse"], 4),
            "train_mae": round(train_m["mae"], 4),
            "train_r2": round(train_m["r2"], 4),
            "val_rmse": round(val_m["rmse"], 4),
            "val_mae": round(val_m["mae"], 4),
            "val_r2": round(val_m["r2"], 4),
            "test_rmse": round(test_m["rmse"], 4),
            "test_mae": round(test_m["mae"], 4),
            "test_r2": round(test_m["r2"], 4),
            "test_mape": round(test_m["mape"], 2),
            "overfit_gap": round(train_m["r2"] - val_m["r2"], 4),
        })

    if not results:
        print("\nNo models completed. Nothing to report.")
        return

    results_df = pd.DataFrame(results).sort_values("test_r2", ascending=False)
    results_df.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)

    print("\n" + "=" * 70)
    print("FINAL RANKING (by Test R²)")
    print("=" * 70)
    print(results_df[[
        "model", "train_r2", "val_r2", "test_r2",
        "test_mae", "test_mape", "overfit_gap", "train_time_s",
    ]].to_string(index=False))

    # ----------------------------------------------------------------
    # RECOMMENDATION — best balance of accuracy + speed + size
    # ----------------------------------------------------------------
    # Pick from models whose R² is within 0.005 of the best
    best_r2 = results_df["test_r2"].max()
    close = results_df[results_df["test_r2"] >= best_r2 - 0.005]

    # Among the close ones, pick the fastest
    recommended = close.sort_values("train_time_s").iloc[0]

    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    print(f"Best R² model:   {results_df.iloc[0]['model']} "
          f"(R²={results_df.iloc[0]['test_r2']:.4f}, "
          f"{results_df.iloc[0]['train_time_s']}s)")
    print(f"Recommended:     {recommended['model']} "
          f"(R²={recommended['test_r2']:.4f}, "
          f"{recommended['train_time_s']}s)")
    print(f"Reason: within 0.005 R² of the best, but "
          f"{results_df.iloc[0]['train_time_s'] / max(recommended['train_time_s'], 0.1):.1f}x faster")

    md_path = REPORTS_DIR / "model_comparison.md"
    with open(md_path, "w") as f:
        f.write("# Model Comparison Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"Train rows: {len(train):,} | Val rows: {len(val):,} | Test rows: {len(test):,}\n\n")
        f.write("| Rank | Model | Train R² | Val R² | Test R² | Test MAE | Test MAPE | Overfit Gap | Time (s) |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for i, row in results_df.reset_index(drop=True).iterrows():
            f.write(f"| {i+1} | {row['model']} | {row['train_r2']:.4f} | "
                    f"{row['val_r2']:.4f} | {row['test_r2']:.4f} | "
                    f"{row['test_mae']:.4f} | {row['test_mape']:.2f}% | "
                    f"{row['overfit_gap']:.4f} | {row['train_time_s']} |\n")

        f.write(f"\n## Recommendation: **{recommended['model']}**\n\n")
        f.write(f"- Test R²: {recommended['test_r2']:.4f}\n")
        f.write(f"- Test MAE: {recommended['test_mae']:.4f} GB\n")
        f.write(f"- Overfitting gap: {recommended['overfit_gap']:.4f}\n")
        f.write(f"- Train time: {recommended['train_time_s']}s\n")
        f.write(f"\nChosen because its R² is within 0.005 of the best "
                f"({results_df.iloc[0]['model']}), but it trains "
                f"{results_df.iloc[0]['train_time_s'] / max(recommended['train_time_s'], 0.1):.1f}x faster.\n")

    print(f"\nReports saved:")
    print(f"  {REPORTS_DIR / 'model_comparison.csv'}")
    print(f"  {md_path}")


if __name__ == "__main__":
    main()