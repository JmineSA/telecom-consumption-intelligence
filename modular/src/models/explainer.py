"""
Model explainability using SHAP
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px

from ..constants import EXPECTED_FEATURES
from ..data.processor import DataProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelExplainer:
    """Explain model predictions using SHAP values"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.logger = logger
        self.explainer = None
        self.shap_values = None
    
    def create_explainer(self, model, X_train: pd.DataFrame):
        """Create SHAP explainer"""
        try:
            import shap
            self.explainer = shap.TreeExplainer(model)
            self.shap_values = self.explainer.shap_values(X_train)
            self.logger.info("SHAP explainer created successfully")
            return True
        except ImportError:
            self.logger.warning("SHAP not installed. Install with: pip install shap")
            return False
        except Exception as e:
            self.logger.error(f"Error creating SHAP explainer: {str(e)}")
            return False
    
    def explain_prediction(self, model, X_input: pd.DataFrame) -> Dict:
        """Explain a single prediction"""
        X_input = self.processor.prepare_features(X_input)
        X_features = X_input[EXPECTED_FEATURES]
        
        # Get prediction
        prediction = model.predict(X_features)[0]
        
        # Get SHAP values if available
        shap_values = None
        if self.explainer is not None:
            shap_values = self.explainer.shap_values(X_features)
        
        # Generate explanation
        explanation = {
            'prediction': float(prediction),
            'base_value': float(self.explainer.expected_value) if self.explainer else None,
            'shap_values': shap_values.tolist() if shap_values is not None else None,
            'features': X_features.iloc[0].to_dict(),
            'feature_names': EXPECTED_FEATURES
        }
        
        return explanation
    
    def plot_feature_importance(self, model) -> go.Figure:
        """Plot feature importance"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_df = pd.DataFrame({
                'Feature': EXPECTED_FEATURES[:len(importance)],
                'Importance': importance[:len(EXPECTED_FEATURES)]
            }).sort_values('Importance', ascending=True)
            
            fig = go.Figure(go.Bar(
                x=feature_df['Importance'],
                y=feature_df['Feature'],
                orientation='h',
                marker_color=feature_df['Importance'],
                marker_colorscale='Blues',
                text=feature_df['Importance'].apply(lambda x: f'{x:.3f}'),
                textposition='outside'
            ))
            
            fig.update_layout(
                title='Feature Importance',
                xaxis_title='Importance Score',
                yaxis_title='Features',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter, sans-serif'}
            )
            
            return fig
        
        return None
    
    def plot_shap_summary(self, model, X_sample: pd.DataFrame) -> Optional[go.Figure]:
        """Create SHAP summary plot"""
        if self.explainer is None or self.shap_values is None:
            self.logger.warning("SHAP explainer not created")
            return None
        
        try:
            import shap
            
            # Get SHAP values for sample
            X_sample = self.processor.prepare_features(X_sample)
            X_features = X_sample[EXPECTED_FEATURES]
            
            shap_values_sample = self.explainer.shap_values(X_features)
            
            # Create summary plot
            plt = shap.summary_plot(
                shap_values_sample, 
                X_features,
                show=False,
                max_display=10
            )
            
            # Convert to Plotly
            fig = go.Figure()
            # Note: This is simplified - actual conversion is more complex
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating SHAP summary: {str(e)}")
            return None