
"""
PHASE 6.

Train the mobile data consumption forecasting model.

Responsibility: TRAIN ONLY.
- Loads train + val splits
- Fits the pipeline
- Saves the model and training metadata
- Does NOT evaluate on test (that's evaluate_model.py)
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
from training.pipelines.training_pipeline import build_model_pipeline


TARGET = "target_next_day_gb"
PROCESSED = project_root / "data" / "processed"
MODEL_DIR = project_root / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_train_val():
    train = pd.read_parquet(PROCESSED / "train.parquet")
    val = pd.read_parquet(PROCESSED / "val.parquet")
    return train, val


def quick_metrics(y_true, y_pred):
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def extract_feature_names(pipeline) -> list:
    """
    Extract the actual feature names the regressor sees after preprocessing.

    The preprocessor is a Pipeline containing:
        drop_cols       (custom DropColumns)
        cyclical_dow    (custom CyclicalDayOfWeek)
        encoding        (sklearn ColumnTransformer)

    Custom transformers don't implement get_feature_names_out(), so calling
    it on the outer Pipeline fails. We reach into the ColumnTransformer
    step directly — it always implements get_feature_names_out().
    """
    pre = pipeline.named_steps["preprocessor"]

    # Case 1: preprocessor is a Pipeline with a ColumnTransformer named "encoding"
    if hasattr(pre, "named_steps") and "encoding" in pre.named_steps:
        ct = pre.named_steps["encoding"]
        return list(ct.get_feature_names_out())

    # Case 2: preprocessor itself is a ColumnTransformer
    if hasattr(pre, "get_feature_names_out"):
        return list(pre.get_feature_names_out())

    # Case 3: fallback — count only
    n = pipeline.named_steps["regressor"].n_features_in_
    return [f"f{i}" for i in range(n)]


def main():
    print("=" * 70)
    print("TRAINING — MOBILE DATA CONSUMPTION FORECASTER (D+1)")
    print("=" * 70)

    train, val = load_train_val()
    print(f"\nTrain shape: {train.shape}")
    print(f"Val shape:   {val.shape}")

    drop_cols = [TARGET, "user_id", "date"]
    X_train = train.drop(columns=[c for c in drop_cols if c in train.columns])
    y_train = train[TARGET]

    X_val = val.drop(columns=[c for c in drop_cols if c in val.columns])
    y_val = val[TARGET]

    print(f"\nRaw input columns: {X_train.shape[1]}")
    print(f"Target mean (train): {y_train.mean():.4f} GB")

    print("\nBuilding model pipeline...")
    pipeline = build_model_pipeline()

    print("Training model...")
    pipeline.fit(X_train, y_train)
    print("Training complete.")

    # Quick sanity check on train and val only
    y_train_pred = pipeline.predict(X_train)
    y_val_pred = pipeline.predict(X_val)

    train_metrics = quick_metrics(y_train, y_train_pred)
    val_metrics = quick_metrics(y_val, y_val_pred)

    print("\n" + "-" * 40)
    print("TRAIN METRICS (sanity check)")
    print("-" * 40)
    print(f"  RMSE: {train_metrics['rmse']:.4f}")
    print(f"  MAE : {train_metrics['mae']:.4f}")
    print(f"  R²  : {train_metrics['r2']:.4f}")

    print("\n" + "-" * 40)
    print("VAL METRICS (model selection)")
    print("-" * 40)
    print(f"  RMSE: {val_metrics['rmse']:.4f}")
    print(f"  MAE : {val_metrics['mae']:.4f}")
    print(f"  R²  : {val_metrics['r2']:.4f}")

    print(f"\nOverfitting gap (train R² − val R²): "
          f"{train_metrics['r2'] - val_metrics['r2']:.4f}")

    # ----- Save model -----
    model_path = MODEL_DIR / "mobile_data_consumption_pipeline.pkl"
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved: {model_path}")

    # ----- Extract real feature names -----
    try:
        transformed_features = extract_feature_names(pipeline)
        print(f"  ✓ Extracted {len(transformed_features)} feature names")
    except Exception as e:
        print(f"  ⚠ Could not extract feature names: {e}")
        n = pipeline.named_steps["regressor"].n_features_in_
        transformed_features = [f"f{i}" for i in range(n)]

    # ----- Save training metadata -----
    info_path = MODEL_DIR / "model_info.json"

    model_info = {
        "model_path": str(model_path),
        "model_type": type(pipeline.named_steps["regressor"]).__name__,
        "target": TARGET,
        "forecast_horizon_days": 1,
        "trained_at": datetime.now().isoformat(),

        # Effective features the regressor sees
        "n_features": int(pipeline.named_steps["regressor"].n_features_in_),
        "feature_names": transformed_features,

        # Raw input schema (what the pipeline expects as input)
        "n_input_columns": int(X_train.shape[1]),
        "input_columns": X_train.columns.tolist(),

        "n_train_samples": int(len(X_train)),
        "n_val_samples": int(len(X_val)),
        "train_metrics": train_metrics,
        "val_metrics": val_metrics,
        "overfitting_gap": train_metrics["r2"] - val_metrics["r2"],
    }

    with open(info_path, "w") as f:
        json.dump(model_info, f, indent=2)
    print(f"Training metadata saved: {info_path}")
    print(f"  n_features (effective): {model_info['n_features']}")
    print(f"  n_input_columns (raw):  {model_info['n_input_columns']}")
    print("\n→ Run evaluate_model.py next for test-set evaluation.")


if __name__ == "__main__":
    main()