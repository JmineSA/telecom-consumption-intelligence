"""
Three page renderers: Overview, Predict, Insights.
"""
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np

from ..config import (
    INSIGHTS_DIR, BUSINESS_SUMMARY_PATH, TARGET_COLUMN,
    AGE_GROUPS, PLAN_TYPES, NETWORK_TYPES, DEVICE_TYPES,
)
from ..constants import INSIGHT_CHARTS
from ..utils.logger import get_logger
from .components import (
    metric_card, insight_card, section_header, page_header, result_card,
)

logger = get_logger(__name__)


# ======================================================================
# PAGE 1 — OVERVIEW
# ======================================================================
def render_overview(model_info: dict, test_df: pd.DataFrame):
    page_header(
        "🏠 Overview",
        "Forecast of tomorrow's mobile data consumption per subscriber. "
        "Built on synthetic South African telecom data.",
    )

    # ----- KPI row -----
    train_r2 = model_info.get("train_metrics", {}).get("r2")
    val_r2 = model_info.get("val_metrics", {}).get("r2")
    val_mae = model_info.get("val_metrics", {}).get("mae")
    n_features = model_info.get("n_features")
    n_train = model_info.get("n_train_samples")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if val_r2 is not None:
            metric_card("Validation R²", f"{val_r2:.4f}")
    with col2:
        if val_mae is not None:
            metric_card("Validation MAE", f"{val_mae:.2f} GB")
    with col3:
        if n_features is not None:
            metric_card("Features", f"{n_features}")
    with col4:
        if n_train is not None:
            metric_card("Training Rows", f"{n_train:,}")

    # ----- Key insights -----
    section_header("💡 Key Insights", "What the model found")

    c1, c2 = st.columns(2)
    with c1:
        insight_card(
            "Rolling averages dominate",
            "The target correlates more strongly with 30-day rolling averages "
            "(0.87) than with yesterday's single value (0.76). The model "
            "correctly weights longer-term behaviour over daily noise.",
            icon="📈",
        )
        insight_card(
            "Leakage-free design",
            "All features use past-only information. Target is tomorrow's usage. "
            "Time-based split, no random shuffling.",
            icon="🔍",
        )
    with c2:
        insight_card(
            "Congestion matters",
            "During network congestion, prediction error rises — usage drops "
            "but the model doesn't fully anticipate it. Real implication for "
            "capacity planning.",
            icon="🌐",
        )
        insight_card(
            "Revenue implications",
            "Under-predicted users = top-up opportunity. Over-predicted users = "
            "possible churn signals or network over-allocation.",
            icon="💰",
        )

    # ----- Business summary -----
    section_header("📄 Business Summary", "Auto-generated from the trained model")

    if BUSINESS_SUMMARY_PATH.exists():
        text = BUSINESS_SUMMARY_PATH.read_text(encoding="utf-8")
        st.code(text, language="text")
    else:
        st.info(
            "Business summary not found. Run the report notebook:\n\n"
            "`jupyter nbconvert --to notebook --execute notebooks/04_final_report.ipynb`"
        )


# ======================================================================
# PAGE 2 — PREDICT
# ======================================================================
def render_predict(model_manager, model_info: dict):
    page_header(
        "🎯 Predict Next-Day Usage",
        "Adjust the profile in the sidebar, then click Predict. "
        "The app derives lag features from the user's typical usage.",
    )

    if not model_manager.is_loaded:
        st.error("❌ Model not loaded.")
        if model_manager.last_traceback:
            with st.expander("🐛 Traceback"):
                st.code(model_manager.last_traceback, language="python")
        return

    # ----- Sidebar form -----
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 User Profile")

        age_group = st.selectbox("Age Group", AGE_GROUPS, key="f_age")
        plan_type = st.selectbox("Plan Type", PLAN_TYPES, key="f_plan")
        network_type = st.selectbox("Network", NETWORK_TYPES, key="f_network")
        device_type = st.selectbox("Device", DEVICE_TYPES, key="f_device")

        st.markdown("### 💰 Account Details")
        customer_tenure_months = st.number_input(
            "Tenure (months)", min_value=1, max_value=120, value=12, key="f_tenure"
        )
        contract_duration_months = st.number_input(
            "Contract duration (months)", min_value=1, max_value=24, value=12, key="f_contract"
        )
        monthly_bill_zar = st.number_input(
            "Monthly bill (ZAR)", min_value=50, max_value=2000, value=400, step=10, key="f_bill"
        )
        support_calls_6months = st.number_input(
            "Support calls (last 6 months)", min_value=0, max_value=20, value=2, key="f_calls"
        )
        churn_probability = st.slider(
            "Churn probability", 0.0, 1.0, 0.20, 0.01, key="f_churn"
        )

        st.markdown("### ⏰ Recent Usage")
        typical_usage_gb = st.slider(
            "Typical daily usage (GB)", 0.5, 20.0, 4.0, 0.5, key="f_usage"
        )
        col1, col2 = st.columns(2)
        with col1:
            hours_streaming = st.slider("Streaming (h/day)", 0.0, 12.0, 2.0, 0.5, key="f_stream")
            hours_social = st.slider("Social (h/day)", 0.0, 12.0, 3.0, 0.5, key="f_social")
        with col2:
            hours_messaging = st.slider("Messaging (h/day)", 0.0, 8.0, 1.0, 0.5, key="f_msg")
            hours_gaming = st.slider("Gaming (h/day)", 0.0, 8.0, 1.0, 0.5, key="f_game")

        st.markdown("### 🔄 Patterns")
        c1, c2 = st.columns(2)
        with c1:
            is_peak = st.selectbox("Peak User", [0, 1],
                                   format_func=lambda x: "Yes" if x else "No",
                                   key="f_peak")
        with c2:
            is_weekend = st.selectbox("Weekend", [0, 1],
                                      format_func=lambda x: "Yes" if x else "No",
                                      key="f_weekend")

        congested = st.selectbox(
            "Network congested?", [0, 1],
            format_func=lambda x: "Yes" if x else "No",
            key="f_congested",
        )

    # ----- Compute derived features -----
    today = pd.Timestamp.today().normalize()
    day_index = max((today - pd.Timestamp("2026-01-01")).days, 1)
    dow = today.dayofweek
    is_weekend_calc = int(dow >= 5)

    # Lag approximations (all based on typical usage)
    lag_1d_total_gb = typical_usage_gb
    lag_7d_total_gb = typical_usage_gb
    rolling_7d_avg_gb = typical_usage_gb
    rolling_30d_avg_gb = typical_usage_gb
    delta_1d_gb = 0.0

    # Service lags as fractions of typical usage
    total_hours = hours_streaming + hours_social + hours_gaming + hours_messaging
    total_hours = max(total_hours, 0.1)
    lag_1d_streaming_gb = typical_usage_gb * (hours_streaming / total_hours)
    lag_1d_social_gb = typical_usage_gb * (hours_social / total_hours)
    lag_1d_gaming_gb = typical_usage_gb * (hours_gaming / total_hours)
    lag_1d_messaging_gb = typical_usage_gb * (hours_messaging / total_hours)

    # ----- Build the input DataFrame with all 34 columns -----
    input_df = pd.DataFrame({
        "measurement_date": [today],
        "age_group": [age_group],
        "plan_type": [plan_type],
        "network_type": [network_type],
        "device_type": [device_type],
        "day_index": [day_index],
        "day_of_week": [dow],
        "is_weekend": [is_weekend],
        "day_of_month": [today.day],
        "congested": [congested],
        "contract_duration_months": [contract_duration_months],
        "customer_tenure_months": [customer_tenure_months],
        "monthly_bill_zar": [monthly_bill_zar],
        "support_calls_6months": [support_calls_6months],
        "churn_probability": [churn_probability],
        "churn_status": [0],
        "lag_1d_total_gb": [lag_1d_total_gb],
        "lag_7d_total_gb": [lag_7d_total_gb],
        "rolling_7d_avg_gb": [rolling_7d_avg_gb],
        "rolling_30d_avg_gb": [rolling_30d_avg_gb],
        "delta_1d_gb": [delta_1d_gb],
        "lag_1d_streaming_gb": [lag_1d_streaming_gb],
        "lag_1d_social_gb": [lag_1d_social_gb],
        "lag_1d_gaming_gb": [lag_1d_gaming_gb],
        "lag_1d_messaging_gb": [lag_1d_messaging_gb],
        "streaming_gb": [0.0],
        "social_gb": [0.0],
        "messaging_gb": [0.0],
        "gaming_gb": [0.0],
        "background_gb": [0.0],
        "total_gb": [0.0],
        "arpu": [0.0],
        "region": ["Gauteng"],
        "is_month_start": [int(today.day <= 3)],
        "is_month_end": [int(today.day >= 28)],
    })

    # ----- Predict -----
    if st.button("🚀 Predict", type="primary", use_container_width=True):
        try:
            pred = model_manager.predict(input_df)[0]

            if pred < 2:
                tag_color, label = "#16a34a", "Low Usage"
            elif pred < 5:
                tag_color, label = "#d97706", "Medium Usage"
            else:
                tag_color, label = "#dc2626", "High Usage"

            result_card(
                value=pred,
                unit="GB",
                label="Predicted usage tomorrow",
                tag=label,
                tag_color=tag_color,
            )

        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            import traceback
            with st.expander("🐛 Traceback"):
                st.code(traceback.format_exc())

    # ----- Input summary -----
    section_header("📋 Input Summary")

    summary = pd.DataFrame({
        "Field": [
            "Age group", "Plan", "Network", "Device",
            "Typical usage", "Congested", "Weekend",
            "Tenure (months)", "Monthly bill (ZAR)",
            "Churn probability",
        ],
        "Value": [
            str(age_group), str(plan_type), str(network_type), str(device_type),
            f"{typical_usage_gb:.1f} GB",
            "Yes" if congested else "No",
            "Yes" if is_weekend else "No",
            str(customer_tenure_months), str(monthly_bill_zar),
            f"{churn_probability:.2f}",
        ],
    })
    st.dataframe(summary, hide_index=True, use_container_width=True)


# ======================================================================
# PAGE 3 — INSIGHTS
# ======================================================================
def render_insights():
    page_header("📊 Insights", "Charts and analysis from the trained model")

    if not INSIGHTS_DIR.exists():
        st.warning(
            f"Insights folder not found: {INSIGHTS_DIR}\n\n"
            "Run `python -m training.models.model_insights` first."
        )
        return

    found_any = False
    for title, filename in INSIGHT_CHARTS:
        path = INSIGHTS_DIR / filename
        if path.exists():
            section_header(f"📈 {title}")
            st.image(str(path), use_container_width=True)
            found_any = True

    if not found_any:
        st.info("No charts found. Run the insights script to generate them.")