"""
Telecom Consumption Intelligence — Streamlit app entry point.

Three pages:
    🏠 Overview  — model summary + key insights
    🎯 Predict   — per-subscriber next-day forecast
    📊 Insights  — charts from reports/insights/
"""
import sys
from pathlib import Path

# Make modular/ importable
MODULAR_DIR = Path(__file__).resolve().parent
if str(MODULAR_DIR) not in sys.path:
    sys.path.insert(0, str(MODULAR_DIR))

import streamlit as st
from src.config import (
    PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT, SIDEBAR_STATE,
)
from src.constants import NAV_ITEMS

# ----- Page config (must be the FIRST Streamlit call) -----
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)

# ----- Lazy imports (after set_page_config) -----
from src.ui.styling import load_css
from src.ui.pages import render_overview, render_predict, render_insights
from src.data.loader import load_test_data, load_model_info
from src.models.manager import ModelManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ----- Load CSS -----
load_css()

# ----- Load model + data -----
@st.cache_resource
def get_model():
    return ModelManager()


@st.cache_data(ttl=3600)
def get_test_data():
    return load_test_data()


@st.cache_data(ttl=3600)
def get_model_info():
    return load_model_info()


model_manager = get_model()
test_df = get_test_data()
model_info = get_model_info()

# ----- Sidebar nav -----
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size:2rem; background: linear-gradient(135deg,#1a237e,#3949ab);
                    width:60px; height:60px; line-height:60px; border-radius:16px;
                    margin:0 auto; color:white;">📶</div>
        <div style="color:#94a3b8; font-size:0.65rem; margin-top:0.5rem;
                    letter-spacing:0.5px; font-weight:600;">
            TELECOM FORECASTING
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        '<div style="font-size:0.65rem; font-weight:700; color:#94a3b8; '
        'letter-spacing:0.8px; text-transform:uppercase; margin-bottom:0.5rem;">'
        'Navigation</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        NAV_ITEMS,
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.markdown("---")

    # Model status footer
    if model_info:
        r2 = model_info.get("val_metrics", {}).get("r2")
        if r2 is not None:
            st.caption(f"**Model:** HistGradientBoosting")
            st.caption(f"**Val R²:** {r2:.4f}")
    st.caption("Synthetic data — demo")

# ----- Route to the selected page -----
if page == NAV_ITEMS[0]:
    render_overview(model_info, test_df)
elif page == NAV_ITEMS[1]:
    render_predict(model_manager, model_info)
elif page == NAV_ITEMS[2]:
    render_insights()