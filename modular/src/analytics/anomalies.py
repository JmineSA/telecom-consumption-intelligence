"""
Anomaly detection utilities
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from scipy import stats
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnomalyDetector:
    """Detect anomalies in data"""
    
    def detect_anomalies(self, df: pd.DataFrame, columns: List[str], 
                         threshold: float = 2.5) -> pd.DataFrame:
        """
        Detect anomalies using z-score method
        
        Args:
            df: DataFrame to analyze
            columns: Columns to check for anomalies
            threshold: Z-score threshold for anomaly detection
        
        Returns:
            DataFrame with detected anomalies
        """
        anomalies = pd.DataFrame()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            # Get numeric data
            valid_data = df[col].dropna()
            if len(valid_data) == 0:
                continue
            
            # Calculate z-scores using scipy
            z_scores = np.abs(stats.zscore(valid_data))
            
            # Create boolean mask for anomalies
            anomaly_mask = z_scores > threshold
            
            if anomaly_mask.sum() > 0:
                # Get the indices where anomalies occur
                anomaly_indices = valid_data.index[anomaly_mask]
                
                # Get the original rows at these indices
                col_anomalies = df.loc[anomaly_indices].copy()
                col_anomalies['anomaly_column'] = col
                col_anomalies['z_score'] = z_scores[anomaly_mask]
                col_anomalies['original_value'] = valid_data[anomaly_mask]
                col_anomalies['anomaly_type'] = 'high' if z_scores[anomaly_mask] > 0 else 'low'
                
                anomalies = pd.concat([anomalies, col_anomalies], ignore_index=True)
        
        if len(anomalies) > 0:
            logger.info(f"Detected {len(anomalies)} anomalies")
        
        return anomalies
    
    def detect_iqr_anomalies(self, df: pd.DataFrame, columns: List[str],
                             factor: float = 1.5) -> pd.DataFrame:
        """
        Detect anomalies using IQR method
        
        Args:
            df: DataFrame to analyze
            columns: Columns to check for anomalies
            factor: IQR multiplier (default 1.5)
        
        Returns:
            DataFrame with detected anomalies
        """
        anomalies = pd.DataFrame()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            valid_data = df[col].dropna()
            if len(valid_data) == 0:
                continue
            
            Q1 = valid_data.quantile(0.25)
            Q3 = valid_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            
            anomaly_mask = (valid_data < lower_bound) | (valid_data > upper_bound)
            
            if anomaly_mask.sum() > 0:
                anomaly_indices = valid_data.index[anomaly_mask]
                col_anomalies = df.loc[anomaly_indices].copy()
                col_anomalies['anomaly_column'] = col
                col_anomalies['original_value'] = valid_data[anomaly_mask]
                col_anomalies['anomaly_type'] = 'high' if valid_data[anomaly_mask] > upper_bound else 'low'
                
                anomalies = pd.concat([anomalies, col_anomalies], ignore_index=True)
        
        return anomalies
    
    def get_anomaly_summary(self, anomalies: pd.DataFrame) -> Dict:
        """Get summary statistics for anomalies"""
        if len(anomalies) == 0:
            return {'total': 0, 'by_column': {}, 'by_type': {}}
        
        summary = {
            'total': len(anomalies),
            'by_column': anomalies['anomaly_column'].value_counts().to_dict(),
            'by_type': anomalies['anomaly_type'].value_counts().to_dict()
        }
        
        return summary