"""
Model visualizations
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional

from ..constants import EXPECTED_FEATURES
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelVisualizations:
    """Model visualizations"""
    
    def create_feature_importance(self, model) -> Optional[go.Figure]:
        """Create feature importance chart"""
        if not hasattr(model, 'feature_importances_'):
            return None
        
        importance = model.feature_importances_
        feature_df = pd.DataFrame({
            'Feature': EXPECTED_FEATURES[:len(importance)],
            'Importance': importance[:len(EXPECTED_FEATURES)]
        }).sort_values('Importance', ascending=False)
        
        fig = px.bar(
            feature_df.head(10),
            x='Importance',
            y='Feature',
            orientation='h',
            title='Top 10 Feature Importance',
            color='Importance',
            color_continuous_scale='Blues',
            text=feature_df.head(10)['Importance'].apply(lambda x: f'{x:.3f}')
        )
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            xaxis_title='Importance Score',
            yaxis_title=''
        )
        fig.update_traces(textposition='outside')
        
        return fig
    
    def create_actual_vs_predicted(self, y_actual, y_pred) -> Optional[go.Figure]:
        """Create actual vs predicted scatter plot"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=y_actual,
            y=y_pred,
            mode='markers',
            marker=dict(
                size=8,
                color=y_pred - y_actual,
                colorscale='RdBu',
                showscale=True,
                colorbar=dict(title='Residual'),
                line=dict(width=0.5, color='white')
            ),
            text=[f"Actual: {a:.2f} GB<br>Predicted: {p:.2f} GB" for a, p in zip(y_actual, y_pred)],
            hoverinfo='text'
        ))
        
        max_val = max(y_actual.max(), y_pred.max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Perfect Prediction',
            line=dict(color='#e65100', width=2, dash='dash'),
            showlegend=True
        ))
        
        fig.update_layout(
            title='Actual vs Predicted Usage',
            xaxis_title='Actual Usage (GB)',
            yaxis_title='Predicted Usage (GB)',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'}
        )
        
        return fig
    
    def create_gauge_chart(self, value: float, title: str, 
                          max_val: float = 10) -> go.Figure:
        """Create gauge chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title, 'font': {'size': 14, 'color': '#64748b'}},
            delta={'reference': max_val/2, 'increasing': {'color': '#22c55e'}, 
                   'decreasing': {'color': '#ef4444'}},
            gauge={
                'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#1a237e"},
                'bgcolor': "white",
                'borderwidth': 0,
                'bordercolor': "white",
                'steps': [
                    {'range': [0, max_val*0.4], 'color': '#dcfce7'},
                    {'range': [max_val*0.4, max_val*0.7], 'color': '#fef3c7'},
                    {'range': [max_val*0.7, max_val], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_val*0.8
                }
            }
        ))
        
        fig.update_layout(
            height=200,
            font={'family': 'Inter, sans-serif'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig