"""
Analytics and metrics calculation
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCalculator:
    """Calculate business and technical metrics"""
    
    def calculate_all_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all metrics from dataset"""
        metrics = {}
        
        if df is None or len(df) == 0:
            return metrics
        
        metrics['total_subscribers'] = len(df)
        
        # Usage metrics
        usage_metrics = self._calculate_usage_metrics(df)
        metrics.update(usage_metrics)
        
        # Network metrics
        network_metrics = self._calculate_network_metrics(df)
        metrics.update(network_metrics)
        
        # Demographic metrics
        demo_metrics = self._calculate_demographic_metrics(df)
        metrics.update(demo_metrics)
        
        return metrics
    
    def _calculate_usage_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate usage-related metrics"""
        metrics = {}
        
        if 'total_data_gb' in df.columns:
            data = df['total_data_gb']
            metrics['avg_usage'] = data.mean()
            metrics['max_usage'] = data.max()
            metrics['min_usage'] = data.min()
            metrics['median_usage'] = data.median()
            metrics['std_usage'] = data.std()
            
            # Heavy users
            heavy_users = len(df[df['total_data_gb'] >= 5])
            metrics['heavy_users'] = heavy_users
            metrics['pct_heavy'] = (heavy_users / len(df)) * 100
            
            # Usage growth (80/20 split)
            split_idx = int(len(df) * 0.8)
            if split_idx > 0 and split_idx < len(df):
                first_avg = df['total_data_gb'].iloc[:split_idx].mean()
                second_avg = df['total_data_gb'].iloc[split_idx:].mean()
                metrics['usage_growth'] = ((second_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
            else:
                metrics['usage_growth'] = 0
            
            # Percentiles
            metrics['pct_25'] = data.quantile(0.25)
            metrics['pct_75'] = data.quantile(0.75)
            metrics['iqr'] = metrics['pct_75'] - metrics['pct_25']
        
        return metrics
    
    def _calculate_network_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate network-related metrics"""
        metrics = {}
        
        if 'network_type' in df.columns:
            # 5G adoption
            pct_5g = (df['network_type'] == 3).mean() * 100
            metrics['pct_5g'] = pct_5g
            
            # Network distribution
            network_counts = df['network_type'].value_counts()
            network_map = {0: '3G', 1: '4G', 2: '4G+', 3: '5G'}
            
            for k, v in network_counts.items():
                network_name = network_map.get(k, f'Type_{k}')
                metrics[f'pct_{network_name}'] = (v / len(df)) * 100
        
        return metrics
    
    def _calculate_demographic_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate demographic metrics"""
        metrics = {}
        
        if 'age_group' in df.columns:
            age_counts = df['age_group'].value_counts()
            from ..constants import REV_AGE
            for age_idx, count in age_counts.items():
                age_name = REV_AGE.get(age_idx, f'Age_{age_idx}')
                metrics[f'pct_{age_name.replace("-", "_")}'] = (count / len(df)) * 100
        
        if 'plan_type' in df.columns:
            plan_counts = df['plan_type'].value_counts()
            from ..constants import REV_PLAN
            for plan_idx, count in plan_counts.items():
                plan_name = REV_PLAN.get(plan_idx, f'Plan_{plan_idx}')
                metrics[f'pct_{plan_name}'] = (count / len(df)) * 100
        
        return metrics


class BusinessMetrics:
    """Calculate business-focused metrics"""
    
    @staticmethod
    def calculate_revenue_opportunity(df: pd.DataFrame) -> Dict:
        """Calculate revenue opportunities"""
        metrics = {}
        
        if 'total_data_gb' not in df.columns:
            return metrics
        
        heavy_users = len(df[df['total_data_gb'] >= 5])
        
        # Upsell opportunities
        metrics['upsell_revenue'] = heavy_users * 299  # Premium bundle upsell
        metrics['topup_revenue'] = len(df) * 49  # Data top-up revenue
        
        # 5G upgrade targets
        metrics['upgrade_targets'] = int(len(df) * 0.05)  # 5% high-value prospects
        
        # Average revenue per user
        from ..models.manager import ModelMetrics
        if 'plan_type' in df.columns:
            arpu_values = df.apply(
                lambda row: ModelMetrics.calculate_arpu(row['total_data_gb'], row['plan_type']),
                axis=1
            )
            metrics['avg_arpu'] = arpu_values.mean()
            metrics['total_arpu'] = arpu_values.sum()
        
        return metrics