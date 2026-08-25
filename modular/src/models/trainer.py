"""
Model training utilities
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from ..config import CONFIG
from ..constants import EXPECTED_FEATURES
from ..data.processor import DataProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Handle model training with hyperparameter tuning"""
    
    def __init__(self):
        self.config = CONFIG.model
        self.processor = DataProcessor()
        self.logger = logger
    
    def train_gradient_boosting(self, df: pd.DataFrame) -> Tuple[GradientBoostingRegressor, Dict]:
        """Train Gradient Boosting model"""
        self.logger.info("Training Gradient Boosting model...")
        return self._train_model(df, GradientBoostingRegressor)
    
    def train_random_forest(self, df: pd.DataFrame) -> Tuple[RandomForestRegressor, Dict]:
        """Train Random Forest model"""
        self.logger.info("Training Random Forest model...")
        return self._train_model(df, RandomForestRegressor)
    
    def _train_model(self, df: pd.DataFrame, model_class) -> Tuple[Any, Dict]:
        """Generic model training"""
        df = self.processor.prepare_features(df)
        
        X = df[EXPECTED_FEATURES]
        y = df[self.config.target_column]
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.test_size,
            random_state=self.config.random_state
        )
        
        # Train model
        model = model_class(
            n_estimators=self.config.n_estimators,
            random_state=self.config.random_state,
            **self._get_model_params(model_class)
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_train_pred = model.predict(X_train)
        
        performance = {
            'r2_score': float(r2_score(y_test, y_pred)),
            'train_r2_score': float(r2_score(y_train, y_train_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'model_type': model_class.__name__,
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        return model, performance
    
    def _get_model_params(self, model_class) -> Dict:
        """Get model-specific parameters"""
        if model_class == GradientBoostingRegressor:
            return {
                'learning_rate': self.config.learning_rate,
                'max_depth': self.config.max_depth
            }
        elif model_class == RandomForestRegressor:
            return {
                'max_depth': self.config.max_depth,
                'n_jobs': -1
            }
        return {}
    
    def cross_validate(self, model, X, y, cv: int = 5) -> Dict:
        """Perform cross-validation"""
        scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
        
        return {
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'min_score': float(np.min(scores)),
            'max_score': float(np.max(scores)),
            'scores': scores.tolist()
        }
    
    def hyperparameter_tuning(self, df: pd.DataFrame) -> Dict:
        """Perform hyperparameter tuning"""
        self.logger.info("Performing hyperparameter tuning...")
        
        df = self.processor.prepare_features(df)
        X = df[EXPECTED_FEATURES]
        y = df[self.config.target_column]
        
        param_grid = {
            'n_estimators': [50, 100, 150],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7]
        }
        
        grid_search = GridSearchCV(
            GradientBoostingRegressor(random_state=self.config.random_state),
            param_grid,
            cv=3,
            scoring='r2',
            n_jobs=-1
        )
        grid_search.fit(X, y)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': float(grid_search.best_score_),
            'cv_results': grid_search.cv_results_
        }