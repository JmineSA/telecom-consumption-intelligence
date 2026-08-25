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
        
        # Get the project root directory
        # This file is at: modular/src/models/manager.py
        # So we need to go up 3 levels to get the project root
        current_file = os.path.abspath(__file__)  # .../modular/src/models/manager.py
        src_dir = os.path.dirname(current_file)   # .../modular/src/models
        models_dir = os.path.dirname(src_dir)      # .../modular/src
        modular_dir = os.path.dirname(models_dir)  # .../modular
        project_dir = os.path.dirname(modular_dir) # .../telecom-consumption-intelligence
        
        self.project_dir = project_dir
        self.models_dir = os.path.join(project_dir, 'models')
        
        # Build model paths - try multiple locations
        self.model_paths = [
            # Primary: Project models folder
            os.path.join(self.models_dir, 'gradient_boosting_final.pkl'),
            os.path.join(self.models_dir, 'model_performance.json'),
            
            # Relative paths from modular directory
            '../models/gradient_boosting_final.pkl',
            '../models/model_performance.json',
            
            # Relative from src directory
            '../../models/gradient_boosting_final.pkl',
            '../../models/model_performance.json',
            
            # Fallback - local models folder
            'models/gradient_boosting_final.pkl',
            'models/model_performance.json',
        ]
        
        self.perf_paths = [
            # Primary: Project models folder
            os.path.join(self.models_dir, 'model_performance.json'),
            
            # Relative paths
            '../models/model_performance.json',
            '../../models/model_performance.json',
            'models/model_performance.json',
        ]
        
        self.logger = logger
        self.logger.info(f"Project directory: {project_dir}")
        self.logger.info(f"Models directory: {self.models_dir}")
    
    def _find_existing_model(self) -> Tuple[Optional[str], Optional[str]]:
        """Find existing model and performance files"""
        # First check if models directory exists
        if os.path.exists(self.models_dir):
            self.logger.info(f"Checking models directory: {self.models_dir}")
            # Look for model file
            model_file = os.path.join(self.models_dir, 'gradient_boosting_final.pkl')
            perf_file = os.path.join(self.models_dir, 'model_performance.json')
            
            if os.path.exists(model_file) and os.path.exists(perf_file):
                self.logger.info(f"Found model in project models directory: {model_file}")
                return model_file, perf_file
        
        # Then try all paths
        for model_path in self.model_paths:
            if os.path.exists(model_path):
                self.logger.info(f"Found model at: {model_path}")
                # Find corresponding performance file
                for perf_path in self.perf_paths:
                    if os.path.exists(perf_path):
                        self.logger.info(f"Found performance file at: {perf_path}")
                        return model_path, perf_path
        
        self.logger.warning("No existing model found")
        return None, None
    
    def load(self, train_df: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
        """Load existing model or train if not available"""
        try:
            # Try to find existing model
            model_path, perf_path = self._find_existing_model()
            
            if model_path is not None and perf_path is not None:
                self.logger.info(f"Loading model from: {model_path}")
                model = joblib.load(model_path)
                
                with open(perf_path, 'r') as f:
                    performance = json.load(f)
                
                self.logger.info(f"Loaded existing model successfully")
                self.logger.info(f"Model R²: {performance.get('r2_score', 'N/A')}")
                
                return {
                    'model': model,
                    'performance': performance,
                    'is_real': True,
                    'model_path': model_path,
                    'perf_path': perf_path
                }
            
            # If no model found, try to train
            self.logger.warning("No existing model found. Trying to train...")
            if train_df is not None and len(train_df) > 0:
                self.logger.info("Training new model...")
                model, performance = self.train(train_df)
                return {
                    'model': model, 
                    'performance': performance, 
                    'is_real': True,
                    'model_path': self.model_paths[0],
                    'perf_path': self.perf_paths[0]
                }
            else:
                self.logger.warning("No training data available")
                return None
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return None
    
    def train(self, train_df: pd.DataFrame) -> Tuple[GradientBoostingRegressor, Dict]:
        """Train a new model on the provided data"""
        self.logger.info("Starting model training...")
        
        # Prepare data
        train_df = self.processor.prepare_features(train_df)
        
        # Check if target column exists
        if self.config.target_column not in train_df.columns:
            self.logger.error(f"Target column '{self.config.target_column}' not found in data")
            raise ValueError(f"Target column '{self.config.target_column}' not found in data")
        
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
        # Prepare features
        X_input = self.processor.prepare_features(X_input)
        
        # Get feature columns - keep as DataFrame to avoid warnings
        X_features = X_input[EXPECTED_FEATURES]
        
        # Make prediction
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
    
    def _save_model(self, model: GradientBoostingRegressor, performance: Dict):
        """Save model and performance metrics"""
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs('models', exist_ok=True)  # Also save locally
        
        # Save to project models folder
        model_path = os.path.join(self.models_dir, 'gradient_boosting_final.pkl')
        perf_path = os.path.join(self.models_dir, 'model_performance.json')
        
        joblib.dump(model, model_path)
        with open(perf_path, 'w') as f:
            json.dump(performance, f, indent=2)
        
        # Also save locally
        joblib.dump(model, 'models/gradient_boosting_final.pkl')
        with open('models/model_performance.json', 'w') as f:
            json.dump(performance, f, indent=2)
        
        self.logger.info(f"Model saved to: {model_path}")
        self.logger.info(f"Performance saved to: {perf_path}")
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            model_path, perf_path = self._find_existing_model()
            
            if model_path and perf_path:
                with open(perf_path, 'r') as f:
                    performance = json.load(f)
                
                return {
                    'exists': True,
                    'path': model_path,
                    'performance': performance,
                    'file_size': os.path.getsize(model_path) if os.path.exists(model_path) else 0,
                    'last_modified': datetime.fromtimestamp(
                        os.path.getmtime(model_path)
                    ).isoformat() if os.path.exists(model_path) else None
                }
        except Exception as e:
            self.logger.error(f"Error getting model info: {str(e)}")
        
        return {'exists': False}


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
    
    @staticmethod
    def calculate_usage_tier(usage_gb: float) -> str:
        """Categorize usage into tiers"""
        if usage_gb < 2:
            return 'low'
        elif usage_gb < 5:
            return 'medium'
        else:
            return 'high'
    
    @staticmethod
    def get_usage_badge(usage_gb: float) -> Dict[str, str]:
        """Get badge information for usage level"""
        tier = ModelMetrics.calculate_usage_tier(usage_gb)
        
        badges = {
            'low': {'label': 'Low Usage', 'color': '#16a34a', 'badge_class': 'badge-low'},
            'medium': {'label': 'Medium Usage', 'color': '#d97706', 'badge_class': 'badge-medium'},
            'high': {'label': 'High Usage', 'color': '#dc2626', 'badge_class': 'badge-high'}
        }
        
        return badges.get(tier, badges['low'])