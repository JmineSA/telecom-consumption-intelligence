# src/core/custom_transformers.py
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# 1. Drop columns
class DropColumns(BaseEstimator, TransformerMixin):
    def __init__(self, cols):
        self.cols = cols
        self._feature_names = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.cols, errors='ignore')
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names after dropping columns."""
        if input_features is None:
            return np.array([])
        
        self._feature_names = [f for f in input_features if f not in self.cols]
        return np.array(self._feature_names)

# 2. Date feature extraction
class DateFeatures(BaseEstimator, TransformerMixin):
    def __init__(self):
        self._feature_names = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['day_of_week'] = X['measurement_date'].dt.dayofweek
        X['month'] = X['measurement_date'].dt.month
        return X.drop(columns=['measurement_date'])
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names after date feature extraction."""
        if input_features is None:
            return np.array(['day_of_week', 'month'])
        
        # Remove measurement_date and add new date features
        features = [f for f in input_features if f != 'measurement_date']
        features.extend(['day_of_week', 'month'])
        self._feature_names = features
        return np.array(features)

# 3. Cyclical encoding
class CyclicalFeatures(BaseEstimator, TransformerMixin):
    def __init__(self):
        self._feature_names = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['day_of_week_sin'] = np.sin(2 * np.pi * X['day_of_week'] / 7)
        X['day_of_week_cos'] = np.cos(2 * np.pi * X['day_of_week'] / 7)
        X['month_sin'] = np.sin(2 * np.pi * X['month'] / 12)
        X['month_cos'] = np.cos(2 * np.pi * X['month'] / 12)
        return X.drop(columns=['day_of_week', 'month'])
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names after cyclical encoding."""
        if input_features is None:
            return np.array(['day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos'])
        
        # Remove day_of_week and month, add cyclical versions
        features = [f for f in input_features if f not in ['day_of_week', 'month']]
        features.extend(['day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos'])
        self._feature_names = features
        return np.array(features)