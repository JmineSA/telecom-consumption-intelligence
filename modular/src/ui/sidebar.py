"""
Sidebar components and user profile
"""
import streamlit as st
import pandas as pd
from typing import Optional, Tuple, Dict, Any

from ..constants import AGE_MAPPING, PLAN_MAPPING, NETWORK_MAPPING
from .components import UIComponents  # ← FIXED: Use .components
from ..data.loader import DataLoader
from ..data.validator import DataValidator
from ..data.processor import DataProcessor
from ..models.manager import ModelManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


def render_sidebar(train_df: Optional[pd.DataFrame], 
                   model_info: Optional[Dict[str, Any]]):
    """Render the sidebar"""
    
    # ========== DARK MODE TOGGLE ==========
    st.markdown("### 🎨 Theme")
    dark_mode = st.toggle(
        "🌙 Dark Mode", 
        value=st.session_state.get('dark_mode', False),
        key="dark_mode_toggle"
    )
    if dark_mode != st.session_state.get('dark_mode', False):
        st.session_state.dark_mode = dark_mode
        st.rerun()
    st.markdown("---")
    # ========== END DARK MODE ==========
    
    # Logo and header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem; background: linear-gradient(135deg, #1a237e, #3949ab); 
                    width: 70px; height: 70px; line-height: 70px; border-radius: 20px; 
                    margin: 0 auto; color: white; box-shadow: 0 8px 24px rgba(26,35,126,0.25);">
            📊
        </div>
        <div style="color: #94a3b8; font-size: 0.6rem; margin-top: 0.5rem; letter-spacing: 0.5px; font-weight: 600;">
            TELECOM INTELLIGENCE ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data management
    st.markdown('<div style="font-size: 0.7rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 0.5rem;">📤 Data Management</div>', unsafe_allow_html=True)
    
    render_data_upload()
    
    # Show current dataset info
    if st.session_state.data_loaded:
        render_dataset_info(train_df)
    
    st.markdown("---")
    
    # User profile (only if data is loaded)
    if st.session_state.data_loaded:
        render_user_profile()
        
        st.markdown("---")
        
        # Total predictions counter
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem;">
            <div style="color: #94a3b8; font-size: 0.6rem; font-weight: 600; letter-spacing: 0.5px;">TOTAL PREDICTIONS</div>
            <div style="color: #0f172a; font-size: 2rem; font-weight: 800;">{st.session_state.total_predictions}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Model management
        st.markdown('<div style="font-size: 0.7rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 0.5rem;">🔧 Model Management</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Retrain Model", use_container_width=True):
            with st.spinner("Training model..."):
                try:
                    from ..data.loader import DataLoader
                    from ..models.manager import ModelManager
                    
                    loader = DataLoader()
                    manager = ModelManager()
                    
                    current_df = loader.load_default_data()
                    if current_df is not None:
                        model, perf = manager.train(current_df)
                        st.success(f"✅ Retrained! R²: {perf.get('r2_score', 'N/A'):.4f}")
                        st.rerun()
                    else:
                        st.error("❌ No data available!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0; color: #94a3b8;">
            <div style="font-size: 3rem;">📤</div>
            <p style="font-weight: 500;">Upload data to begin</p>
        </div>
        """, unsafe_allow_html=True)


def render_data_upload():
    """Render data upload section"""
    with st.expander("📂 Upload Dataset", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'parquet'],
            key="data_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                loader = DataLoader()
                validator = DataValidator()
                processor = DataProcessor()
                
                # Validate
                validator.validate_file_size(uploaded_file.size)
                validator.validate_format(uploaded_file.name)
                
                # Load
                uploaded_df = loader.load_uploaded_data(uploaded_file)
                st.success(f"✅ {len(uploaded_df):,} rows loaded")
                
                with st.expander("📋 Preview"):
                    st.dataframe(loader.get_sample_data(uploaded_df))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Use Data", use_container_width=True):
                        with st.spinner("Processing..."):
                            try:
                                # Process data
                                processed_df = processor.create_target(uploaded_df)
                                processed_df = processor.prepare_features(processed_df)
                                
                                # Store in session state
                                st.session_state.uploaded_data = processed_df
                                st.session_state.data_hash = loader.get_data_hash(processed_df)
                                st.session_state.data_source = 'uploaded'
                                st.session_state.data_loaded = True
                                
                                # Calculate metrics
                                from ..analytics.metrics import MetricsCalculator
                                calc = MetricsCalculator()
                                st.session_state.current_metrics = calc.calculate_all_metrics(processed_df)
                                
                                st.success("✅ Data loaded!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error processing data: {str(e)}")
                
                with col2:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state.uploaded_data = None
                        st.session_state.data_hash = None
                        st.session_state.data_source = 'none'
                        st.session_state.data_loaded = False
                        st.session_state.current_metrics = {}
                        st.success("✅ Cleared!")
                        st.rerun()
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_dataset_info(df: Optional[pd.DataFrame]):
    """Show dataset information"""
    if df is None:
        return
    
    source = st.session_state.data_source
    hash_val = st.session_state.data_hash or 'N/A'
    
    if source == 'uploaded':
        st.markdown(f"""
        <div style="background: #f0fdf4; border-radius: 12px; padding: 0.8rem; border: 1px solid #86efac; margin: 0.5rem 0;">
            <div style="font-weight: 600; color: #16a34a; font-size: 0.8rem;">✅ Active Dataset</div>
            <div style="color: #64748b; font-size: 0.75rem;">
                {len(df):,} rows · {hash_val}
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif source == 'default':
        st.markdown(f"""
        <div style="background: #dbeafe; border-radius: 12px; padding: 0.8rem; border: 1px solid #93c5fd; margin: 0.5rem 0;">
            <div style="font-weight: 600; color: #2563eb; font-size: 0.8rem;">📁 Default Dataset</div>
            <div style="color: #64748b; font-size: 0.75rem;">
                {len(df):,} rows · {hash_val}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_user_profile():
    """Render user profile section with sliders"""
    # This is handled in the sidebar directly now
    pass


def get_user_profile() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Get user profile from sidebar inputs"""
    
    st.markdown('<div style="font-size: 0.7rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 0.5rem;">👤 User Profile</div>', unsafe_allow_html=True)
    
    age_group = st.selectbox("Age Group", list(AGE_MAPPING.keys()), key="age")
    plan_type = st.selectbox("Plan Type", list(PLAN_MAPPING.keys()), key="plan")
    network_type = st.selectbox("Network", list(NETWORK_MAPPING.keys()), key="network")
    device_type = st.selectbox("Device", ['Basic_Phone', 'Mid_Range', 'Premium_Smartphone', 'Tablet'], key="device")
    
    st.markdown('<div style="font-size: 0.7rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 0.5rem;">⏰ Usage Hours</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        hours_streaming = st.slider("Streaming", 0.0, 24.0, 2.0, 0.5, key="stream")
        hours_social = st.slider("Social", 0.0, 24.0, 3.0, 0.5, key="social")
    with col2:
        hours_messaging = st.slider("Messaging", 0.0, 24.0, 1.0, 0.5, key="msg")
        hours_gaming = st.slider("Gaming", 0.0, 24.0, 1.0, 0.5, key="game")
    
    st.markdown('<div style="font-size: 0.7rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 0.5rem;">🔄 Patterns</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        is_peak_hour_user = st.selectbox("Peak User", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No", key="peak")
    with col2:
        is_weekend = st.selectbox("Weekend", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No", key="weekend")
    
    # Create DataFrame
    data = {
        'age_group': [AGE_MAPPING[age_group]],
        'plan_type': [PLAN_MAPPING[plan_type]],
        'network_type': [NETWORK_MAPPING[network_type]],
        'device_type_Basic_Phone': [1 if device_type == 'Basic_Phone' else 0],
        'device_type_Mid_Range': [1 if device_type == 'Mid_Range' else 0],
        'device_type_Premium_Smartphone': [1 if device_type == 'Premium_Smartphone' else 0],
        'device_type_Tablet': [1 if device_type == 'Tablet' else 0],
        'hours_streaming': [hours_streaming],
        'hours_social': [hours_social],
        'hours_messaging': [hours_messaging],
        'hours_gaming': [hours_gaming],
        'is_peak_hour_user': [is_peak_hour_user],
        'is_weekend': [is_weekend]
    }
    
    input_dict = {
        'age_group': age_group, 
        'plan_type': plan_type, 
        'network_type': network_type,
        'device_type': device_type, 
        'hours_streaming': hours_streaming,
        'hours_social': hours_social, 
        'hours_messaging': hours_messaging,
        'hours_gaming': hours_gaming, 
        'is_peak_hour_user': is_peak_hour_user,
        'is_weekend': is_weekend
    }
    
    return pd.DataFrame(data), input_dict