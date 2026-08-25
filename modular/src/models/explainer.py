"""
Model explainability using SHAP
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

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
        self.background_data = None
        self.is_ready = False
    
    def create_explainer(self, model, X_background: pd.DataFrame) -> bool:
        """
        Create SHAP explainer with background data
        
        Args:
            model: Trained model
            X_background: Background data for SHAP (sample of training data)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import shap
            
            # Prepare background data
            X_background = self.processor.prepare_features(X_background)
            X_background = X_background[EXPECTED_FEATURES]
            
            # Sample background data (max 100 rows for performance)
            if len(X_background) > 100:
                X_background = X_background.sample(n=100, random_state=42)
            
            self.background_data = X_background
            
            # Create TreeExplainer for tree-based models
            self.explainer = shap.TreeExplainer(model)
            self.is_ready = True
            self.logger.info("SHAP explainer created successfully")
            return True
            
        except ImportError:
            self.logger.warning("SHAP not installed. Install with: pip install shap")
            self.is_ready = False
            return False
        except Exception as e:
            self.logger.error(f"Error creating SHAP explainer: {str(e)}")
            self.is_ready = False
            return False
    
    def explain_prediction(self, model, X_input: pd.DataFrame) -> Dict:
        """
        Explain a single prediction
        
        Args:
            model: Trained model
            X_input: Input features for prediction
        
        Returns:
            Dictionary with explanation details
        """
        X_input = self.processor.prepare_features(X_input)
        X_features = X_input[EXPECTED_FEATURES]
        
        # Get prediction
        prediction = model.predict(X_features)[0]
        
        # Get SHAP values if available
        shap_values = None
        expected_value = None
        
        if self.explainer is not None and self.is_ready:
            try:
                shap_values = self.explainer.shap_values(X_features)
                expected_value = self.explainer.expected_value
            except Exception as e:
                self.logger.error(f"Error computing SHAP values: {str(e)}")
        
        # Calculate feature impacts
        feature_impacts = {}
        if shap_values is not None and len(shap_values) > 0:
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # Multi-output model (e.g., classification)
                shap_vals = shap_values[0][0] if len(shap_values[0]) > 0 else []
            elif len(shap_values.shape) > 1:
                shap_vals = shap_values[0]
            else:
                shap_vals = shap_values
            
            # Ensure we have the right number of values
            n_features = min(len(shap_vals), len(EXPECTED_FEATURES))
            for i in range(n_features):
                feature_impacts[EXPECTED_FEATURES[i]] = float(shap_vals[i])
        
        # Generate explanation
        explanation = {
            'prediction': float(prediction),
            'base_value': float(expected_value) if expected_value is not None else None,
            'feature_impacts': feature_impacts,
            'feature_names': EXPECTED_FEATURES,
            'shap_values': shap_values.tolist() if shap_values is not None else None,
            'has_shap': shap_values is not None
        }
        
        # Add top contributing features
        if feature_impacts:
            sorted_impacts = sorted(
                feature_impacts.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            explanation['top_positive'] = [
                {'feature': f, 'impact': v} 
                for f, v in sorted_impacts if v > 0
            ][:5]
            explanation['top_negative'] = [
                {'feature': f, 'impact': v} 
                for f, v in sorted_impacts if v < 0
            ][:5]
        
        return explanation
    
    def plot_waterfall(self, explanation: Dict) -> Optional[go.Figure]:
        """
        Create a waterfall plot showing feature contributions
        
        Args:
            explanation: Dictionary from explain_prediction
        
        Returns:
            Plotly figure or None
        """
        if not explanation.get('feature_impacts'):
            return None
        
        impacts = explanation['feature_impacts']
        base_value = explanation.get('base_value', 0)
        prediction = explanation['prediction']
        
        if not impacts:
            return None
        
        # Sort features by absolute impact
        sorted_features = sorted(impacts.items(), key=lambda x: abs(x[1]), reverse=True)
        
        # Take top 8 features to keep plot readable
        top_features = sorted_features[:8]
        feature_names = [f.replace('_', ' ').title() for f, _ in top_features]
        impact_values = [v for _, v in top_features]
        
        # Create waterfall chart
        fig = go.Figure()
        
        # Add bars for each feature
        colors = ['#22c55e' if v > 0 else '#ef4444' for v in impact_values]
        
        # Create measure list: all relative except last (total)
        measure = ["relative"] * len(impact_values) + ["total"]
        
        # Calculate running total
        running_total = base_value
        x_values = []
        for v in impact_values:
            running_total += v
            x_values.append(running_total)
        
        fig.add_trace(go.Waterfall(
            name="Feature Contributions",
            orientation="h",
            measure=measure,
            x=impact_values + [prediction - base_value],
            y=feature_names + ["<b>Prediction</b>"],
            text=[f"{v:+.2f}" for v in impact_values] + [f"{prediction:.2f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#22c55e"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#1a237e"}},
        ))
        
        # Add base value line
        fig.add_vline(
            x=base_value,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Base: {base_value:.2f} GB",
            annotation_position="top left"
        )
        
        fig.update_layout(
            title="Prediction Explanation (Waterfall Plot)",
            xaxis_title="Data Usage (GB)",
            yaxis_title="Features",
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'},
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        return fig
    
    def plot_feature_importance(self, model) -> Optional[go.Figure]:
        """Plot feature importance from the model"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_df = pd.DataFrame({
                'Feature': EXPECTED_FEATURES[:len(importance)],
                'Importance': importance[:len(EXPECTED_FEATURES)]
            }).sort_values('Importance', ascending=True)
            
            # Clean feature names for display
            feature_df['Display Name'] = feature_df['Feature'].str.replace('_', ' ').str.title()
            
            fig = go.Figure(go.Bar(
                x=feature_df['Importance'],
                y=feature_df['Display Name'],
                orientation='h',
                marker_color=feature_df['Importance'],
                marker_colorscale='Blues',
                text=feature_df['Importance'].apply(lambda x: f'{x:.3f}'),
                textposition='outside'
            ))
            
            fig.update_layout(
                title='Model Feature Importance',
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
        if not self.is_ready or self.explainer is None:
            self.logger.warning("SHAP explainer not ready")
            return None
        
        try:
            import shap
            
            X_sample = self.processor.prepare_features(X_sample)
            X_features = X_sample[EXPECTED_FEATURES]
            
            # Limit sample size for performance
            if len(X_features) > 100:
                X_features = X_features.sample(n=100, random_state=42)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(X_features)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                shap_vals = shap_values[0]
            else:
                shap_vals = shap_values
            
            # Compute mean absolute SHAP values for each feature
            if len(shap_vals.shape) > 1:
                mean_abs_shap = np.abs(shap_vals).mean(axis=0)
            else:
                mean_abs_shap = np.abs(shap_vals).mean(axis=0)
            
            feature_importance = pd.DataFrame({
                'Feature': EXPECTED_FEATURES[:len(mean_abs_shap)],
                'Mean_SHAP': mean_abs_shap
            }).sort_values('Mean_SHAP', ascending=True)
            
            # Clean feature names
            feature_importance['Display Name'] = feature_importance['Feature'].str.replace('_', ' ').str.title()
            
            fig = go.Figure(go.Bar(
                x=feature_importance['Mean_SHAP'],
                y=feature_importance['Display Name'],
                orientation='h',
                marker_color=feature_importance['Mean_SHAP'],
                marker_colorscale='Viridis',
                text=feature_importance['Mean_SHAP'].apply(lambda x: f'{x:.3f}'),
                textposition='outside'
            ))
            
            fig.update_layout(
                title='SHAP Feature Importance (Mean |SHAP Value|)',
                xaxis_title='Mean |SHAP Value|',
                yaxis_title='Features',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter, sans-serif'}
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating SHAP summary: {str(e)}")
            return None
    
    def get_explanation_summary(self, explanation: Dict) -> Dict:
        """Get a human-readable summary of the explanation"""
        if not explanation or not explanation.get('feature_impacts'):
            return {'summary': 'No explanation available'}
        
        impacts = explanation['feature_impacts']
        sorted_impacts = sorted(impacts.items(), key=lambda x: abs(x[1]), reverse=True)
        
        # Top positive and negative features
        positive = [f for f, v in sorted_impacts if v > 0][:3]
        negative = [f for f, v in sorted_impacts if v < 0][:3]
        
        # Clean feature names
        positive_clean = [f.replace('_', ' ').title() for f in positive]
        negative_clean = [f.replace('_', ' ').title() for f in negative]
        
        # Generate summary text
        summary_parts = []
        
        if positive:
            summary_parts.append(f"Main drivers: {', '.join(positive_clean)}")
        if negative:
            summary_parts.append(f"Reducing factors: {', '.join(negative_clean)}")
        
        # Add prediction context
        pred = explanation.get('prediction', 0)
        if pred < 2:
            context = "Low usage expected"
        elif pred < 5:
            context = "Medium usage expected"
        else:
            context = "High usage expected"
        summary_parts.append(context)
        
        return {
            'summary': ' | '.join(summary_parts),
            'positive_features': positive_clean,
            'negative_features': negative_clean,
            'prediction_context': context,
            'prediction': pred
        }