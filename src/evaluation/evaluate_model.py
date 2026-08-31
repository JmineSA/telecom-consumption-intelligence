import sys
from pathlib import Path

# Add project root to Python path - FIXED: go up 3 levels
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
from datetime import datetime

print("=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

# ============================================================
# 1. LOAD MODEL
# ============================================================

model_path = project_root / "models" / "mobile_data_consumption_pipeline.pkl"
if not model_path.exists():
    print(f" Model not found at: {model_path}")
    print("   Please train first: python main.py --train")
    exit(1)

model = joblib.load(model_path)
print(f" Model loaded from: {model_path}")

# Load model info if available
info_path = project_root / "models" / "model_info.json"
if info_path.exists():
    with open(info_path, 'r') as f:
        info = json.load(f)
    print(f" Model info loaded: {info.get('n_features', 'N/A')} features")
    print(f"   Model type: {info.get('model_type', 'N/A')}")
    print(f"   Saved: {info.get('saved_date', 'N/A')}")

# ============================================================
# 2. LOAD TEST DATA
# ============================================================

test_data_path = project_root / "data" / "processed" / "test_data.parquet"
if test_data_path.exists():
    df = pd.read_parquet(test_data_path)
    print(f" Test data loaded: {df.shape}")
    
    X_test = df.drop(columns=["total_data_gb"])
    y_test = df["total_data_gb"]
    
    # ============================================================
    # 3. MAKE PREDICTIONS
    # ============================================================
    
    print("\nMaking predictions...")
    predictions = model.predict(X_test)
    print(" Predictions complete!")
    
    # ============================================================
    # 4. CALCULATE METRICS
    # ============================================================
    
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    # Error analysis
    errors = predictions - y_test
    mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
    
    print("\n" + "=" * 70)
    print(" TEST PERFORMANCE METRICS")
    print("=" * 70)
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R²:   {r2:.4f}")
    print(f"  MAPE: {mape:.2f}%")
    
    print("\n ERROR STATISTICS:")
    print(f"  Mean Error: {errors.mean():.4f}")
    print(f"  Std Error:  {errors.std():.4f}")
    print(f"  Min Error:  {errors.min():.4f}")
    print(f"  Max Error:  {errors.max():.4f}")
    
    print("\n DATA SUMMARY:")
    print(f"  Actual Mean: {y_test.mean():.4f}")
    print(f"  Predicted Mean: {predictions.mean():.4f}")
    print(f"  Actual Std: {y_test.std():.4f}")
    print(f"  Predicted Std: {predictions.std():.4f}")
    
    # ============================================================
    # 5. SAVE RESULTS
    # ============================================================
    
    results = {
        'model_path': str(model_path),
        'test_data_path': str(test_data_path),
        'evaluation_date': datetime.now().isoformat(),
        'n_samples': len(y_test),
        'metrics': {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'mape': float(mape)
        },
        'error_stats': {
            'mean_error': float(errors.mean()),
            'std_error': float(errors.std()),
            'min_error': float(errors.min()),
            'max_error': float(errors.max())
        },
        'data_stats': {
            'actual_mean': float(y_test.mean()),
            'predicted_mean': float(predictions.mean()),
            'actual_std': float(y_test.std()),
            'predicted_std': float(predictions.std())
        }
    }
    
    reports_dir = project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    results_path = reports_dir / "evaluation_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n Evaluation results saved to: {results_path}")
    
    # Save predictions for analysis
    predictions_df = pd.DataFrame({
        'actual': y_test.values,
        'predicted': predictions,
        'error': errors.values
    })
    predictions_path = reports_dir / "predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)
    print(f" Predictions saved to: {predictions_path}")
    
else:
    print(f" Test data not found at: {test_data_path}")
    print("   Using training data for evaluation...")
    
    train_data_path = project_root / "data" / "processed" / "train_data.parquet"
    if train_data_path.exists():
        df = pd.read_parquet(train_data_path)
        print(f" Training data loaded: {df.shape}")
        
        X = df.drop(columns=["total_data_gb"])
        y = df["total_data_gb"]
        
        # Use a subset for quick evaluation
        X_sample = X.head(1000)
        y_sample = y.head(1000)
        predictions = model.predict(X_sample)
        
        rmse = np.sqrt(mean_squared_error(y_sample, predictions))
        mae = mean_absolute_error(y_sample, predictions)
        r2 = r2_score(y_sample, predictions)
        
        print("\n TRAINING DATA PERFORMANCE (sample of 1000 rows):")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE:  {mae:.4f}")
        print(f"  R²:   {r2:.4f}")
    else:
        print(f" No data found for evaluation!")

print("\n" + "=" * 70)
print(" Evaluation complete!")
print("=" * 70)