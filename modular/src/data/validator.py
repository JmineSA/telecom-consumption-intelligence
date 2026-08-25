"""
Data validation utilities
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from ..constants import EXPECTED_FEATURES
from ..utils.logger import get_logger

logger = get_logger(__name__)


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
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
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
    
    def validate_predictions(self, y_pred: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Validate predictions are reasonable
        
        Returns:
            (is_valid, warnings)
        """
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


# Legacy functions for backward compatibility
def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Legacy function - use DataValidator class instead"""
    validator = DataValidator()
    return validator.validate_dataframe(df)


def validate_predictions(y_pred: np.ndarray) -> Tuple[bool, List[str]]:
    """Legacy function - use DataValidator class instead"""
    validator = DataValidator()
    return validator.validate_predictions(y_pred)