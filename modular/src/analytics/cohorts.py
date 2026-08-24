"""
Cohort analysis utilities
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CohortAnalyzer:
    """Perform cohort analysis on customer data"""
    
    def analyze_cohorts(self, df: pd.DataFrame, 
                        cohort_col: str = 'plan_type',
                        metric_col: str = 'total_data_gb') -> pd.DataFrame:
        """
        Analyze customer cohorts
        
        Args:
            df: DataFrame with customer data
            cohort_col: Column to group by (e.g., 'plan_type', 'age_group')
            metric_col: Metric to analyze (e.g., 'total_data_gb')
        
        Returns:
            Cohort analysis DataFrame
        """
        if cohort_col not in df.columns or metric_col not in df.columns:
            logger.warning(f"Required columns not found: {cohort_col} or {metric_col}")
            return pd.DataFrame()
        
        # Group by cohort
        cohorts = df.groupby(cohort_col).agg({
            metric_col: ['mean', 'median', 'std', 'count'],
            'total_subscribers': 'sum' if 'total_subscribers' in df.columns else 'count'
        }).reset_index()
        
        # Rename columns
        cohorts.columns = ['cohort', 'mean', 'median', 'std', 'count', 'total']
        
        # Calculate percentage
        cohorts['percentage'] = (cohorts['count'] / cohorts['count'].sum()) * 100
        
        # Calculate retention (simplified)
        cohorts['retention_rate'] = cohorts['count'] / cohorts['count'].max()
        
        return cohorts
    
    def cohort_matrix(self, df: pd.DataFrame, 
                      row_col: str = 'age_group',
                      col_col: str = 'plan_type',
                      value_col: str = 'total_data_gb') -> pd.DataFrame:
        """
        Create a cohort matrix (pivot table)
        
        Args:
            df: DataFrame with customer data
            row_col: Column for rows
            col_col: Column for columns
            value_col: Column for values
        
        Returns:
            Pivot table DataFrame
        """
        pivot = pd.pivot_table(
            df,
            values=value_col,
            index=row_col,
            columns=col_col,
            aggfunc='mean',
            fill_value=0
        )
        
        return pivot
    
    def segment_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze customer segments"""
        
        # Segment by usage
        if 'total_data_gb' in df.columns:
            low_usage = len(df[df['total_data_gb'] < 2])
            mid_usage = len(df[(df['total_data_gb'] >= 2) & (df['total_data_gb'] < 5)])
            high_usage = len(df[df['total_data_gb'] >= 5])
            
            total = len(df)
            
            return {
                'low_usage': {'count': low_usage, 'percentage': (low_usage/total)*100},
                'medium_usage': {'count': mid_usage, 'percentage': (mid_usage/total)*100},
                'high_usage': {'count': high_usage, 'percentage': (high_usage/total)*100},
                'total': total
            }
        
        return {}