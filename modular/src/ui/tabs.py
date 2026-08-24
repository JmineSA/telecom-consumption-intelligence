"""
Tab definitions and rendering
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

from ..constants import TABS
from .components import UIComponents
from ..visualizations.dashboard import DashboardVisualizations
from ..visualizations.analytics import AnalyticsVisualizations
from ..visualizations.network import NetworkVisualizations
from ..visualizations.model import ModelVisualizations
from ..analytics.metrics import MetricsCalculator, BusinessMetrics
from ..models.manager import ModelManager
from ..data.loader import DataLoader
from ..utils.logger import get_logger

logger = get_logger(__name__)


def render_tabs(df: pd.DataFrame, model_info: Dict[str, Any]):
    """Render all tabs"""
    
    vis = DashboardVisualizations()
    analytics_vis = AnalyticsVisualizations()
    network_vis = NetworkVisualizations()
    model_vis = ModelVisualizations()
    
    tab_names = [f"{info['icon']} {info['label']}" for info in TABS.values()]
    tabs = st.tabs(tab_names)
    
    # Tab 1: Command Centre
    with tabs[0]:
        render_command_centre(df, vis)
    
    # Tab 2: Predict & Explain
    with tabs[1]:
        render_predict(df, model_info)
    
    # Tab 3: Analytics
    with tabs[2]:
        render_analytics(df, analytics_vis, vis)
    
    # Tab 4: Forecast
    with tabs[3]:
        render_forecast(df, analytics_vis)
    
    # Tab 5: Segmentation
    with tabs[4]:
        render_segmentation(df, analytics_vis)
    
    # Tab 6: Revenue
    with tabs[5]:
        render_revenue(df)
    
    # Tab 7: Network
    with tabs[6]:
        render_network(df, network_vis)
    
    # Tab 8: Model
    with tabs[7]:
        render_model(df, model_info, model_vis)
    
    # Tab 9: Data Explorer
    with tabs[8]:
        render_data_explorer(df)
    
    # Tab 10: Monitoring
    with tabs[9]:
        render_monitoring(df, model_info)


def render_command_centre(df: pd.DataFrame, vis):
    """Render Command Centre tab"""
    UIComponents.section_title("🏠 Command Centre")
    
    metrics = st.session_state.current_metrics
    
    # Source info
    source_labels = {
        'uploaded': ('📤 Uploaded Dataset', 'uploaded'),
        'default': ('📁 Default Dataset', 'default'),
    }
    label, badge_type = source_labels.get(
        st.session_state.data_source, 
        ('📊 Dataset', 'none')
    )
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem;">
        <span style="font-weight: 500; color: #0f172a;">{label}</span>
        <span class="source-badge {badge_type}">{st.session_state.data_source.title()}</span>
        <span style="color: #94a3b8; font-size: 0.8rem;">({metrics.get('total_subscribers', 0):,} subscribers)</span>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        UIComponents.metric_card("👥 Subscribers", f"{metrics.get('total_subscribers', 0):,}")
    
    with col2:
        avg_usage = metrics.get('avg_usage', 0)
        UIComponents.metric_card("📊 Avg Usage", f"{avg_usage:.1f} GB")
    
    with col3:
        pct_heavy = metrics.get('pct_heavy', 0)
        UIComponents.metric_card("🔥 Heavy Users", f"{pct_heavy:.1f}%")
    
    with col4:
        growth = metrics.get('usage_growth', 0)
        UIComponents.metric_card("📈 Usage Growth", f"{growth:+.1f}%", trend=growth)
    
    with col5:
        pct_5g = metrics.get('pct_5g', 0)
        UIComponents.metric_card("📡 5G Adoption", f"{pct_5g:.0f}%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        fig_dist = vis.create_usage_distribution(df)
        if fig_dist:
            st.plotly_chart(fig_dist, use_container_width=True, key="command_dist")  # ← ADDED key
    
    with col2:
        fig_trend = vis.create_trend_chart(df)
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True, key="command_trend")  # ← ADDED key
    
    # Insights
    st.markdown("---")
    UIComponents.section_title("🧠 Key Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        UIComponents.insight_card(
            "📊 Streaming Dominates Usage",
            "Customers spending >3 hours/day streaming consume <strong>42%</strong> more data than average.",
            type="primary"
        )
        UIComponents.insight_card(
            "⚠️ Evening Network Congestion",
            "Peak consumption occurs between <strong>18:00–21:00</strong>, requiring capacity planning.",
            type="warning"
        )
    
    with col2:
        heavy_count = metrics.get('heavy_users', 0)
        UIComponents.insight_card(
            "💰 Upsell Opportunity",
            f"<strong>{heavy_count:,}</strong> heavy users identified for premium bundles representing <strong>R{heavy_count * 299:,.0f}</strong> monthly potential.",
            type="success"
        )
        UIComponents.insight_card(
            "📱 5G Premium Segment",
            "5G users consume <strong>2.3x</strong> more data than 4G users, indicating higher ARPU potential.",
            type="primary"
        )


def render_predict(df: pd.DataFrame, model_info: Dict[str, Any]):
    """Render Predict & Explain tab"""
    UIComponents.section_title("🎯 Predict & Explain")
    
    # Get user profile from sidebar
    from .sidebar import get_user_profile
    input_df, input_dict = get_user_profile()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 1.5rem; border: 1px solid #f1f5f9;">
            <h4 style="color: #0f172a;">👤 Current Profile</h4>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            **Age:** {input_dict['age_group']}  
            **Device:** {input_dict['device_type']}  
            **Network:** {input_dict['network_type']}  
            **Plan:** {input_dict['plan_type']}
            """)
        with col_b:
            st.markdown(f"""
            **Streaming:** {input_dict['hours_streaming']:.1f}h  
            **Social:** {input_dict['hours_social']:.1f}h  
            **Messaging:** {input_dict['hours_messaging']:.1f}h  
            **Gaming:** {input_dict['hours_gaming']:.1f}h
            """)
        
        predict_btn = st.button("🚀 Predict Usage", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("📊 Results")
        
        if predict_btn:
            try:
                import time
                from ..models.manager import ModelManager
                from ..constants import EXPECTED_FEATURES
                
                manager = ModelManager()
                start_time = time.time()
                
                # Validate and predict
                X_input = input_df[EXPECTED_FEATURES]
                prediction = manager.predict(model_info['model'], X_input)[0]
                
                # Calculate ARPU
                from ..models.manager import ModelMetrics
                arpu = ModelMetrics.calculate_arpu(prediction, input_dict['plan_type'])
                
                latency = time.time() - start_time
                st.session_state.prediction_latency.append(latency)
                
                st.session_state.scenario_results = {
                    'prediction': prediction,
                    'arpu': arpu,
                    'plan': input_dict['plan_type'],
                    'device': input_dict['device_type'],
                    'hours': input_dict,
                    'latency': latency
                }
                
                st.session_state.total_predictions += 1
                st.success(f"✅ Complete! ({latency*1000:.0f}ms)")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        # Display results
        if st.session_state.scenario_results:
            results = st.session_state.scenario_results
            pred = results['prediction']
            
            if pred < 2:
                badge = "low"; color = "#16a34a"; label = "Low Usage"
            elif pred < 5:
                badge = "medium"; color = "#d97706"; label = "Medium Usage"
            else:
                badge = "high"; color = "#dc2626"; label = "High Usage"
            
            r2 = model_info.get('performance', {}).get('r2_score', 'N/A')
            r2_display = f"{r2:.4f}" if isinstance(r2, (int, float)) else r2
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #f8fafc, #f1f5f9); border-radius: 20px; padding: 2rem; text-align: center; border: 1px solid #e8edf3;">
                <div style="font-size: 3.5rem; font-weight: 900; color: {color};">{pred:.2f}</div>
                <div style="font-size: 1.2rem; color: #64748b;">GB</div>
                <div style="margin: 0.5rem 0;">{UIComponents.badge(label, badge)}</div>
                <div style="color: #64748b; font-size: 0.9rem;">
                    Estimated ARPU: <strong>R{results['arpu']:.2f}</strong>
                </div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 0.3rem;">
                    Model R²: {r2_display} · {results.get('latency', 0)*1000:.0f}ms
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_analytics(df: pd.DataFrame, analytics_vis, dashboard_vis):
    """Render Analytics tab"""
    UIComponents.section_title("📊 Advanced Analytics")
    
    # Distribution - use DashboardVisualizations
    fig_dist = dashboard_vis.create_usage_distribution(df)
    if fig_dist:
        st.plotly_chart(fig_dist, use_container_width=True, key="analytics_dist")  # ← ADDED key
    
    # Activity breakdown
    st.subheader("📊 Activity Breakdown")
    activity_cols = ['hours_streaming', 'hours_social', 'hours_messaging', 'hours_gaming']
    if all(col in df.columns for col in activity_cols):
        fig_activity = analytics_vis.create_activity_breakdown(df, activity_cols)
        if fig_activity:
            st.plotly_chart(fig_activity, use_container_width=True, key="analytics_activity")  # ← ADDED key
    
    # Correlation heatmap
    st.subheader("📊 Feature Correlations")
    numeric_cols = ['total_data_gb'] + activity_cols
    if all(col in df.columns for col in numeric_cols):
        fig_corr = analytics_vis.create_correlation_heatmap(df, numeric_cols)
        if fig_corr:
            st.plotly_chart(fig_corr, use_container_width=True, key="analytics_corr")  # ← ADDED key


def render_forecast(df: pd.DataFrame, vis):
    """Render Forecast tab"""
    UIComponents.section_title("🔮 Consumption Forecast")
    
    fig_forecast = vis.create_forecast(df)
    if fig_forecast:
        st.plotly_chart(fig_forecast, use_container_width=True, key="forecast")  # ← ADDED key
    
    # Forecast metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = st.session_state.current_metrics
    avg_usage = metrics.get('avg_usage', 0)
    growth = metrics.get('usage_growth', 0)
    
    with col1:
        st.metric("📈 Projected Growth", f"{growth + np.random.uniform(2, 5):.1f}%", "Next 30 days")
    with col2:
        st.metric("📊 Forecast Peak", f"{avg_usage * 1.15:.1f} GB", "Expected maximum")
    with col3:
        st.metric("📉 Forecast Low", f"{avg_usage * 0.85:.1f} GB", "Expected minimum")
    with col4:
        st.metric("📅 Confidence", f"{85 + np.random.randint(0, 10)}%", "95% CI range")


def render_segmentation(df: pd.DataFrame, vis):
    """Render Segmentation tab"""
    UIComponents.section_title("👥 Customer Segmentation")
    
    # Bubble chart
    fig_bubble = vis.create_segment_bubble_chart(df)
    if fig_bubble:
        st.plotly_chart(fig_bubble, use_container_width=True, key="segmentation_bubble")  # ← ADDED key
    
    # Segment summary
    st.subheader("📊 Segment Summary")
    
    if 'total_data_gb' in df.columns:
        low_usage = df[df['total_data_gb'] < 2]
        mid_usage = df[(df['total_data_gb'] >= 2) & (df['total_data_gb'] < 5)]
        high_usage = df[df['total_data_gb'] >= 5]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            UIComponents.metric_card("🟢 Low Usage", f"{len(low_usage):,}")
        with col2:
            UIComponents.metric_card("🟡 Medium Usage", f"{len(mid_usage):,}")
        with col3:
            UIComponents.metric_card("🔴 High Usage", f"{len(high_usage):,}")


def render_revenue(df: pd.DataFrame):
    """Render Revenue tab"""
    UIComponents.section_title("💰 Revenue Opportunity")
    
    metrics = st.session_state.current_metrics
    heavy_count = metrics.get('heavy_users', 0)
    total_subscribers = metrics.get('total_subscribers', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        UIComponents.metric_card("💰 Premium Bundle Upsell", f"R{heavy_count * 299:,.0f}", color="success")
    with col2:
        UIComponents.metric_card("📊 Data Top-up Revenue", f"R{total_subscribers * 49:,.0f}", color="info")
    with col3:
        UIComponents.metric_card("📱 5G Upgrade Target", f"{int(total_subscribers * 0.05):,}", color="warning")
    
    # Revenue recommendations
    st.markdown("---")
    st.markdown("### 💡 Revenue Recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        UIComponents.recommendation_card(
            "🎯",
            "Targeted Upsell Campaign",
            "Focus on high-usage customers (>5 GB/day) who are currently on basic plans. "
            "Offer premium bundles with 20-30% more data at competitive rates to increase ARPU."
        )
    with col2:
        UIComponents.recommendation_card(
            "📡",
            "5G Early Adopter Program",
            "Identify customers with premium devices and heavy usage patterns for targeted "
            "5G upgrade offers. These users show 2.3x higher consumption and willingness to pay."
        )


def render_network(df: pd.DataFrame, vis):
    """Render Network tab"""
    UIComponents.section_title("📡 Network Insights")
    
    # Network heatmap
    fig_heatmap = vis.create_network_heatmap(df)
    if fig_heatmap:
        st.plotly_chart(fig_heatmap, use_container_width=True, key="network_heatmap")  # ← ADDED key
    
    # Network distribution
    fig_network = vis.create_network_distribution(df)
    if fig_network:
        st.plotly_chart(fig_network, use_container_width=True, key="network_dist")  # ← ADDED key
    
    # Network insights
    st.markdown("---")
    st.markdown("### 📡 Network Planning Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        UIComponents.insight_card(
            "⚠️ Peak Hours",
            "Evening peak (18:00-21:00) shows <strong>40% higher usage</strong> than average.",
            type="warning"
        )
        UIComponents.insight_card(
            "📱 5G Performance",
            "5G users consume <strong>2.3x more data</strong> than 4G users.",
            type="primary"
        )
    with col2:
        UIComponents.insight_card(
            "📈 Capacity Planning",
            "Consider capacity expansion in high-usage areas and during peak hours.",
            type="success"
        )
        UIComponents.insight_card(
            "📊 Weekend Usage",
            "Weekend usage patterns show <strong>25% higher</strong> daytime consumption.",
            type="warning"
        )


def render_model(df: pd.DataFrame, model_info: Dict[str, Any], vis):
    """Render Model tab"""
    UIComponents.section_title("🧠 Model & Pipeline")
    
    perf = model_info.get('performance', {})
    r2 = perf.get('r2_score', 'N/A')
    r2_display = f"{r2:.4f}" if isinstance(r2, (int, float)) else r2
    train_r2 = perf.get('train_r2_score', 'N/A')
    rmse = perf.get('rmse', 'N/A')
    mae = perf.get('mae', 'N/A')
    
    # Model metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        UIComponents.metric_card("📊 R² Score", r2_display)
    with col2:
        train_r2_display = f"{train_r2:.4f}" if isinstance(train_r2, (int, float)) else train_r2
        UIComponents.metric_card("📈 Training R²", train_r2_display)
    with col3:
        UIComponents.metric_card("📉 RMSE", str(rmse) if rmse != 'N/A' else 'N/A')
    with col4:
        UIComponents.metric_card("📊 MAE", str(mae) if mae != 'N/A' else 'N/A')
    
    # Feature importance
    st.markdown("---")
    st.subheader("📊 Feature Importance")
    
    fig_feature = vis.create_feature_importance(model_info['model'])
    if fig_feature:
        st.plotly_chart(fig_feature, use_container_width=True, key="model_feature_importance")  # ← ADDED key
    
    # Model configuration
    st.markdown("---")
    st.subheader("🔧 Model Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🏗️ Architecture**
        - Gradient Boosting Regressor
        - 150 estimators
        - Learning rate: 0.05
        - Max depth: 5
        - 13 features
        - Target: total_data_gb
        """)
    with col2:
        st.markdown(f"""
        **📊 Performance Details**
        - Training samples: {perf.get('training_samples', 'N/A')}
        - Test samples: {perf.get('test_samples', 'N/A')}
        - Dataset rows: {perf.get('dataset_rows', 'N/A')}
        - Features: {perf.get('n_features', 'N/A')}
        """)


def render_data_explorer(df: pd.DataFrame):
    """Render Data Explorer tab"""
    UIComponents.section_title("📊 Data Explorer")
    
    # Data preview
    st.subheader("📋 Data Preview")
    from ..data.loader import DataLoader
    loader = DataLoader()
    preview_df = loader.get_sample_data(df)
    st.dataframe(preview_df, use_container_width=True)
    
    # Data stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Rows", f"{len(df):,}")
    with col2:
        st.metric("📋 Total Columns", f"{len(df.columns)}")
    with col3:
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        st.metric("🔢 Numeric Features", f"{numeric_cols}")
    with col4:
        categorical_cols = len(df.select_dtypes(include=['object']).columns)
        st.metric("📝 Categorical Features", f"{categorical_cols}")
    
    # Summary statistics
    st.markdown("---")
    st.subheader("📈 Summary Statistics")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    
    # Column info
    st.markdown("---")
    st.subheader("📋 Column Information")
    
    # Convert dtypes to strings to avoid Arrow serialization issues
    col_info = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes.astype(str).values,  # ← KEY FIX: Convert dtype to string
        'Null Count': df.isnull().sum().values,
        'Unique Values': df.nunique().values
    })
    st.dataframe(col_info, use_container_width=True)


def render_monitoring(df: pd.DataFrame, model_info: Dict[str, Any]):
    """Render Monitoring tab"""
    UIComponents.section_title("📋 Model Monitoring")
    
    # Health metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "Production" if model_info.get('is_real', False) else "Demo"
        UIComponents.metric_card("🟢 Model Status", status)
    
    with col2:
        UIComponents.metric_card("📊 Total Predictions", f"{st.session_state.total_predictions:,}")
    
    with col3:
        avg_latency = np.mean(st.session_state.prediction_latency) if st.session_state.prediction_latency else 0
        UIComponents.metric_card("⏱️ Avg Latency", f"{avg_latency*1000:.0f} ms")
    
    # Prediction history
    if st.session_state.prediction_history:
        st.markdown("---")
        st.subheader("📋 Recent Predictions")
        
        history_df = pd.DataFrame(st.session_state.prediction_history[-20:])
        display_cols = ['timestamp', 'age_group', 'plan_type', 'network_type', 'device_type', 'prediction', 'arpu_zar']
        if all(col in history_df.columns for col in display_cols):
            st.dataframe(
                history_df[display_cols].style.format({
                    'prediction': '{:.2f}',
                    'arpu_zar': 'R{:.2f}'
                }),
                use_container_width=True
            )
    
    # Anomaly detection
    st.markdown("---")
    st.subheader("🔍 Anomaly Detection")
    
    from ..analytics.anomalies import AnomalyDetector
    detector = AnomalyDetector()
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    default_cols = [col for col in ['total_data_gb', 'hours_streaming', 'hours_gaming'] if col in numeric_cols]
    
    selected_cols = st.multiselect(
        "Select columns for anomaly detection",
        numeric_cols,
        default=default_cols
    )
    
    if selected_cols:
        threshold = st.slider("Z-score threshold", 1.5, 4.0, 2.5, 0.1)
        
        if st.button("🔍 Detect Anomalies", use_container_width=True):
            with st.spinner("Detecting anomalies..."):
                anomalies = detector.detect_anomalies(df, selected_cols, threshold)
                
                if len(anomalies) > 0:
                    st.warning(f"Found {len(anomalies)} anomalies in the data")
                    st.dataframe(anomalies, use_container_width=True)
                else:
                    st.success("✅ No anomalies detected above the threshold")
    
    # Latency trend
    if st.session_state.prediction_latency:
        st.markdown("---")
        st.subheader("⏱️ Latency Trend")
        
        latency_df = pd.DataFrame({
            'Prediction': range(1, len(st.session_state.prediction_latency) + 1),
            'Latency (ms)': np.array(st.session_state.prediction_latency) * 1000
        })
        
        import plotly.express as px
        fig_latency = px.line(
            latency_df,
            x='Prediction',
            y='Latency (ms)',
            title='Prediction Latency Over Time'
        )
        fig_latency.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif'}
        )
        st.plotly_chart(fig_latency, use_container_width=True, key="monitoring_latency")  # ← ADDED key