# src/evaluation/evaluate_model.py
"""
Evaluate the trained mobile data consumption model on the held-out test set.

Responsibility: EVALUATE ONLY.
- Loads saved model + test split
- Computes test metrics
- Breaks down error by congestion
- Saves evaluation results (does NOT retrain)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import joblib
import json
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


TARGET = "target_next_day_gb"
PROCESSED = project_root / "data" / "processed"
MODEL_DIR = project_root / "models"
REPORTS_DIR = project_root / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


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
    print("EVALUATION — MOBILE DATA CONSUMPTION FORECASTER (D+1)")
    print("=" * 70)

    # --- Load model
    model_path = MODEL_DIR / "mobile_data_consumption_pipeline.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}\n"
            f"Run src/models/mobile_data_consumption_model.py first."
        )
    pipeline = joblib.load(model_path)
    print(f"\nLoaded model: {model_path}")

    # --- Load test set
    test = pd.read_parquet(PROCESSED / "test.parquet")
    print(f"Test shape: {test.shape}")

    drop_cols = [TARGET, "user_id", "date"]
    X_test = test.drop(columns=[c for c in drop_cols if c in test.columns])
    y_test = test[TARGET]

    # --- Predict
    y_pred = pipeline.predict(X_test)

    # --- Overall metrics
    overall = compute_metrics(y_test, y_pred)

    print("\n" + "=" * 70)
    print("TEST METRICS")
    print("=" * 70)
    print(f"  RMSE: {overall['rmse']:.4f}")
    print(f"  MAE : {overall['mae']:.4f}")
    print(f"  R²  : {overall['r2']:.4f}")
    print(f"  MAPE: {overall['mape']:.2f}%")

    # --- Congestion breakdown
    print("\n" + "=" * 70)
    print("CONGESTION BREAKDOWN")
    print("=" * 70)

    breakdown = {}
    if "congested" in X_test.columns:
        test_df = test.copy()
        test_df["pred"] = y_pred
        test_df["error"] = np.abs(test_df[TARGET] - test_df["pred"])

        for label, mask in [("Normal", test_df["congested"] == 0),
                            ("Congested", test_df["congested"] == 1)]:
            subset = test_df[mask]
            if len(subset) == 0:
                continue
            m = compute_metrics(subset[TARGET], subset["pred"])
            m["n_samples"] = int(len(subset))
            m["avg_usage_gb"] = float(subset[TARGET].mean())
            breakdown[label.lower()] = m

            print(f"\n{label} (n={len(subset):,})")
            print(f"  Avg usage   : {m['avg_usage_gb']:.4f} GB")
            print(f"  Avg |error| : {m['mae']:.4f} GB")
            print(f"  RMSE        : {m['rmse']:.4f}")
            print(f"  R²          : {m['r2']:.4f}")

    # --- Error by drift window (before/after day 45)
    if "day_index" in X_test.columns:
        print("\n" + "=" * 70)
        print("DRIFT BREAKDOWN (day_index >= 45 vs < 45)")
        print("=" * 70)

        test_df = test.copy()
        test_df["pred"] = y_pred

        for label, mask in [("Pre-drift", test_df["day_index"] < 45),
                            ("Post-drift", test_df["day_index"] >= 45)]:
            subset = test_df[mask]
            if len(subset) == 0:
                continue
            m = compute_metrics(subset[TARGET], subset["pred"])
            print(f"\n{label} (n={len(subset):,})")
            print(f"  R²  : {m['r2']:.4f}")
            print(f"  MAE : {m['mae']:.4f}")

    # --- Save results
    results = {
        "evaluated_at": datetime.now().isoformat(),
        "model_path": str(model_path),
        "test_shape": {"rows": int(len(test)), "cols": int(test.shape[1])},
        "overall": overall,
        "by_congestion": breakdown,
    }
    out_file = REPORTS_DIR / "evaluation_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {out_file}")


if __name__ == "__main__":
    main()