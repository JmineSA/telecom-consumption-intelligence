"""
Model validation utilities including cross-validation
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from sklearn.model_selection import cross_val_score, cross_val_predict, KFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ..config import CONFIG
from ..constants import EXPECTED_FEATURES
from ..data.processor import DataProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelValidator:
    """Model validation and cross-validation utilities"""
    
    def __init__(self):
        self.config = CONFIG.model
        self.processor = DataProcessor()
        self.logger = logger
    
    def cross_validate(self, model, df: pd.DataFrame, 
                       cv_folds: int = 5, 
                       scoring: str = 'r2') -> Dict:
        """
        Perform cross-validation on the model
        
        Args:
            model: Trained model
            df: DataFrame with data
            cv_folds: Number of folds
            scoring: Scoring metric
        
        Returns:
            Dictionary with cross-validation results
        """
        try:
            # Prepare data
            df = self.processor.prepare_features(df)
            X = df[EXPECTED_FEATURES]
            y = df[self.config.target_column]
            
            # Perform cross-validation
            cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
            cv_predictions = cross_val_predict(model, X, y, cv=cv_folds)
            
            # Calculate metrics on predictions
            r2 = r2_score(y, cv_predictions)
            rmse = np.sqrt(mean_squared_error(y, cv_predictions))
            mae = mean_absolute_error(y, cv_predictions)
            
            results = {
                'cv_folds': cv_folds,
                'scoring': scoring,
                'cv_scores': cv_scores.tolist(),
                'mean_score': float(np.mean(cv_scores)),
                'std_score': float(np.std(cv_scores)),
                'min_score': float(np.min(cv_scores)),
                'max_score': float(np.max(cv_scores)),
                'predictions': cv_predictions.tolist(),
                'actual': y.tolist(),
                'r2': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'n_samples': len(y)
            }
            
            self.logger.info(f"Cross-validation completed: Mean {scoring} = {results['mean_score']:.4f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in cross-validation: {str(e)}")
            return {'error': str(e)}
    
    def plot_cv_results(self, cv_results: Dict) -> go.Figure:
        """Plot cross-validation results"""
        if 'error' in cv_results:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Unable to plot validation results: {cv_results['error']}",
                x=0.5,
                y=0.5,
                xref='paper',
                yref='paper',
                showarrow=False
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            return fig
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CV Scores by Fold', 'Score Distribution',
                           'Actual vs Predicted', 'Residuals Plot')
        )
        
        # CV Scores by Fold
        fig.add_trace(
            go.Bar(
                x=list(range(1, cv_results['cv_folds'] + 1)),
                y=cv_results['cv_scores'],
                name='CV Scores',
                marker_color='#3949ab',
                text=cv_results['cv_scores'],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # Score Distribution
        fig.add_trace(
            go.Histogram(
                x=cv_results['cv_scores'],
                name='Score Distribution',
                marker_color='#5c6bc0'
            ),
            row=1, col=2
        )
        
        # Actual vs Predicted
        fig.add_trace(
            go.Scatter(
                x=cv_results['actual'],
                y=cv_results['predictions'],
                mode='markers',
                name='Predictions',
                marker=dict(color='#3949ab', size=8, opacity=0.6)
            ),
            row=2, col=1
        )
        
        # Perfect prediction line
        max_val = max(max(cv_results['actual']), max(cv_results['predictions']))
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='Perfect Prediction',
                line=dict(color='#e65100', dash='dash')
            ),
            row=2, col=1
        )
        
        # Residuals
        residuals = np.array(cv_results['actual']) - np.array(cv_results['predictions'])
        fig.add_trace(
            go.Scatter(
                x=cv_results['predictions'],
                y=residuals,
                mode='markers',
                name='Residuals',
                marker=dict(color='#eab308', size=8, opacity=0.6)
            ),
            row=2, col=2
        )
        
        # Zero line for residuals
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=2)
        
        fig.update_layout(
            height=600,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'}
        )
        
        fig.update_xaxes(title_text="Fold", row=1, col=1)
        fig.update_xaxes(title_text="Score", row=1, col=2)
        fig.update_xaxes(title_text="Actual", row=2, col=1)
        fig.update_xaxes(title_text="Predicted", row=2, col=2)
        
        fig.update_yaxes(title_text="Score", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        fig.update_yaxes(title_text="Predicted", row=2, col=1)
        fig.update_yaxes(title_text="Residual", row=2, col=2)
        
        return fig