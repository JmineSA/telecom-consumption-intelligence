"""
Telecom Consumption Intelligence Platform — Modular Entry Point
"""
import streamlit as st
import sys
import os
import pandas as pd
from typing import Optional

from src.ui.onboarding import OnboardingWizard
from src.ui.shortcuts import KeyboardShortcuts
from src.utils.report_generator import ReportGenerator

# ============================================================================
# PATHS
# ============================================================================
# ---------------------------------------------------------------------------
# PATHS — must be set before any imports that unpickle src.* modules
# ---------------------------------------------------------------------------
MODULAR_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(MODULAR_DIR)      # repo root

# Repo root first — the trained pickle lives there as `src.*`
for _p in (PARENT_DIR, MODULAR_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

if MODULAR_DIR not in sys.path:
    sys.path.insert(0, MODULAR_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# ============================================================================
# IMPORTS
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
    st.error(f"❌ Import Error: {e}")
    st.error(f"Current directory: {MODULAR_DIR}")
    st.error(f"Parent directory:  {PARENT_DIR}")
    st.error("Make sure the 'src' folder exists in the modular directory.")
    st.stop()

logger = get_logger(__name__)
data_loader = DataLoader()
model_manager = ModelManager()
metrics_calculator = MetricsCalculator()

st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()


# ============================================================================
# SESSION STATE
# ============================================================================
def init_session_state():
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
        "first_visit": True,
        "dark_mode": False,
        "explainer_ready": False,
        "explanation": None,
        "show_explanation": False,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


init_session_state()


# ============================================================================
# DATA
# ============================================================================
@st.cache_data(ttl=3600)
def load_default_data_cached() -> Optional[pd.DataFrame]:
    loader = DataLoader()
    return loader.load_default_data()


def load_data():
    if st.session_state.uploaded_data is not None:
        st.session_state.data_source = "uploaded"
        st.session_state.data_loaded = True
        return st.session_state.uploaded_data.copy()

    default_df = load_default_data_cached()
    if default_df is not None:
        st.session_state.data_source = "default"
        st.session_state.data_loaded = True
        return default_df

    st.session_state.data_source = "none"
    st.session_state.data_loaded = False
    return None


train_df = load_data()
if train_df is not None:
    st.session_state.data_hash = data_loader.get_data_hash(train_df)
    st.session_state.current_metrics = metrics_calculator.calculate_all_metrics(train_df)


# ============================================================================
# MODEL — fail loudly with full traceback
# ============================================================================
model_info = None
if train_df is not None:
    model_info = model_manager.load(train_df)

if model_info is None and train_df is not None:
    st.error("❌ **Trained model not found.** The app cannot make real predictions without it.")

    # Full traceback from manager (this is the new bit that shows the real cause)
    if getattr(model_manager, "last_traceback", None):
        with st.expander("🐛 Exception traceback", expanded=True):
            st.code(model_manager.last_traceback, language="python")
    elif getattr(model_manager, "last_error", None):
        with st.expander("🐛 Error message", expanded=True):
            st.code(model_manager.last_error, language="text")

    expected_path = os.path.join(PARENT_DIR, "models", "mobile_data_consumption_pipeline.pkl")
    expected_meta = os.path.join(PARENT_DIR, "models", "model_info.json")

    with st.expander("🔍 Debug info", expanded=False):
        st.code(f"Working directory  : {os.getcwd()}")
        st.code(f"Modular dir        : {MODULAR_DIR}")
        st.code(f"Parent dir         : {PARENT_DIR}")
        st.code(f"Expected model at  : {expected_path}")
        st.code(f"Model file exists  : {os.path.exists(expected_path)}")
        st.code(f"Metadata file      : {expected_meta} (exists: {os.path.exists(expected_meta)})")

        models_dir = os.path.join(PARENT_DIR, "models")
        if os.path.isdir(models_dir):
            st.write("Files in `models/`:")
            st.code("\n".join(sorted(os.listdir(models_dir))))
        else:
            st.warning("The `models/` folder does not exist next to the app.")

    st.markdown("""
    **Most common cause on Streamlit Cloud:** version mismatch between the
    scikit-learn/joblib used to *save* the pickle and the versions installed on Cloud.

    **Fix:** pin the exact versions in `requirements.txt` at the repo root, then reboot.
    """)
    st.stop()


# ============================================================================
# SHAP EXPLAINER
# ============================================================================
if model_info is not None and train_df is not None:
    try:
        explainer = ModelExplainer()
        success = explainer.create_explainer(model_info["model"], train_df)
        st.session_state.explainer_ready = success
        st.session_state.explainer = explainer
        logger.info(f"SHAP explainer created: {success}")
    except Exception as e:
        logger.error(f"Error creating SHAP explainer: {e}")
        st.session_state.explainer_ready = False
else:
    st.session_state.explainer_ready = False


# ============================================================================
# SIDEBAR + MAIN
# ============================================================================
with st.sidebar:
    render_sidebar(train_df, model_info)

if st.session_state.data_loaded:
    render_tabs(train_df, model_info)
else:
    from src.ui.components import UIComponents
    UIComponents.no_data_message(
        icon="📊",
        title="Welcome to Telecom Intelligence",
        description="Upload your dataset to unlock powerful consumption analytics and predictions.",
    )


st.markdown("""
<div class="app-footer">
    <strong>Telecom Consumption Intelligence</strong> · v3.0 · Built with Streamlit
    <br>
    <span style="color: #94a3b8;">Data → Analysis → ML → Prediction → Business Decision</span>
</div>
""", unsafe_allow_html=True)