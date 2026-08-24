"""
Data loading utilities
"""
import os
import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Tuple
from pathlib import Path
from ..config import CONFIG
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """Handle data loading from various sources"""
    
    def __init__(self):
        self.config = CONFIG.data
        self.logger = logger
    
    @st.cache_data(ttl=3600)
    def load_default_data(_self) -> Optional[pd.DataFrame]:  # ← FIXED: Added underscore to _self
        """Load default data from configured paths"""
        try:
            for path in _self.config.default_data_paths:
                if os.path.exists(path):
                    _self.logger.info(f"Loading data from: {path}")
                    
                    if path.endswith('.parquet'):
                        df = pd.read_parquet(path)
                    else:
                        df = pd.read_csv(path)
                    
                    _self.logger.info(f"Loaded {len(df)} rows from {path}")
                    return df
            
            _self.logger.warning("No default data found")
            return None
            
        except Exception as e:
            _self.logger.error(f"Error loading default data: {str(e)}")
            return None
    
    @st.cache_data(ttl=300)
    def load_uploaded_data(_self, uploaded_file) -> Optional[pd.DataFrame]:  # ← FIXED: Added underscore to _self
        """Load uploaded file data"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_parquet(uploaded_file)
            
            _self.logger.info(f"Loaded {len(df)} rows from uploaded file: {uploaded_file.name}")
            return df
            
        except Exception as e:
            _self.logger.error(f"Error loading uploaded data: {str(e)}")
            raise
    
    def get_sample_data(self, df: pd.DataFrame, n: int = None) -> pd.DataFrame:
        """Get a sample of data for preview"""
        if n is None:
            n = self.config.sample_size_preview
        
        if len(df) > n:
            return df.sample(n=n, random_state=42)
        return df
    
    def get_data_hash(self, df: pd.DataFrame) -> str:
        """Generate hash for data tracking"""
        import hashlib
        return hashlib.md5(
            pd.util.hash_pandas_object(df).values.tobytes()
        ).hexdigest()[:8]


class DataValidator:
    """Validate data for processing"""
    
    def __init__(self):
        self.logger = logger
    
    def validate_file_size(self, file_size_bytes: int) -> bool:
        """Validate file size doesn't exceed limit"""
        from ..config import CONFIG
        max_bytes = CONFIG.data.max_file_size_mb * 1024 * 1024
        if file_size_bytes > max_bytes:
            raise ValueError(f"File too large. Max size: {CONFIG.data.max_file_size_mb}MB")
        return True
    
    def validate_format(self, filename: str) -> bool:
        """Validate file format is supported"""
        from ..config import CONFIG
        ext = filename.split('.')[-1].lower()
        if ext not in CONFIG.data.supported_formats:
            raise ValueError(f"Unsupported format: {ext}. Supported: {CONFIG.data.supported_formats}")
        return True
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, list]:
        """
        Validate the DataFrame has required structure
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        if df is None or len(df) == 0:
            errors.append("DataFrame is empty or None")
            return False, errors
        
        # Check for required columns
        required_columns = ['age_group', 'plan_type', 'network_type']
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        # Check data types
        numeric_columns = ['hours_streaming', 'hours_social', 'hours_messaging', 'hours_gaming']
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Column {col} should be numeric")
        
        return len(errors) == 0, errors
    
    def validate_predictions(self, y_pred: np.ndarray) -> Tuple[bool, list]:
        """
        Validate predictions are reasonable
        
        Returns:
            (is_valid, warnings)
        """
        import numpy as np
        warnings = []
        
        if len(y_pred) == 0:
            warnings.append("No predictions generated")
            return False, warnings
        
        # Check for negative values
        if np.any(y_pred < 0):
            warnings.append("Some predictions are negative")
        
        # Check for extremely large values
        if np.any(y_pred > 100):
            warnings.append("Some predictions are very large (>100 GB)")
        
        return len(warnings) == 0, warnings