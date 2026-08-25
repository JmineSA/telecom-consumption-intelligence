"""
Dashboard visualizations
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DashboardVisualizations:
    """Dashboard visualizations"""
    
    def create_usage_distribution(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create usage distribution chart"""
        if 'total_data_gb' not in df.columns:
            return None
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Usage Distribution', 'Box Plot'),
            column_widths=[0.7, 0.3]
        )
        
        fig.add_trace(
            go.Histogram(
                x=df['total_data_gb'],
                nbinsx=30,
                name='Distribution',
                marker_color='#3949ab',
                opacity=0.7,
                hovertemplate='Usage: %{x:.1f} GB<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Box(
                y=df['total_data_gb'],
                name='Usage',
                boxmean='sd',
                marker_color='#5c6bc0',
                line_color='#1a237e',
                fillcolor='rgba(57, 73, 171, 0.2)'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            bargap=0.05
        )
        
        fig.update_xaxes(title_text="Data Usage (GB)", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Usage (GB)", row=1, col=2)
        
        return fig
    
    def create_trend_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create KPI trend chart"""
        if df is None or len(df) < 10:
            return None
        
        dates = pd.date_range(start='2024-01-01', periods=min(len(df), 90), freq='D')
        usage_data = df['total_data_gb'].iloc[:len(dates)].values
        
        if len(usage_data) < len(dates):
            usage_data = np.resize(usage_data, len(dates))
        
        df_dates = pd.DataFrame({'date': dates, 'usage': usage_data})
        df_dates['ma7'] = df_dates['usage'].rolling(window=7).mean()
        df_dates['ma30'] = df_dates['usage'].rolling(window=30).mean()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=df_dates['date'],
                y=df_dates['usage'],
                mode='lines+markers',
                name='Daily Usage',
                line=dict(color='#3949ab', width=2),
                marker=dict(size=3),
                hovertemplate='%{x|%b %d}<br>Usage: %{y:.1f} GB<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_dates['date'],
                y=df_dates['ma7'],
                mode='lines',
                name='7-Day MA',
                line=dict(color='#5c6bc0', width=2, dash='dot')
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_dates['date'],
                y=df_dates['ma30'],
                mode='lines',
                name='30-Day MA',
                line=dict(color='#e65100', width=2, dash='dash')
            ),
            secondary_y=False
        )
        
        fig.update_layout(
            title='Usage Trends & KPIs',
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            hovermode='x unified'
        )
        
        return fig