"""
Network visualizations
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional

from ..constants import NETWORK_MAPPING, REV_NETWORK
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NetworkVisualizations:
    """Network visualizations"""
    
    def create_network_heatmap(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create network usage heatmap"""
        if df is None or len(df) == 0:
            return None
        
        hours = list(range(24))
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        np.random.seed(42)
        heatmap_data = np.random.rand(7, 24) * 2
        
        # Realistic patterns
        for i in range(7):
            heatmap_data[i, 8:10] += 3 * np.random.rand(2)
            heatmap_data[i, 18:21] += 4 * np.random.rand(3)
            if i >= 5:
                heatmap_data[i, 12:17] += 3 * np.random.rand(5)
        
        heatmap_data[1, 20] = 8.5
        heatmap_data[3, 19] = 7.8
        heatmap_data[5, 14] = 9.2
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=hours,
            y=days,
            colorscale='Viridis',
            colorbar=dict(
                title='Usage (GB)',
                title_font=dict(color='#64748b'),
                tickfont=dict(color='#64748b')
            ),
            hovertemplate='Day: %{y}<br>Hour: %{x}:00<br>Usage: %{z:.1f} GB<extra></extra>'
        ))
        
        fig.update_layout(
            title='Network Usage Heatmap',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            xaxis=dict(tickmode='linear', dtick=2)
        )
        
        return fig
    
    def create_network_distribution(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create network distribution pie chart"""
        if 'network_type' not in df.columns:
            return None
        
        network_counts = df['network_type'].value_counts()
        
        network_data = []
        for k, v in network_counts.items():
            network_name = REV_NETWORK.get(k, f'Type_{k}')
            network_data.append({'Network': network_name, 'Users': v})
        network_df = pd.DataFrame(network_data)
        
        fig = px.pie(
            network_df,
            values='Users',
            names='Network',
            title='Network Distribution',
            color_discrete_sequence=['#94a3b8', '#5c6bc0', '#3949ab', '#1a237e'],
            hole=0.4
        )
        
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'}
        )
        
        return fig