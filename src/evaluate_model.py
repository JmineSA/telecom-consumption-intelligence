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
print("UNSEEN TEST DATA EVALUATION")
print("=" * 70)


# ============================================================
# 2. LOAD UNSEEN TEST DATA
# ============================================================

test_data = pd.read_parquet(
    "data/processed/test_data.parquet"
)

print(f"\nTest dataset shape: {test_data.shape}")


# ============================================================
# 3. SEPARATE FEATURES AND TARGET
# ============================================================

X_test = test_data.drop(
    columns=["total_data_gb"]
)

y_test = test_data["total_data_gb"]


# ============================================================
# 4. PREDICT
# ============================================================

print("\nMaking predictions...")

y_test_pred = pipeline.predict(X_test)

print("Predictions complete!")


# ============================================================
# 5. EVALUATE
# ============================================================

test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_test_pred
    )
)

test_mae = mean_absolute_error(
    y_test,
    y_test_pred
)

test_r2 = r2_score(
    y_test,
    y_test_pred
)


# ============================================================
# 6. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("FINAL UNSEEN TEST PERFORMANCE")
print("=" * 70)

print(f"\nRMSE: {test_rmse:.4f}")
print(f"MAE : {test_mae:.4f}")
print(f"R²  : {test_r2:.4f}")


# ============================================================
# 7. SAMPLE PREDICTIONS
# ============================================================

results = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_test_pred
})

print("\nSample Predictions")
print("------------------")

print(
    results.head(10)
)