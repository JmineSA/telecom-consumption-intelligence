# src/models/compare_models.py
"""
Compare multiple regressors on the same train/val/test split.

Purpose: identify the best model for the forecasting task.
Output: reports/model_comparison.csv + reports/model_comparison.md
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from src.pipelines.preprocessing_pipeline import build_pipeline

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
# MODEL REGISTRY (tuned for speed on 580K rows)
# ------------------------------------------------------------------
def get_candidates():
    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=42),

        # Faster RF — cap depth and use subsampling
        "RandomForest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=20,
            max_samples=0.5,          # subsample rows per tree
            max_features=0.7,         # subsample features per split
            n_jobs=-1,
            random_state=42,
        ),

        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_leaf=20,
            random_state=42,
        ),

        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=400,
            max_depth=6,
            learning_rate=0.05,
            min_samples_leaf=20,
            l2_regularization=1.0,
            random_state=42,
        ),
    }

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
            print(f"  SKIPPED (user interrupted)")
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

        best = results_df.iloc[0]
        f.write(f"\n## Winner: **{best['model']}**\n\n")
        f.write(f"- Test R²: {best['test_r2']:.4f}\n")
        f.write(f"- Test MAE: {best['test_mae']:.4f} GB\n")
        f.write(f"- Overfitting gap: {best['overfit_gap']:.4f}\n")

    print(f"\nReports saved:")
    print(f"  {REPORTS_DIR / 'model_comparison.csv'}")
    print(f"  {md_path}")
    print(f"\n→ Winner: {results_df.iloc[0]['model']}")


if __name__ == "__main__":
    main()