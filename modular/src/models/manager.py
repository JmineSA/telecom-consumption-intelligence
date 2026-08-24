"""
Model lifecycle management - Updated to work with your existing files
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from ..config import CONFIG
from ..constants import EXPECTED_FEATURES, PRICING_BENCHMARKS
from ..data.processor import DataProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manage model lifecycle: training, loading, prediction"""
    
    def __init__(self):
        self.config = CONFIG.model
        self.processor = DataProcessor()
        
        # Try multiple paths to find your existing model (parent directory)
        self.model_paths = [
            '../models/gradient_boosting_final.pkl',           # Your existing model
            '../models/model_performance.json',                # Your existing metrics
            '../../models/gradient_boosting_final.pkl',        # Alternative path
            'models/gradient_boosting_final.pkl',              # Fallback
        ]
        
        self.perf_paths = [
            '../models/model_performance.json',
            '../../models/model_performance.json',
            'models/model_performance.json',
        ]
        
        self.logger = logger
    
    def _find_existing_model(self) -> Tuple[Optional[str], Optional[str]]:
        """Find existing model and performance files"""
        for model_path in self.model_paths:
            if os.path.exists(model_path):
                # Find corresponding performance file
                for perf_path in self.perf_paths:
                    if os.path.exists(perf_path):
                        self.logger.info(f"Found existing model at: {model_path}")
                        return model_path, perf_path
        return None, None
    
    def load(self, train_df: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
        """Load existing model or train if not available"""
        try:
            # Try to find existing model
            model_path, perf_path = self._find_existing_model()
            
            if model_path is not None and perf_path is not None:
                model = joblib.load(model_path)
                
                with open(perf_path, 'r') as f:
                    performance = json.load(f)
                
                self.logger.info(f"Loaded existing model from: {model_path}")
                
                return {
                    'model': model,
                    'performance': performance,
                    'is_real': True,
                    'model_path': model_path,
                    'perf_path': perf_path
                }
            
            # If no model found, try to train
            self.logger.warning("No existing model found. Trying to train...")
            if train_df is not None:
                model, performance = self.train(train_df)
                return {
                    'model': model, 
                    'performance': performance, 
                    'is_real': True,
                    'model_path': self.model_paths[0],
                    'perf_path': self.perf_paths[0]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return None
    
    def train(self, train_df: pd.DataFrame) -> Tuple[GradientBoostingRegressor, Dict]:
        """Train a new model on the provided data"""
        self.logger.info("Starting model training...")
        
        # Prepare data
        train_df = self.processor.prepare_features(train_df)
        
        X = train_df[EXPECTED_FEATURES]
        y = train_df[self.config.target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.test_size, 
            random_state=self.config.random_state
        )
        
        self.logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=self.config.n_estimators,
            learning_rate=self.config.learning_rate,
            max_depth=self.config.max_depth,
            random_state=self.config.random_state
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_train_pred = model.predict(X_train)
        
        performance = self._calculate_performance(
            y_train, y_train_pred, y_test, y_pred, 
            X_train, X_test, train_df
        )
        
        # Save model and performance
        self._save_model(model, performance)
        
        self.logger.info(f"Model trained with R²: {performance['r2_score']:.4f}")
        return model, performance
    
    def predict(self, model: GradientBoostingRegressor, X_input: pd.DataFrame) -> np.ndarray:
        """Make predictions with the model"""
        X_input = self.processor.prepare_features(X_input)
        X_features = X_input[EXPECTED_FEATURES]
        return model.predict(X_features)
    
    def _calculate_performance(self, y_train, y_train_pred, y_test, y_pred, 
                               X_train, X_test, train_df) -> Dict:
        """Calculate performance metrics"""
        return {
            'r2_score': float(r2_score(y_test, y_pred)),
            'train_r2_score': float(r2_score(y_train, y_train_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'n_features': len(EXPECTED_FEATURES),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'target_column': self.config.target_column,
            'timestamp': datetime.now().isoformat(),
            'dataset_rows': len(train_df)
        }
    
    def _save_model(self, model, performance: Dict):
        """Save model and performance metrics"""
        os.makedirs('../models', exist_ok=True)  # Save to parent project's models folder
        os.makedirs('models', exist_ok=True)     # Also save locally
        
        # Save to parent project
        joblib.dump(model, '../models/gradient_boosting_final.pkl')
        with open('../models/model_performance.json', 'w') as f:
            json.dump(performance, f, indent=2)
        
        # Also save locally
        joblib.dump(model, 'models/gradient_boosting_final.pkl')
        with open('models/model_performance.json', 'w') as f:
            json.dump(performance, f, indent=2)
        
        self.logger.info(f"Model saved to ../models/ and models/")
    
    def get_feature_importance(self, model: GradientBoostingRegressor) -> pd.DataFrame:
        """Get feature importance from the model"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_df = pd.DataFrame({
                'Feature': EXPECTED_FEATURES[:len(importance)],
                'Importance': importance[:len(EXPECTED_FEATURES)]
            }).sort_values('Importance', ascending=False)
            return feature_df
        return pd.DataFrame()


class ModelMetrics:
    """Calculate and manage model metrics"""
    
    @staticmethod
    def calculate_arpu(usage_gb: float, plan_type: str) -> float:
        """Calculate ARPU based on usage and plan"""
        pricing = PRICING_BENCHMARKS.get(plan_type, PRICING_BENCHMARKS['Prepaid'])
        data_charge = usage_gb * pricing['base_rate_per_gb']
        monthly_fee = pricing['monthly_fee']
        
        # Tiered pricing
        if usage_gb > 30:
            arpu = (data_charge * 0.75) + monthly_fee
        elif usage_gb > 20:
            arpu = (data_charge * 0.82) + monthly_fee
        elif usage_gb > 10:
            arpu = (data_charge * 0.90) + monthly_fee
        elif usage_gb > 5:
            arpu = data_charge + monthly_fee
        else:
            arpu = (data_charge * 1.15) + monthly_fee
        
        min_arpu = 29 if 'Prepaid' in plan_type else 79
        return round(max(min_arpu, arpu), 2)