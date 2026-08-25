import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

from model_trainning_pipeline import build_model_pipeline


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_parquet(
    "data/processed/train_data.parquet"
)

print("=" * 70)
print("MOBILE DATA CONSUMPTION MODEL")
print("=" * 70)

print(f"\nDataset shape: {df.shape}")


# ============================================================
# 2. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(columns=["total_data_gb"])
y = df["total_data_gb"]

print(f"Features: {X.shape}")
print(f"Target: {y.shape}")


# ============================================================
# 3. TRAIN / VALIDATION SPLIT
# ============================================================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTrain/Validation Split")
print("----------------------")
print(f"Training samples:   {len(X_train)}")
print(f"Validation samples: {len(X_val)}")


# ============================================================
# 4. BUILD COMPLETE MODEL PIPELINE
# ============================================================

print("\nBuilding model pipeline...")

pipeline = build_model_pipeline()

print("Model pipeline created successfully.")


# ============================================================
# 5. TRAIN
# ============================================================

print("\nTraining Gradient Boosting model...")

pipeline.fit(
    X_train,
    y_train
)

print("Training complete!")


# ============================================================
# 6. PREDICTIONS
# ============================================================

y_train_pred = pipeline.predict(X_train)
y_val_pred = pipeline.predict(X_val)


# ============================================================
# 7. TRAINING METRICS
# ============================================================

train_rmse = np.sqrt(
    mean_squared_error(
        y_train,
        y_train_pred
    )
)

train_mae = mean_absolute_error(
    y_train,
    y_train_pred
)

train_r2 = r2_score(
    y_train,
    y_train_pred
)


# ============================================================
# 8. VALIDATION METRICS
# ============================================================

val_rmse = np.sqrt(
    mean_squared_error(
        y_val,
        y_val_pred
    )
)

val_mae = mean_absolute_error(
    y_val,
    y_val_pred
)

val_r2 = r2_score(
    y_val,
    y_val_pred
)


# ============================================================
# 9. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("FINAL MODEL PERFORMANCE")
print("=" * 70)

print("\nTraining Performance")
print("--------------------")
print(f"RMSE: {train_rmse:.4f}")
print(f"MAE : {train_mae:.4f}")
print(f"R²  : {train_r2:.4f}")

print("\nValidation Performance")
print("----------------------")
print(f"RMSE: {val_rmse:.4f}")
print(f"MAE : {val_mae:.4f}")
print(f"R²  : {val_r2:.4f}")


# ============================================================
# 10. OVERFITTING ANALYSIS
# ============================================================

overfitting_gap = train_r2 - val_r2

print("\nOverfitting Analysis")
print("--------------------")
print(f"R² Gap: {overfitting_gap:.4f}")


# ============================================================
# 11. SAVE COMPLETE PIPELINE
# ============================================================

from pathlib import Path
import joblib
import json
from datetime import datetime

model_dir = Path("models")
model_dir.mkdir(parents=True, exist_ok=True)

# Define paths
model_path = model_dir / "mobile_data_consumption_pipeline.pkl"
info_path = model_dir / "model_info.json"

# Save the model
joblib.dump(pipeline, model_path)

# Get feature information
if hasattr(pipeline, 'feature_names_in_'):
    feature_names = pipeline.feature_names_in_.tolist()
elif hasattr(pipeline, 'get_feature_names_out'):
    feature_names = pipeline.get_feature_names_out().tolist()
else:
    feature_names = []  # Replace with actual feature names

# Collect comprehensive metadata
model_info = {
    'model_path': str(model_path),
    'feature_names': feature_names,
    'n_features': len(feature_names),
    'model_type': type(pipeline).__name__,
    'saved_date': datetime.now().isoformat(),
    'n_samples': None,  # Add if you know
    'feature_dtypes': None,  # Add if available
    'description': 'Mobile data consumption prediction model'
}

with open(info_path, 'w') as f:
    json.dump(model_info, f, indent=2)

print(f"✓ Model saved to: {model_path}")
print(f"✓ Model info saved to: {info_path}")
print(f"✓ Features ({len(feature_names)}): {feature_names}")
