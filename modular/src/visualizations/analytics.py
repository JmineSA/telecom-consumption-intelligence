"""
Analytics visualizations
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List

from ..constants import AGE_MAPPING, PLAN_MAPPING, REV_AGE, REV_PLAN
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsVisualizations:
    """Analytics visualizations"""
    
    def create_activity_breakdown(self, df: pd.DataFrame, 
                                  activity_cols: List[str]) -> Optional[go.Figure]:
        """Create activity breakdown chart"""
        if not all(col in df.columns for col in activity_cols):
            return None
        
        activity_avg = df[activity_cols].mean()
        
        fig = go.Figure()
        
        colors = ['#3949ab', '#5c6bc0', '#8e99d6', '#aeb8e8']
        for i, col in enumerate(activity_cols):
            fig.add_trace(go.Bar(
                x=[col.replace('hours_', '').title()],
                y=[activity_avg[col]],
                marker_color=colors[i],
                name=col.replace('hours_', '').title(),
                text=[f"{activity_avg[col]:.1f}h"],
                textposition='auto'
            ))
        
        fig.update_layout(
            title='Average Daily Hours by Activity',
            yaxis_title='Hours',
            height=350,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            bargap=0.3
        )
        
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame, 
                                   columns: List[str]) -> Optional[go.Figure]:
        """Create correlation heatmap"""
        if not all(col in df.columns for col in columns):
            return None
        
        corr_data = df[columns].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_data.values,
            x=corr_data.columns,
            y=corr_data.index,
            colorscale='RdBu',
            zmin=-1, zmax=1,
            text=corr_data.round(2).values,
            texttemplate='%{text}',
            textfont={'size': 10}
        ))
        
        fig.update_layout(
            title='Correlation Matrix',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'}
        )
        
        return fig
    
    def create_forecast(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create forecast chart with confidence intervals"""
        if df is None or len(df) < 10:
            return None
        
        dates = pd.date_range(start='2024-01-01', periods=min(len(df), 90), freq='D')
        usage_data = df['total_data_gb'].iloc[:len(dates)].values
        
        if len(usage_data) < len(dates):
            usage_data = np.resize(usage_data, len(dates))
        
        window = 7
        smoothed = np.convolve(usage_data, np.ones(window)/window, mode='same')
        
        future_dates = pd.date_range(start=dates[-1], periods=31, freq='D')[1:]
        forecast_mean = smoothed[-1] * np.linspace(1, 1.05, 30)
        forecast_std = np.std(usage_data) * 0.3
        
        fig = go.Figure()
        
        # Historical
        fig.add_trace(go.Scatter(
            x=dates,
            y=usage_data,
            mode='lines+markers',
            name='Historical',
            line=dict(color='#3949ab', width=2.5),
            marker=dict(size=4, color='#3949ab')
        ))
        
        # Moving average
        fig.add_trace(go.Scatter(
            x=dates,
            y=smoothed,
            mode='lines',
            name='7-Day MA',
            line=dict(color='#5c6bc0', width=2, dash='dash')
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_mean,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#e65100', width=2.5),
            marker=dict(size=6, color='#e65100')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=np.concatenate([future_dates, future_dates[::-1]]),
            y=np.concatenate([forecast_mean + 1.96 * forecast_std, 
                              (forecast_mean - 1.96 * forecast_std)[::-1]]),
            fill='toself',
            fillcolor='rgba(230, 81, 0, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% CI',
            showlegend=True
        ))
        
        fig.update_layout(
            title='Consumption Forecast with Confidence Intervals',
            xaxis_title='Date',
            yaxis_title='Data Usage (GB)',
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            hovermode='x unified'
        )
        
        return fig
    
    def create_segment_bubble_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create segment bubble chart"""
        if df is None or len(df) == 0:
            return None
        
        df = df.copy()
        
        if 'age_group' in df.columns:
            df['age_display'] = df['age_group'].map(REV_AGE)
        
        if 'plan_type' in df.columns:
            df['plan_display'] = df['plan_type'].map(REV_PLAN)
        
        if 'age_display' not in df.columns or 'plan_display' not in df.columns:
            return None
        
        if 'total_data_gb' not in df.columns:
            return None
        
        segment_df = df.groupby(['age_display', 'plan_display']).agg({
            'total_data_gb': ['mean', 'count', 'std']
        }).reset_index()
        
        segment_df.columns = ['age', 'plan', 'avg_usage', 'count', 'std_usage']
        segment_df = segment_df.dropna()
        
        if len(segment_df) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=segment_df['avg_usage'],
            y=segment_df['count'],
            mode='markers',
            marker=dict(
                size=segment_df['std_usage'] * 2 + 5,
                color=segment_df['avg_usage'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title='Avg Usage (GB)'),
                line=dict(width=1, color='white'),
                sizemode='area',
                sizeref=1
            ),
            text=segment_df.apply(lambda r: f"Age: {r['age']}<br>Plan: {r['plan']}<br>Avg: {r['avg_usage']:.1f} GB<br>Count: {r['count']:,}", axis=1),
            hoverinfo='text'
        ))
        
        fig.update_layout(
            title='Segment Analysis: Age vs Plan',
            xaxis_title='Average Usage (GB)',
            yaxis_title='Number of Users',
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            hoverlabel=dict(bgcolor='white', font_size=12)
        )
        
        return fig