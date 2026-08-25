"""
Cohort analysis utilities
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional, List, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CohortAnalyzer:
    """Perform cohort analysis on customer data"""
    
    def __init__(self):
        self.logger = logger
    
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
            self.logger.warning(f"Required columns not found: {cohort_col} or {metric_col}")
            return pd.DataFrame()
        
        # Get cohort labels
        from ..constants import REV_PLAN, REV_AGE, REV_NETWORK
        
        cohort_labels = {
            'plan_type': REV_PLAN,
            'age_group': REV_AGE,
            'network_type': REV_NETWORK
        }
        
        # Apply labels if available
        df_copy = df.copy()
        
        if cohort_col in cohort_labels:
            # Map values to display names
            df_copy['cohort_display'] = df_copy[cohort_col].map(cohort_labels[cohort_col])
            
            # For any unmapped values, create a display name
            if df_copy['cohort_display'].isna().any():
                # Get unique values that weren't mapped
                unmapped = df_copy[df_copy['cohort_display'].isna()][cohort_col].unique()
                for val in unmapped:
                    # Create a display name
                    display_name = f"{cohort_col}_{val}"
                    df_copy.loc[df_copy[cohort_col] == val, 'cohort_display'] = display_name
        else:
            # If no mapping available, use the column as-is
            df_copy['cohort_display'] = df_copy[cohort_col].astype(str)
        
        # Fill any remaining NaN values
        df_copy['cohort_display'] = df_copy['cohort_display'].fillna('Unknown')
        
        # Group by cohort
        agg_dict = {
            metric_col: ['mean', 'median', 'std', 'count']
        }
        
        # Only add total_subscribers if it exists in the dataframe
        if 'total_subscribers' in df_copy.columns:
            agg_dict['total_subscribers'] = 'sum'
        
        # Group by cohort
        cohorts = df_copy.groupby('cohort_display').agg(agg_dict).reset_index()
        
        # Rename columns
        if 'total_subscribers' in df_copy.columns:
            cohorts.columns = ['cohort', 'mean', 'median', 'std', 'count', 'total']
        else:
            cohorts.columns = ['cohort', 'mean', 'median', 'std', 'count']
            cohorts['total'] = cohorts['count']  # Use count as total
        
        # Calculate percentage
        cohorts['percentage'] = (cohorts['count'] / cohorts['count'].sum()) * 100
        
        # Calculate retention (simplified)
        cohorts['retention_rate'] = cohorts['count'] / cohorts['count'].max()
        
        # Add usage tier
        cohorts['tier'] = cohorts['mean'].apply(self._get_tier)
        
        # Sort by count descending
        cohorts = cohorts.sort_values('count', ascending=False)
        
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
        # Get labels
        from ..constants import REV_PLAN, REV_AGE, REV_NETWORK
        
        row_labels = {
            'age_group': REV_AGE,
            'plan_type': REV_PLAN,
            'network_type': REV_NETWORK
        }
        
        col_labels = {
            'plan_type': REV_PLAN,
            'age_group': REV_AGE,
            'network_type': REV_NETWORK
        }
        
        df_copy = df.copy()
        
        # Apply labels for rows
        if row_col in row_labels:
            df_copy['row_display'] = df_copy[row_col].map(row_labels[row_col])
            if df_copy['row_display'].isna().any():
                unmapped = df_copy[df_copy['row_display'].isna()][row_col].unique()
                for val in unmapped:
                    df_copy.loc[df_copy[row_col] == val, 'row_display'] = f"{row_col}_{val}"
        else:
            df_copy['row_display'] = df_copy[row_col].astype(str)
        
        # Apply labels for columns
        if col_col in col_labels:
            df_copy['col_display'] = df_copy[col_col].map(col_labels[col_col])
            if df_copy['col_display'].isna().any():
                unmapped = df_copy[df_copy['col_display'].isna()][col_col].unique()
                for val in unmapped:
                    df_copy.loc[df_copy[col_col] == val, 'col_display'] = f"{col_col}_{val}"
        else:
            df_copy['col_display'] = df_copy[col_col].astype(str)
        
        # Fill NaN values
        df_copy['row_display'] = df_copy['row_display'].fillna('Unknown')
        df_copy['col_display'] = df_copy['col_display'].fillna('Unknown')
        
        # Create pivot table
        pivot = pd.pivot_table(
            df_copy,
            values=value_col,
            index='row_display',
            columns='col_display',
            aggfunc='mean',
            fill_value=0
        )
        
        return pivot
    
    def segment_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze customer segments"""
        segments = {}
        
        # Usage segments
        if 'total_data_gb' in df.columns:
            low_usage = len(df[df['total_data_gb'] < 2])
            mid_usage = len(df[(df['total_data_gb'] >= 2) & (df['total_data_gb'] < 5)])
            high_usage = len(df[df['total_data_gb'] >= 5])
            
            total = len(df)
            
            segments['usage_segments'] = {
                'low_usage': {'count': low_usage, 'percentage': (low_usage/total)*100 if total > 0 else 0},
                'medium_usage': {'count': mid_usage, 'percentage': (mid_usage/total)*100 if total > 0 else 0},
                'high_usage': {'count': high_usage, 'percentage': (high_usage/total)*100 if total > 0 else 0},
                'total': total
            }
        
        # Plan type segments
        if 'plan_type' in df.columns:
            from ..constants import REV_PLAN
            plan_counts = df['plan_type'].value_counts()
            segments['plan_segments'] = {}
            for plan_idx, count in plan_counts.items():
                plan_name = REV_PLAN.get(plan_idx, f'Plan_{plan_idx}')
                segments['plan_segments'][plan_name] = {
                    'count': count,
                    'percentage': (count / len(df)) * 100 if len(df) > 0 else 0
                }
        
        # Age segments
        if 'age_group' in df.columns:
            from ..constants import REV_AGE
            age_counts = df['age_group'].value_counts()
            segments['age_segments'] = {}
            for age_idx, count in age_counts.items():
                age_name = REV_AGE.get(age_idx, f'Age_{age_idx}')
                segments['age_segments'][age_name] = {
                    'count': count,
                    'percentage': (count / len(df)) * 100 if len(df) > 0 else 0
                }
        
        # Network segments
        if 'network_type' in df.columns:
            from ..constants import REV_NETWORK
            network_counts = df['network_type'].value_counts()
            segments['network_segments'] = {}
            for net_idx, count in network_counts.items():
                net_name = REV_NETWORK.get(net_idx, f'Network_{net_idx}')
                segments['network_segments'][net_name] = {
                    'count': count,
                    'percentage': (count / len(df)) * 100 if len(df) > 0 else 0
                }
        
        return segments
    
    def plot_cohort_heatmap(self, pivot_df: pd.DataFrame) -> Optional[go.Figure]:
        """Create a heatmap from cohort matrix"""
        if pivot_df.empty:
            return None
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Viridis',
            text=pivot_df.values.round(1),
            texttemplate='%{text}',
            textfont={'size': 10, 'color': 'white'},
            hovertemplate='Row: %{y}<br>Col: %{x}<br>Value: %{z:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Cohort Analysis: Heatmap',
            xaxis_title='Columns',
            yaxis_title='Rows',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'}
        )
        
        return fig
    
    def plot_cohort_bars(self, cohorts_df: pd.DataFrame) -> Optional[go.Figure]:
        """Create bar chart from cohort analysis"""
        if cohorts_df.empty:
            return None
        
        fig = go.Figure()
        
        # Sort by mean for better visualization
        cohorts_df = cohorts_df.sort_values('mean', ascending=True)
        
        fig.add_trace(go.Bar(
            x=cohorts_df['mean'],
            y=cohorts_df['cohort'],
            orientation='h',
            name='Average Usage',
            marker_color='#3949ab',
            text=cohorts_df['mean'].apply(lambda x: f'{x:.1f} GB'),
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            x=cohorts_df['median'],
            y=cohorts_df['cohort'],
            orientation='h',
            name='Median Usage',
            marker_color='#5c6bc0',
            text=cohorts_df['median'].apply(lambda x: f'{x:.1f} GB'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Usage by Cohort',
            xaxis_title='Data Usage (GB)',
            yaxis_title='Cohort',
            height=max(400, len(cohorts_df) * 40),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            bargap=0.2
        )
        
        return fig
    
    def _get_tier(self, value: float) -> str:
        """Get tier based on value"""
        if value < 2:
            return 'Low'
        elif value < 5:
            return 'Medium'
        else:
            return 'High'