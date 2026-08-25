"""
Predictive maintenance alerts for network issues
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PredictiveMaintenance:
    """Predictive maintenance for network issues"""
    
    def __init__(self):
        self.logger = logger
    
    def detect_network_issues(self, df: pd.DataFrame, 
                              threshold_percentile: float = 95) -> List[Dict]:
        """
        Detect potential network issues
        
        Args:
            df: DataFrame with network data
            threshold_percentile: Percentile threshold for warnings
        
        Returns:
            List of warnings
        """
        warnings = []
        
        if 'network_type' not in df.columns or 'total_data_gb' not in df.columns:
            self.logger.warning("Required columns not found for network analysis")
            return warnings
        
        # Calculate network load
        network_load = df.groupby('network_type')['total_data_gb'].sum()
        
        if len(network_load) == 0:
            return warnings
        
        threshold = network_load.quantile(threshold_percentile / 100)
        
        network_names = {0: '3G', 1: '4G', 2: '4G+', 3: '5G'}
        
        for network, load in network_load.items():
            network_name = network_names.get(network, f'Network_{network}')
            
            if load > threshold:
                warnings.append({
                    'network': network_name,
                    'load': float(load),
                    'threshold': float(threshold),
                    'status': 'Critical',
                    'recommendation': 'Immediate capacity expansion needed',
                    'severity': 'High'
                })
            elif load > threshold * 0.8:
                warnings.append({
                    'network': network_name,
                    'load': float(load),
                    'threshold': float(threshold),
                    'status': 'Warning',
                    'recommendation': 'Monitor and consider capacity upgrade',
                    'severity': 'Medium'
                })
        
        return warnings
    
    def detect_usage_anomalies(self, df: pd.DataFrame, 
                               window_days: int = 7) -> pd.DataFrame:
        """
        Detect sudden changes in usage patterns
        
        Args:
            df: DataFrame with usage data
            window_days: Rolling window for comparison
        
        Returns:
            DataFrame with anomalies
        """
        if 'total_data_gb' not in df.columns:
            return pd.DataFrame()
        
        # Create time series
        df_copy = df.copy()
        df_copy['date'] = pd.date_range(
            start=datetime.now() - timedelta(days=len(df)), 
            periods=len(df), 
            freq='D'
        )
        
        # Calculate rolling statistics
        df_copy['rolling_mean'] = df_copy['total_data_gb'].rolling(window=window_days).mean()
        df_copy['rolling_std'] = df_copy['total_data_gb'].rolling(window=window_days).std()
        df_copy['z_score'] = (df_copy['total_data_gb'] - df_copy['rolling_mean']) / df_copy['rolling_std']
        
        # Detect anomalies
        anomalies = df_copy[df_copy['z_score'].abs() > 2.5].copy()
        
        if len(anomalies) > 0:
            anomalies['anomaly_type'] = anomalies['z_score'].apply(
                lambda x: 'High Spike' if x > 0 else 'Sudden Drop'
            )
            anomalies['severity'] = anomalies['z_score'].apply(
                lambda x: 'High' if abs(x) > 3 else 'Medium' if abs(x) > 2.5 else 'Low'
            )
        
        return anomalies
    
    def generate_maintenance_schedule(self, df: pd.DataFrame) -> Dict:
        """
        Generate maintenance recommendations based on usage patterns
        
        Args:
            df: DataFrame with usage data
        
        Returns:
            Dictionary with maintenance recommendations
        """
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': [],
            'peak_hours': []
        }
        
        if 'total_data_gb' not in df.columns:
            return recommendations
        
        # Find peak usage hours
        if 'is_peak_hour_user' in df.columns:
            peak_hours = df[df['is_peak_hour_user'] == 1]
            if len(peak_hours) > 0:
                recommendations['peak_hours'] = [
                    {
                        'description': f"{len(peak_hours)} users active during peak hours",
                        'recommendation': 'Consider capacity expansion during peak hours'
                    }
                ]
        
        # Check for high usage
        high_usage = df[df['total_data_gb'] > 5]
        if len(high_usage) > 0:
            recommendations['short_term'].append({
                'description': f"{len(high_usage)} users with high usage (>5 GB)",
                'recommendation': 'Target for premium plan upgrades'
            })
        
        # Check for very high usage
        very_high_usage = df[df['total_data_gb'] > 10]
        if len(very_high_usage) > 0:
            recommendations['immediate'].append({
                'description': f"{len(very_high_usage)} users with very high usage (>10 GB)",
                'recommendation': 'Immediate investigation and potential plan adjustment'
            })
        
        # Check network distribution
        if 'network_type' in df.columns:
            network_counts = df['network_type'].value_counts()
            if 3 in network_counts.index:  # 5G
                pct_5g = (network_counts.get(3, 0) / len(df)) * 100
                if pct_5g > 20:
                    recommendations['long_term'].append({
                        'description': f"{pct_5g:.1f}% of users on 5G",
                        'recommendation': 'Plan for 5G infrastructure expansion'
                    })
        
        return recommendations