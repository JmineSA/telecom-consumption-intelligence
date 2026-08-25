"""
Prediction utilities
"""
import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any
from datetime import datetime

from ..constants import EXPECTED_FEATURES
from ..data.processor import DataProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelPredictor:
    """Handle predictions and prediction analysis"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.logger = logger
    
    def predict_batch(self, model, df: pd.DataFrame, 
                      return_details: bool = False) -> Union[np.ndarray, Dict]:
        """
        Make batch predictions
        
        Args:
            model: Trained model
            df: DataFrame with features
            return_details: If True, return detailed results including confidence
        
        Returns:
            Predictions or detailed results
        """
        self.logger.info(f"Making batch predictions for {len(df)} rows")
        
        df = self.processor.prepare_features(df)
        X = df[EXPECTED_FEATURES].values
        
        predictions = model.predict(X)
        
        if return_details:
            # Calculate confidence intervals (using prediction variance)
            try:
                # For models with .std() method (like GradientBoosting)
                if hasattr(model, 'std'):
                    stds = model.std(X)
                    confidence = 1 - (stds / predictions)
                    confidence = np.clip(confidence, 0, 1)
                else:
                    confidence = np.ones_like(predictions) * 0.85  # Default confidence
            except:
                confidence = np.ones_like(predictions) * 0.85
            
            return {
                'predictions': predictions,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'n_samples': len(predictions)
            }
        
        return predictions
    
    def predict_single(self, model, features: Dict[str, Any]) -> Dict:
        """
        Make a single prediction from feature dictionary
        
        Args:
            model: Trained model
            features: Dictionary of feature values
        
        Returns:
            Dictionary with prediction and details
        """
        # Convert to DataFrame
        df = pd.DataFrame([features])
        df = self.processor.prepare_features(df)
        
        # Make prediction
        X = df[EXPECTED_FEATURES].values
        prediction = model.predict(X)[0]
        
        return {
            'prediction': float(prediction),
            'features': features,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_prediction(self, model, features: Dict[str, Any]) -> Dict:
        """
        Analyze a single prediction with feature importance
        
        Args:
            model: Trained model
            features: Dictionary of feature values
        
        Returns:
            Detailed prediction analysis
        """
        # Get prediction
        result = self.predict_single(model, features)
        
        # Get feature importance if available
        if hasattr(model, 'feature_importances_'):
            df = pd.DataFrame([features])
            df = self.processor.prepare_features(df)
            X = df[EXPECTED_FEATURES].values[0]
            
            importance = model.feature_importances_
            feature_impacts = {}
            
            for i, feat in enumerate(EXPECTED_FEATURES):
                if i < len(importance):
                    # Approximate contribution
                    contrib = importance[i] * X[i] * 2
                    feature_impacts[feat] = float(contrib)
            
            result['feature_impacts'] = feature_impacts
            result['top_features'] = sorted(
                feature_impacts.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )[:5]
        
        return result