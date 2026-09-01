"""
model_insights.py - Generate insights and visualizations from the trained model
"""

import sys
from pathlib import Path

# Add project root to Python path - FIXED: go up 3 levels
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

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("viridis")

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

# Create reports directory
reports_dir = project_root / "reports"
insights_dir = reports_dir / "insights"
insights_dir.mkdir(parents=True, exist_ok=True)

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
    
    # Save feature importance CSV
    importance_df.to_csv(reports_dir / "feature_importance.csv", index=False)
    print(f"\n Saved to: {reports_dir / 'feature_importance.csv'}")
    
    # Create feature importance visualization
    print("\n Generating feature importance plot...")
    plt.figure(figsize=(12, 8))
    
    # Create horizontal bar chart
    top_features = importance_df.head(15)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))[::-1]
    
    bars = plt.barh(top_features['feature'], top_features['importance'], color=colors)
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', va='center', fontsize=10)
    
    plt.xlabel('Importance', fontsize=12)
    plt.title('Feature Importance for Mobile Data Consumption Prediction', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    plot_path = insights_dir / "feature_importance.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Feature importance plot saved to: {plot_path}")
    
except Exception as e:
    print(f" Error extracting feature importance: {e}")

# Load test data and generate prediction visualizations
try:
    # Check for parquet file first, then CSV
    test_path_parquet = project_root / "data" / "processed" / "test_data.parquet"
    test_path_csv = project_root / "data" / "processed" / "test_data.csv"
    
    test_data = None
    if test_path_parquet.exists():
        test_data = pd.read_parquet(test_path_parquet)
        print(f"\n Test data loaded from parquet: {test_data.shape}")
        print(f"  Columns: {list(test_data.columns)}")
    elif test_path_csv.exists():
        test_data = pd.read_csv(test_path_csv)
        print(f"\n Test data loaded from CSV: {test_data.shape}")
        print(f"  Columns: {list(test_data.columns)}")
    else:
        print(f"\n Test data not found. Skipping prediction visualizations.")
    
    if test_data is not None:
        # Check for target column - try 'total_data_gb' first, then 'target'
        target_col = None
        if 'total_data_gb' in test_data.columns:
            target_col = 'total_data_gb'
            print(f"  Target column found: 'total_data_gb'")
        elif 'target' in test_data.columns:
            target_col = 'target'
            print(f"  Target column found: 'target'")
        else:
            print(f"  No target column found. Available columns: {list(test_data.columns)}")
        
        if target_col is not None:
            # Prepare features and target
            X_test = test_data.drop(target_col, axis=1)
            y_actual = test_data[target_col].values
            y_predicted = model.predict(X_test)
            
            print(" Generating prediction visualizations...")
            
            # 1. Actual vs Predicted Scatter Plot
            plt.figure(figsize=(10, 8))
            plt.scatter(y_actual, y_predicted, alpha=0.5, s=20, c='steelblue')
            
            # Perfect prediction line
            min_val = min(y_actual.min(), y_predicted.min())
            max_val = max(y_actual.max(), y_predicted.max())
            plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
            
            plt.xlabel('Actual Data Consumption (GB)', fontsize=12)
            plt.ylabel('Predicted Data Consumption (GB)', fontsize=12)
            plt.title('Actual vs Predicted Data Consumption', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plot_path = insights_dir / "actual_vs_predicted.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  Actual vs Predicted plot saved to: {plot_path}")
            
            # 2. Residual Analysis
            residuals = y_actual - y_predicted
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            
            # Residual distribution
            axes[0].hist(residuals, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
            axes[0].axvline(x=0, color='red', linestyle='--', linewidth=2)
            axes[0].set_xlabel('Residual (GB)', fontsize=12)
            axes[0].set_ylabel('Frequency', fontsize=12)
            axes[0].set_title('Residual Distribution', fontsize=12, fontweight='bold')
            
            # Residuals vs Predicted
            axes[1].scatter(y_predicted, residuals, alpha=0.5, s=20, c='steelblue')
            axes[1].axhline(y=0, color='red', linestyle='--', linewidth=2)
            axes[1].set_xlabel('Predicted Value (GB)', fontsize=12)
            axes[1].set_ylabel('Residual (GB)', fontsize=12)
            axes[1].set_title('Residuals vs Predicted Values', fontsize=12, fontweight='bold')
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plot_path = insights_dir / "residual_analysis.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  Residual analysis plot saved to: {plot_path}")
            
            # 3. Error Statistics
            print("\n Prediction Error Statistics:")
            print("-" * 50)
            print(f"  Samples: {len(y_actual)}")
            print(f"  RMSE: {np.sqrt(np.mean(residuals**2)):.4f}")
            print(f"  MAE:  {np.mean(np.abs(residuals)):.4f}")
            print(f"  R²:   {np.corrcoef(y_actual, y_predicted)[0, 1]**2:.4f}")
            print(f"  Mean Error: {np.mean(residuals):.4f}")
            print(f"  Std Error:  {np.std(residuals):.4f}")
            print(f"  Min Error:  {np.min(residuals):.4f}")
            print(f"  Max Error:  {np.max(residuals):.4f}")
            
            # Save predictions
            predictions_df = pd.DataFrame({
                'actual': y_actual,
                'predicted': y_predicted,
                'residual': residuals
            })
            predictions_df.to_csv(reports_dir / "predictions_with_insights.csv", index=False)
            print(f"\n Predictions saved to: {reports_dir / 'predictions_with_insights.csv'}")
            
            # 4. Distribution comparison
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            
            # Actual distribution
            axes[0].hist(y_actual, bins=50, edgecolor='black', alpha=0.7, color='steelblue', label='Actual')
            axes[0].hist(y_predicted, bins=50, edgecolor='black', alpha=0.5, color='orange', label='Predicted')
            axes[0].set_xlabel('Data Consumption (GB)', fontsize=12)
            axes[0].set_ylabel('Frequency', fontsize=12)
            axes[0].set_title('Actual vs Predicted Distribution', fontsize=12, fontweight='bold')
            axes[0].legend()
            
            # Q-Q plot style - sorted values
            sorted_actual = np.sort(y_actual)
            sorted_predicted = np.sort(y_predicted)
            axes[1].scatter(sorted_actual, sorted_predicted, alpha=0.5, s=10, c='steelblue')
            min_val = min(sorted_actual.min(), sorted_predicted.min())
            max_val = max(sorted_actual.max(), sorted_predicted.max())
            axes[1].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
            axes[1].set_xlabel('Actual Quantiles (GB)', fontsize=12)
            axes[1].set_ylabel('Predicted Quantiles (GB)', fontsize=12)
            axes[1].set_title('Quantile-Quantile Plot', fontsize=12, fontweight='bold')
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plot_path = insights_dir / "distribution_comparison.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  Distribution comparison plot saved to: {plot_path}")
            
        else:
            print(" No target column found. Available columns:")
            print(f"  {list(test_data.columns)}")
            print("  Expected column name: 'total_data_gb'")
        
except Exception as e:
    print(f" Error generating prediction visualizations: {e}")
    import traceback
    traceback.print_exc()

print(f"\n All insights saved to: {insights_dir}")
print("\n Insights complete!")