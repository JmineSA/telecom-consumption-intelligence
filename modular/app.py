"""
Telecom Consumption Intelligence Platform - Modular Entry Point
"""

import streamlit as st

# Import modular components
from src.config import CONFIG
from src.ui.styling import load_css
from src.ui.sidebar import render_sidebar
from src.ui.tabs import render_tabs
from src.data.loader import DataLoader
from src.models.manager import ModelManager
from src.analytics.metrics import MetricsCalculator
from src.utils.logger import get_logger


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
    """Initialize session state variables."""

    defaults = {
        "prediction_history": [],
        "total_predictions": 0,
        "scenario_results": {},
        "model_loaded": False,
        "prediction_latency": [],
        "uploaded_data": None,
        "data_hash": None,
        "data_source": "none",
        "current_metrics": {},
        "data_loaded": False,
        "first_visit": True
    }

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


init_session_state()


# Load data
def load_data():
    """Load data from uploaded or default source."""

    if st.session_state.uploaded_data is not None:
        st.session_state.data_source = "uploaded"
        st.session_state.data_loaded = True
        return st.session_state.uploaded_data.copy()

    default_df = data_loader.load_default_data()

    if default_df is not None:
        st.session_state.data_source = "default"
        st.session_state.data_loaded = True
        return default_df

    st.session_state.data_source = "none"
    st.session_state.data_loaded = False

    return None


# Load data and calculate metrics
train_df = load_data()

if train_df is not None:
    st.session_state.data_hash = data_loader.get_data_hash(train_df)

    st.session_state.current_metrics = (
        metrics_calculator.calculate_all_metrics(train_df)
    )


# Load model
model_info = (
    model_manager.load(train_df)
    if train_df is not None
    else None
)


# If no model and we have data, use demo model
if model_info is None and train_df is not None:

    from sklearn.ensemble import GradientBoostingRegressor
    import numpy as np

    demo_model = GradientBoostingRegressor(
        n_estimators=50,
        random_state=42
    )

    X_demo = np.random.randn(100, 13)
    y_demo = np.random.randn(100) * 3 + 4

    demo_model.fit(X_demo, y_demo)

    model_info = {
        "model": demo_model,
        "performance": {
            "r2_score": "N/A",
            "rmse": "N/A",
            "mae": "N/A"
        },
        "is_real": False
    }

    st.info(
        "ℹ️ Using demonstration model. "
        "Train the real model for accurate predictions."
    )


# Render sidebar
with st.sidebar:
    render_sidebar(train_df, model_info)


# Render main content
if st.session_state.data_loaded:

    render_tabs(train_df, model_info)

else:

    from src.ui.components import UIComponents

    UIComponents.no_data_message(
        icon="📊",
        title="Welcome to Telecom Intelligence",
        description=(
            "Upload your dataset to unlock powerful "
            "consumption analytics and predictions."
        )
    )


# Footer
st.markdown(
    """
    <div class="app-footer">
        <strong>Telecom Consumption Intelligence</strong>
        · v3.0 · Built with Streamlit
        <br>
        <span style="color: #94a3b8;">
            Data → Analysis → ML → Prediction → Business Decision
        </span>
    </div>
    """,
    unsafe_allow_html=True
)