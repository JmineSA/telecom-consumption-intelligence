# training/models/model_insights.py
"""
model_insights.py — Insights and visualizations for the D+1 forecasting model.

Reads the trained pipeline and the time-based test split, produces:
- Feature importance (with the new lag-feature story)
- Actual vs predicted (scatter + residuals)
- Distribution comparison
- Congestion breakdown (the key business insight)
- Drift breakdown (pre/post policy change on day 45)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("viridis")

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
TARGET = "target_next_day_gb"
DRIFT_DAY = 45

print("=" * 70)
print(" MODEL INSIGHTS — D+1 FORECASTER")
print("=" * 70)

# ------------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------------
model_path = project_root / "models" / "mobile_data_consumption_pipeline.pkl"
info_path = project_root / "models" / "model_info.json"

if not model_path.exists():
    print(" Model not found. Train first.")
    sys.exit(1)

model = joblib.load(model_path)
print(" Model loaded")

info = {}
if info_path.exists():
    with open(info_path) as f:
        info = json.load(f)
    print(f" Model type: {info.get('model_type', 'N/A')}")
    print(f" Target:     {info.get('target', 'N/A')}")
    print(f" Horizon:    {info.get('forecast_horizon_days', 'N/A')} day(s)")

# Directories
reports_dir = project_root / "reports"
insights_dir = reports_dir / "insights"
insights_dir.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("FEATURE IMPORTANCE")
print("-" * 60)

regressor = model.named_steps["regressor"]
feature_names = info.get("feature_names", [])

# Try to get feature names from the preprocessor
if not feature_names:
    try:
        pre = model.named_steps["preprocessor"]
        feature_names = list(pre.get_feature_names_out())
    except Exception:
        feature_names = [f"feature_{i}" for i in range(len(getattr(regressor, "feature_importances_", [])))]

try:
    if hasattr(regressor, "feature_importances_"):
        importance = regressor.feature_importances_
        # Align lengths if there's a mismatch
        n = min(len(feature_names), len(importance))
        feature_names = feature_names[:n]
        importance = importance[:n]

        importance_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importance,
        }).sort_values("importance", ascending=False)

        print("\n Top 15 Features:")
        for _, row in importance_df.head(15).iterrows():
            print(f"  {row['feature']:35s}: {row['importance']:.4f}")

        importance_df.to_csv(reports_dir / "feature_importance.csv", index=False)
        print(f"\n Saved: {reports_dir / 'feature_importance.csv'}")

        # Plot
        top = importance_df.head(15)
        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top)))[::-1]
        bars = plt.barh(top["feature"], top["importance"], color=colors)
        for bar in bars:
            w = bar.get_width()
            plt.text(w + 0.002, bar.get_y() + bar.get_height() / 2,
                     f"{w:.3f}", va="center", fontsize=9)
        plt.gca().invert_yaxis()
        plt.xlabel("Importance")
        plt.title("Feature Importance — Next-Day Usage Forecast", fontweight="bold")
        plt.tight_layout()
        plt.savefig(insights_dir / "feature_importance.png", dpi=300, bbox_inches="tight")
        plt.close()
        print(f"  Plot saved: {insights_dir / 'feature_importance.png'}")
    else:
        print(" Regressor has no feature_importances_ (likely HistGradientBoosting).")
        print(" Skipping importance plot — use permutation importance if needed.")
except Exception as e:
    print(f" Error extracting feature importance: {e}")

# ------------------------------------------------------------------
# LOAD TEST SPLIT
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("TEST SET EVALUATION")
print("-" * 60)

test_path = project_root / "data" / "processed" / "test.parquet"
if not test_path.exists():
    print(f" Test file not found: {test_path}")
    print(" Run data preparation first.")
    sys.exit(1)

test_data = pd.read_parquet(test_path)
print(f" Test data: {test_data.shape}")
print(f" Columns ({len(test_data.columns)}): {list(test_data.columns)[:10]}...")

if TARGET not in test_data.columns:
    print(f" Target column '{TARGET}' not found.")
    sys.exit(1)

# ------------------------------------------------------------------
# PREDICT
# ------------------------------------------------------------------
X_test = test_data.drop(columns=[TARGET, "user_id", "date"], errors="ignore")
y_actual = test_data[TARGET].values
y_predicted = model.predict(X_test)

print(f"\n Predictions: {len(y_predicted):,}")
print(f" Actual mean: {y_actual.mean():.4f} GB")
print(f" Pred mean:   {y_predicted.mean():.4f} GB")

residuals = y_actual - y_predicted

rmse = np.sqrt(np.mean(residuals ** 2))
mae = np.mean(np.abs(residuals))
r2 = 1 - np.sum(residuals ** 2) / np.sum((y_actual - y_actual.mean()) ** 2)

print("\n Overall Metrics:")
print(f"  RMSE: {rmse:.4f}")
print(f"  MAE:  {mae:.4f}")
print(f"  R²:   {r2:.4f}")

# ------------------------------------------------------------------
# 1. ACTUAL VS PREDICTED
# ------------------------------------------------------------------
print("\n Generating plots...")

plt.figure(figsize=(10, 8))
plt.scatter(y_actual, y_predicted, alpha=0.3, s=8, c="steelblue")
lims = [min(y_actual.min(), y_predicted.min()),
        max(y_actual.max(), y_predicted.max())]
plt.plot(lims, lims, "r--", linewidth=2, label="Perfect Prediction")
plt.xlabel("Actual Next-Day Usage (GB)")
plt.ylabel("Predicted Next-Day Usage (GB)")
plt.title("Actual vs Predicted — D+1 Forecast", fontweight="bold")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(insights_dir / "actual_vs_predicted.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"  → {insights_dir / 'actual_vs_predicted.png'}")

# ------------------------------------------------------------------
# 2. RESIDUAL ANALYSIS
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].hist(residuals, bins=60, edgecolor="black", alpha=0.7, color="steelblue")
axes[0].axvline(0, color="red", linestyle="--", linewidth=2)
axes[0].set_xlabel("Residual (GB)")
axes[0].set_ylabel("Frequency")
axes[0].set_title("Residual Distribution", fontweight="bold")

axes[1].scatter(y_predicted, residuals, alpha=0.3, s=8, c="steelblue")
axes[1].axhline(0, color="red", linestyle="--", linewidth=2)
axes[1].set_xlabel("Predicted (GB)")
axes[1].set_ylabel("Residual (GB)")
axes[1].set_title("Residuals vs Predicted", fontweight="bold")
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(insights_dir / "residual_analysis.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"  → {insights_dir / 'residual_analysis.png'}")

# ------------------------------------------------------------------
# 3. DISTRIBUTION COMPARISON
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].hist(y_actual, bins=60, alpha=0.7, label="Actual", color="steelblue", edgecolor="black")
axes[0].hist(y_predicted, bins=60, alpha=0.5, label="Predicted", color="orange", edgecolor="black")
axes[0].set_xlabel("Next-Day Usage (GB)")
axes[0].set_ylabel("Frequency")
axes[0].set_title("Actual vs Predicted Distribution", fontweight="bold")
axes[0].legend()

sa, sp = np.sort(y_actual), np.sort(y_predicted)
axes[1].scatter(sa, sp, alpha=0.3, s=5, c="steelblue")
lims = [min(sa.min(), sp.min()), max(sa.max(), sp.max())]
axes[1].plot(lims, lims, "r--", linewidth=2)
axes[1].set_xlabel("Actual Quantiles (GB)")
axes[1].set_ylabel("Predicted Quantiles (GB)")
axes[1].set_title("Q-Q Plot", fontweight="bold")
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(insights_dir / "distribution_comparison.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"  → {insights_dir / 'distribution_comparison.png'}")

# ------------------------------------------------------------------
# 4. CONGESTION BREAKDOWN — THE KILLER INSIGHT
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("CONGESTION INSIGHT")
print("-" * 60)

if "congested" in X_test.columns:
    test_df = test_data.copy()
    test_df["pred"] = y_predicted
    test_df["abs_err"] = np.abs(test_df[TARGET] - test_df["pred"])

    congest_summary = []
    for label, mask in [("Normal", test_df["congested"] == 0),
                        ("Congested", test_df["congested"] == 1)]:
        sub = test_df[mask]
        if len(sub) == 0:
            continue
        row = {
            "condition": label,
            "n": len(sub),
            "avg_actual_gb": sub[TARGET].mean(),
            "avg_pred_gb": sub["pred"].mean(),
            "avg_abs_err": sub["abs_err"].mean(),
            "rmse": np.sqrt(np.mean((sub[TARGET] - sub["pred"]) ** 2)),
            "r2": 1 - np.sum((sub[TARGET] - sub["pred"]) ** 2) /
                  np.sum((sub[TARGET] - sub[TARGET].mean()) ** 2),
        }
        congest_summary.append(row)
        print(f"\n {label} (n={row['n']:,})")
        print(f"   Avg actual:   {row['avg_actual_gb']:.4f} GB")
        print(f"   Avg pred:     {row['avg_pred_gb']:.4f} GB")
        print(f"   Avg |error|:  {row['avg_abs_err']:.4f} GB")
        print(f"   RMSE:         {row['rmse']:.4f}")
        print(f"   R²:           {row['r2']:.4f}")

    if len(congest_summary) == 2:
        normal = congest_summary[0]
        cong = congest_summary[1]
        err_ratio = cong["avg_abs_err"] / normal["avg_abs_err"] if normal["avg_abs_err"] > 0 else float("inf")
        usage_drop = (1 - cong["avg_actual_gb"] / normal["avg_actual_gb"]) * 100 if normal["avg_actual_gb"] > 0 else 0
        print(f"\n KEY INSIGHT:")
        print(f"   Congestion reduces actual usage by {usage_drop:.1f}%")
        print(f"   But increases prediction error {err_ratio:.2f}x")

    pd.DataFrame(congest_summary).to_csv(reports_dir / "congestion_breakdown.csv", index=False)
    print(f"\n Saved: {reports_dir / 'congestion_breakdown.csv'}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    labels = [r["condition"] for r in congest_summary]
    axes[0].bar(labels, [r["avg_actual_gb"] for r in congest_summary], color=["#5c6bc0", "#ef5350"])
    axes[0].set_ylabel("Avg Actual Usage (GB)")
    axes[0].set_title("Usage by Network Condition", fontweight="bold")

    axes[1].bar(labels, [r["avg_abs_err"] for r in congest_summary], color=["#5c6bc0", "#ef5350"])
    axes[1].set_ylabel("Avg Absolute Error (GB)")
    axes[1].set_title("Prediction Error by Condition", fontweight="bold")

    plt.tight_layout()
    plt.savefig(insights_dir / "congestion_breakdown.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → {insights_dir / 'congestion_breakdown.png'}")
else:
    print(" 'congested' column not in test set — skipping.")

# ------------------------------------------------------------------
# 5. DRIFT BREAKDOWN
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("DRIFT INSIGHT (day_index >= 45)")
print("-" * 60)

if "day_index" in X_test.columns:
    test_df = test_data.copy()
    test_df["pred"] = y_predicted

    drift_summary = []
    for label, mask in [("Pre-drift", test_df["day_index"] < DRIFT_DAY),
                        ("Post-drift", test_df["day_index"] >= DRIFT_DAY)]:
        sub = test_df[mask]
        if len(sub) == 0:
            continue
        r2_sub = 1 - np.sum((sub[TARGET] - sub["pred"]) ** 2) / \
                 np.sum((sub[TARGET] - sub[TARGET].mean()) ** 2)
        row = {
            "window": label,
            "n": len(sub),
            "avg_actual_gb": sub[TARGET].mean(),
            "avg_abs_err": np.abs(sub[TARGET] - sub["pred"]).mean(),
            "r2": r2_sub,
        }
        drift_summary.append(row)
        print(f"\n {label} (n={row['n']:,})")
        print(f"   Avg actual:   {row['avg_actual_gb']:.4f} GB")
        print(f"   Avg |error|:  {row['avg_abs_err']:.4f} GB")
        print(f"   R²:           {row['r2']:.4f}")

    pd.DataFrame(drift_summary).to_csv(reports_dir / "drift_breakdown.csv", index=False)
    print(f"\n Saved: {reports_dir / 'drift_breakdown.csv'}")
else:
    print(" 'day_index' column not in test set — skipping.")

# ------------------------------------------------------------------
# SAVE PREDICTIONS
# ------------------------------------------------------------------
preds_df = test_data[["user_id", "date", TARGET]].copy() if "user_id" in test_data.columns else test_data[[TARGET]].copy()
preds_df["predicted"] = y_predicted
preds_df["residual"] = residuals
preds_df["abs_error"] = np.abs(residuals)
preds_df.to_csv(reports_dir / "predictions_with_insights.csv", index=False)
print(f"\n Predictions saved: {reports_dir / 'predictions_with_insights.csv'}")

print(f"\n All insights saved to: {insights_dir}")
print("\n Insights complete!")