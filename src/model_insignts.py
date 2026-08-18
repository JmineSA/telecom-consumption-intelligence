import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error


# ============================================================
# 1. LOAD MODEL
# ============================================================

pipeline = joblib.load(
    "models/mobile_data_consumption_pipeline.pkl"
)


# ============================================================
# 2. LOAD TEST DATA
# ============================================================

test_data = pd.read_parquet(
    "data/processed/test_data.parquet"
)

X_test = test_data.drop(
    columns=["total_data_gb"]
)

y_test = test_data["total_data_gb"]


# ============================================================
# 3. PREDICTIONS
# ============================================================

y_pred = pipeline.predict(X_test)


# ============================================================
# 4. ACTUAL VS PREDICTED
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    y_pred,
    alpha=0.5
)

# Perfect prediction line
min_value = min(y_test.min(), y_pred.min())
max_value = max(y_test.max(), y_pred.max())

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.xlabel("Actual Total Data Usage (GB)")
plt.ylabel("Predicted Total Data Usage (GB)")
plt.title("Actual vs Predicted Data Usage")

plt.tight_layout()

plt.savefig(
    "visuals/actual_vs_predicted.png",
    dpi=300
)

plt.show()


# ============================================================
# 5. RESIDUALS
# ============================================================

residuals = y_test - y_pred

plt.figure(figsize=(8, 6))

plt.scatter(
    y_pred,
    residuals,
    alpha=0.5
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.xlabel("Predicted Total Data Usage (GB)")
plt.ylabel("Residual")
plt.title("Residual Plot")

plt.tight_layout()

plt.savefig(
    "visuals/residual_plot.png",
    dpi=300
)

plt.show()


# ============================================================
# 6. RESIDUAL DISTRIBUTION
# ============================================================

plt.figure(figsize=(8, 6))

plt.hist(
    residuals,
    bins=30
)

plt.xlabel("Residual")
plt.ylabel("Frequency")
plt.title("Distribution of Prediction Errors")

plt.tight_layout()

plt.savefig(
    "visuals/residual_distribution.png",
    dpi=300
)

plt.show()