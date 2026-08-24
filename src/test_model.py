import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)


# ============================================================
# 1. LOAD TRAINED PIPELINE
# ============================================================

pipeline = joblib.load(
    "models/mobile_data_consumption_pipeline.pkl"
)

print("=" * 70)
print("SCENARIO-BASED UNSEEN TEST DATA EVALUATION")
print("=" * 70)


# ============================================================
# 2. LIST OF TEST FILES (baseline + each scenario)
# ============================================================

test_files = {
    "Baseline":                 "data/processed/baseline_5k.parquet",
    "1. Heavy users heavier":   "data/processed/scenario1_heavy_users_heavier.parquet",
    "2. Light users increase":  "data/processed/scenario2_light_users_increase.parquet",
    "3. Streaming increase":    "data/processed/scenario3_streaming_increase.parquet",
    "4. Social decrease":       "data/processed/scenario4_social_decrease.parquet",
    "5. Weekend behavior":      "data/processed/scenario5_weekend_behavior_change.parquet",
    "6. Unlimited plan shift":  "data/processed/scenario6_unlimited_plan_pattern_shift.parquet",
}


# ============================================================
# 3. LOOP: LOAD -> PREDICT -> EVALUATE FOR EACH SCENARIO
# ============================================================

summary_rows = []
all_results = {}  # keep per-scenario prediction detail if you want to inspect later

for label, path in test_files.items():
    print("\n" + "-" * 70)
    print(f"Scenario: {label}")
    print("-" * 70)

    test_data = pd.read_parquet(path)
    print(f"Test dataset shape: {test_data.shape}")

    X_test = test_data.drop(columns=["total_data_gb"])
    y_test = test_data["total_data_gb"]

    print("Making predictions...")
    y_test_pred = pipeline.predict(X_test)
    print("Predictions complete!")

    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    print(f"RMSE: {test_rmse:.4f}")
    print(f"MAE : {test_mae:.4f}")
    print(f"R²  : {test_r2:.4f}")

    summary_rows.append({
        "scenario": label,
        "n_rows": test_data.shape[0],
        "rmse": round(test_rmse, 4),
        "mae": round(test_mae, 4),
        "r2": round(test_r2, 4),
        "mean_actual_gb": round(y_test.mean(), 3),
        "mean_predicted_gb": round(y_test_pred.mean(), 3),
    })

    all_results[label] = pd.DataFrame({
        "Actual": y_test.values,
        "Predicted": y_test_pred
    })


# ============================================================
# 4. SUMMARY TABLE ACROSS ALL SCENARIOS
# ============================================================

summary_df = pd.DataFrame(summary_rows)

print("\n" + "=" * 70)
print("SUMMARY ACROSS ALL SCENARIOS")
print("=" * 70)
print(summary_df.to_string(index=False))

# Flag which scenario hurt the model most (highest RMSE relative to baseline)
baseline_rmse = summary_df.loc[summary_df["scenario"] == "Baseline", "rmse"].values[0]
summary_df["rmse_delta_vs_baseline"] = round(summary_df["rmse"] - baseline_rmse, 4)

print("\nRMSE delta vs baseline (positive = model got worse):")
print(summary_df[["scenario", "rmse_delta_vs_baseline"]].to_string(index=False))

# Save summary for later reference
summary_df.to_csv("reports/scenario_evaluation_summary.csv", index=False)
print("\nSaved summary to reports/scenario_evaluation_summary.csv")


# ============================================================
# 5. SAMPLE PREDICTIONS FOR ONE SCENARIO (optional inspection)
# ============================================================

print("\nSample Predictions (Baseline)")
print("------------------------------")
print(all_results["Baseline"].head(10))