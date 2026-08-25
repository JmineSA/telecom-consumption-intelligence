"""
Telecom Consumption Intelligence Platform - Modular Entry Point
"""
import streamlit as st
import sys
import os
import pandas as pd
from typing import Optional

# ============================================================================
# FIX: Set up paths correctly
# ============================================================================
# Get the absolute path to the modular directory
MODULAR_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (telecom-consumption-intelligence)
PARENT_DIR = os.path.dirname(MODULAR_DIR)

# Add both to path - this ensures Python can find all modules
if MODULAR_DIR not in sys.path:
    sys.path.insert(0, MODULAR_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# ============================================================================
# Import modular components
# ============================================================================
try:
    from src.config import CONFIG
    from src.ui.styling import load_css
    from src.ui.sidebar import render_sidebar
    from src.ui.tabs import render_tabs
    from src.data.loader import DataLoader
    from src.models.manager import ModelManager
    from src.models.explainer import ModelExplainer
    from src.analytics.metrics import MetricsCalculator
    from src.utils.logger import get_logger
except ModuleNotFoundError as e:
    # Print helpful error message
    st.error(f"❌ Import Error: {e}")
    st.error(f"Current directory: {MODULAR_DIR}")
    st.error(f"Parent directory: {PARENT_DIR}")
    st.error("Make sure the 'src' folder exists in the modular directory.")
    st.stop()

# Initialize
logger = get_logger(__name__)
data_loader = DataLoader()
model_manager = ModelManager()
metrics_calculator = MetricsCalculator()

# Page config
st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_css()

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'prediction_history': [],
        'total_predictions': 0,
        'scenario_results': {},
        'model_loaded': False,
        'prediction_latency': [],
        'uploaded_data': None,
        'data_hash': None,
        'data_source': 'none',
        'current_metrics': {},
        'data_loaded': False,
        'first_visit': True,
        'dark_mode': False,
        'explainer_ready': False,
        'explanation': None,
        'show_explanation': False
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

init_session_state()


@st.cache_data(ttl=3600)
def load_default_data_cached() -> Optional[pd.DataFrame]:
    """Cached function to load default data"""
    loader = DataLoader()
    return loader.load_default_data()


# Load data
def load_data():
    """Load data from uploaded or default source"""
    if st.session_state.uploaded_data is not None:
        st.session_state.data_source = 'uploaded'
        st.session_state.data_loaded = True
        return st.session_state.uploaded_data.copy()
    
    default_df = load_default_data_cached()
    if default_df is not None:
        st.session_state.data_source = 'default'
        st.session_state.data_loaded = True
        return default_df
    
    st.session_state.data_source = 'none'
    st.session_state.data_loaded = False
    return None


# Load data and calculate metrics
train_df = load_data()
if train_df is not None:
    st.session_state.data_hash = data_loader.get_data_hash(train_df)
    st.session_state.current_metrics = metrics_calculator.calculate_all_metrics(train_df)

# Load model
model_info = model_manager.load(train_df) if train_df is not None else None

# Create SHAP explainer if model and data are available
if model_info is not None and train_df is not None:
    try:
        explainer = ModelExplainer()
        success = explainer.create_explainer(model_info['model'], train_df)
        st.session_state.explainer_ready = success
        st.session_state.explainer = explainer
        logger.info(f"SHAP explainer created: {success}")
    except Exception as e:
        logger.error(f"Error creating SHAP explainer: {str(e)}")
        st.session_state.explainer_ready = False
else:
    st.session_state.explainer_ready = False

# If no model and we have data, use demo model
if model_info is None and train_df is not None:
    from sklearn.ensemble import GradientBoostingRegressor
    import numpy as np
    demo_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
    X_demo = np.random.randn(100, 13)
    y_demo = np.random.randn(100) * 3 + 4
    demo_model.fit(X_demo, y_demo)
    model_info = {
        'model': demo_model,
        'performance': {'r2_score': 'N/A', 'rmse': 'N/A', 'mae': 'N/A'},
        'is_real': False
    }
    st.info("ℹ️ Using demonstration model. Train the real model for accurate predictions.")

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    render_sidebar(train_df, model_info)

# ============================================================================
# MAIN CONTENT
# ============================================================================
if st.session_state.data_loaded:
    render_tabs(train_df, model_info)
else:
    from src.ui.components import UIComponents
    UIComponents.no_data_message(
        icon="📊",
        title="Welcome to Telecom Intelligence",
        description="Upload your dataset to unlock powerful consumption analytics and predictions."
    )

# Footer
st.markdown("""
<div class="app-footer">
    <strong>Telecom Consumption Intelligence</strong> · v3.0 · Built with Streamlit
    <br>
    <span style="color: #94a3b8;">Data → Analysis → ML → Prediction → Business Decision</span>
</div>
""", unsafe_allow_html=True)