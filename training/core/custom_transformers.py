"""
PHASE 4. 

Custom Transformers for Telecom Consumption Intelligence (Time-Series)"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class DropColumns(BaseEstimator, TransformerMixin):
    def __init__(self, cols):
        self.cols = cols

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.cols, errors="ignore")

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.array([])
        return np.array([f for f in input_features if f not in self.cols])


class CyclicalDayOfWeek(BaseEstimator, TransformerMixin):
    def __init__(self, keep_original=True):
        self.keep_original = keep_original

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        if "day_of_week" in X.columns:
            X["dow_sin"] = np.sin(2 * np.pi * X["day_of_week"] / 7)
            X["dow_cos"] = np.cos(2 * np.pi * X["day_of_week"] / 7)
            if not self.keep_original:
                X = X.drop(columns=["day_of_week"])
        return X

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.array(["dow_sin", "dow_cos"])
        features = list(input_features)
        if "day_of_week" in features and not self.keep_original:
            features.remove("day_of_week")
        features.extend(["dow_sin", "dow_cos"])
        return np.array(features)