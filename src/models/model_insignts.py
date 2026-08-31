import sys
from pathlib import Path

# Add project root to Python path - FIXED: go up 3 levels
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import joblib
import json

print("=" * 70)
print(" MODEL INSIGHTS")
print("=" * 70)

# Load model
model_path = project_root / "models" / "mobile_data_consumption_pipeline.pkl"
if not model_path.exists():
    print(" Model not found. Train first: python main.py --train")
    exit(1)

model = joblib.load(model_path)
print(f" Model loaded")

# Load model info
info_path = project_root / "models" / "model_info.json"
if info_path.exists():
    with open(info_path, 'r') as f:
        info = json.load(f)
    print(f" Model info loaded:")
    print(f"  - Features: {info.get('n_features', 'N/A')}")
    print(f"  - Model: {info.get('model_type', 'N/A')}")

# Get feature importance
try:
    regressor = model.named_steps['regressor']
    feature_names = info.get('feature_names', [f'feature_{i}' for i in range(len(regressor.feature_importances_))])
    importance = regressor.feature_importances_
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print("\n Top 10 Most Important Features:")
    print("-" * 50)
    for i, row in importance_df.head(10).iterrows():
        print(f"  {row['feature']:30s}: {row['importance']:.4f}")
    
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    importance_df.to_csv(reports_dir / "feature_importance.csv", index=False)
    print(f"\n Saved to: {reports_dir / 'feature_importance.csv'}")
    
except Exception as e:
    print(f" Error: {e}")

print("\n Insights complete!")