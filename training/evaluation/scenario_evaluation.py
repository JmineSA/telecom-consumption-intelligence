
"""
Scenario-based stress testing.

Loads the trained model and evaluates it on multiple deliberately-altered
datasets (baseline + scenario mutations) to measure robustness.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


TARGET = "target_next_day_gb"
PROCESSED = project_root / "data" / "processed"
MODEL_DIR = project_root / "models"
REPORTS_DIR = project_root / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------------
# Scenario file map — update if you rename or add files
# ------------------------------------------------------------------
TEST_FILES = {
    "Baseline":             "baseline_5k.parquet",
    "Heavy users heavier":  "scenario1_heavy_users_heavier.parquet",
    "Light users increase": "scenario2_light_users_increase.parquet",
    "Streaming increase":   "scenario3_streaming_increase.parquet",
    "Social decrease":      "scenario4_social_decrease.parquet",
    "Weekend behaviour":    "scenario5_weekend_behavior_change.parquet",
    "Unlimited shift":      "scenario6_unlimited_plan_pattern_shift.parquet",
}


def compute_metrics(y_true, y_pred):
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def main():
    print("=" * 70)
    print("SCENARIO-BASED STRESS TESTING")
    print("=" * 70)

    model_path = MODEL_DIR / "mobile_data_consumption_pipeline.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}\n"
            f"Run src/models/mobile_data_consumption_model.py first."
        )
    pipeline = joblib.load(model_path)
    print(f"Loaded model: {model_path}\n")

    rows = []
    for label, filename in TEST_FILES.items():
        file_path = PROCESSED / filename
        if not file_path.exists():
            print(f"[SKIP] {label}: {file_path} not found")
            continue

        data = pd.read_parquet(file_path)

        if TARGET not in data.columns:
            print(f"[SKIP] {label}: missing target column '{TARGET}'")
            continue

        X = data.drop(columns=[TARGET, "user_id", "date"], errors="ignore")
        y = data[TARGET]

        y_pred = pipeline.predict(X)
        m = compute_metrics(y, y_pred)

        rows.append({
            "scenario": label,
            "n_rows": len(data),
            "rmse": round(m["rmse"], 4),
            "mae": round(m["mae"], 4),
            "r2": round(m["r2"], 4),
            "mean_actual_gb": round(float(y.mean()), 3),
            "mean_predicted_gb": round(float(y_pred.mean()), 3),
        })

    if not rows:
        print("\nNo scenario files found. Skipping scenario evaluation.")
        return

    summary = pd.DataFrame(rows)

    print("\n" + "=" * 70)
    print("SUMMARY ACROSS ALL SCENARIOS")
    print("=" * 70)
    print(summary.to_string(index=False))

    baseline_rmse = summary.loc[summary["scenario"] == "Baseline", "rmse"]
    if not baseline_rmse.empty:
        base = baseline_rmse.values[0]
        summary["rmse_delta_vs_baseline"] = (summary["rmse"] - base).round(4)
        print("\nRMSE delta vs baseline (positive = model got worse):")
        print(summary[["scenario", "rmse_delta_vs_baseline"]].to_string(index=False))

    out = REPORTS_DIR / "scenario_evaluation_summary.csv"
    summary.to_csv(out, index=False)
    print(f"\nSaved summary: {out}")


if __name__ == "__main__":
    main()