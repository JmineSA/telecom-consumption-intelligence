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
                
                # FIX: Use array indexing properly
                # Get the z-scores for anomalies and check if they're positive
                anomaly_z_scores = z_scores[anomaly_mask]
                # Compare each value individually
                anomaly_types = ['high' if z > 0 else 'low' for z in anomaly_z_scores]
                col_anomalies['anomaly_type'] = anomaly_types
                
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
                
                # Determine anomaly type for each value
                anomaly_types = []
                for val in valid_data[anomaly_mask]:
                    if val > upper_bound:
                        anomaly_types.append('high')
                    else:
                        anomaly_types.append('low')
                col_anomalies['anomaly_type'] = anomaly_types
                
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
    
    def get_anomaly_stats(self, df: pd.DataFrame, column: str) -> Dict:
        """
        Get statistical information about a column including potential anomalies
        
        Args:
            df: DataFrame
            column: Column name
        
        Returns:
            Dictionary with statistics
        """
        if column not in df.columns:
            return {}
        
        data = df[column].dropna()
        if len(data) == 0:
            return {}
        
        # Basic stats
        stats_dict = {
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'count': len(data),
            'missing': df[column].isna().sum()
        }
        
        # Calculate z-scores
        z_scores = np.abs(stats.zscore(data))
        anomaly_mask = z_scores > 2.5
        
        stats_dict['anomaly_count'] = int(anomaly_mask.sum())
        stats_dict['anomaly_percentage'] = float((anomaly_mask.sum() / len(data)) * 100)
        
        # Get anomaly values
        if anomaly_mask.sum() > 0:
            stats_dict['anomaly_values'] = data[anomaly_mask].tolist()
        else:
            stats_dict['anomaly_values'] = []
        
        return stats_dict