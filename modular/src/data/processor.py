"""
Data preprocessing and feature engineering
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple
from ..constants import (
    EXPECTED_FEATURES, AGE_MAPPING, PLAN_MAPPING, 
    NETWORK_MAPPING, DEVICE_TYPES
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Handle data preprocessing and feature engineering"""
    
    def __init__(self):
        self.logger = logger
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert categorical columns to numeric"""
        df = df.copy()
        
        # Age group encoding
        if 'age_group' in df.columns and df['age_group'].dtype == 'object':
            df['age_group'] = df['age_group'].map(AGE_MAPPING)
            df['age_group'] = df['age_group'].fillna(1).astype(int)
        
        # Plan type encoding
        if 'plan_type' in df.columns and df['plan_type'].dtype == 'object':
            df['plan_type'] = df['plan_type'].map(PLAN_MAPPING)
            df['plan_type'] = df['plan_type'].fillna(1).astype(int)
        
        # Network type encoding
        if 'network_type' in df.columns and df['network_type'].dtype == 'object':
            df['network_type'] = df['network_type'].map(NETWORK_MAPPING)
            df['network_type'] = df['network_type'].fillna(1).astype(int)
        
        # Device type one-hot encoding
        if 'device_type' in df.columns and df['device_type'].dtype == 'object':
            for device in DEVICE_TYPES:
                df[f'device_type_{device}'] = (df['device_type'] == device).astype(int)
            df = df.drop(columns=['device_type'])
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training/prediction"""
        df = df.copy()
        df = self.encode_categorical(df)
        
        # Ensure all expected features exist
        for col in EXPECTED_FEATURES:
            if col not in df.columns:
                if col.startswith('device_type_'):
                    df[col] = 0
                elif col == 'is_peak_hour_user':
                    df[col] = 0
                elif col == 'is_weekend':
                    df[col] = 0
                else:
                    df[col] = 0
        
        # Convert to numeric and handle missing values
        for col in EXPECTED_FEATURES:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        self.logger.info(f"Prepared features: {len(df)} rows, {len(EXPECTED_FEATURES)} features")
        return df
    
    def create_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variable if not present"""
        df = df.copy()
        
        if 'total_data_gb' not in df.columns:
            self.logger.warning("No 'total_data_gb' column found. Creating synthetic target...")
            
            if all(col in df.columns for col in ['hours_streaming', 'hours_social', 'hours_gaming', 'hours_messaging']):
                # Synthetic target from usage hours
                df['total_data_gb'] = (
                    df['hours_streaming'] * 0.8 +
                    df['hours_social'] * 0.5 +
                    df['hours_gaming'] * 0.6 +
                    df['hours_messaging'] * 0.2 +
                    np.random.normal(0, 0.5, len(df))
                )
                df['total_data_gb'] = np.maximum(0.1, df['total_data_gb'])
                self.logger.info("Created synthetic target variable")
            else:
                raise ValueError("Required columns not found for target creation")
        
        return df
    
    def validate_features(self, df: pd.DataFrame) -> Tuple[bool, list, list]:
        """Validate features for model input"""
        missing = [f for f in EXPECTED_FEATURES if f not in df.columns]
        
        errors = []
        if 'hours_streaming' in df.columns:
            if (df['hours_streaming'] < 0).any() or (df['hours_streaming'] > 24).any():
                errors.append("Streaming hours must be between 0 and 24")
        
        if 'hours_gaming' in df.columns:
            if (df['hours_gaming'] < 0).any() or (df['hours_gaming'] > 24).any():
                errors.append("Gaming hours must be between 0 and 24")
        
        if 'age_group' in df.columns:
            if (df['age_group'] < 0).any() or (df['age_group'] > 4).any():
                errors.append("Age group must be between 0 and 4")
        
        return len(missing) == 0, missing, errors