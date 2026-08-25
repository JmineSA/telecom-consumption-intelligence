"""
Onboarding wizard for first-time users
"""
import streamlit as st
from typing import Dict, Any


class OnboardingWizard:
    """Onboarding wizard for new users"""
    
    @staticmethod
    def show_onboarding():
        """Show the onboarding wizard"""
        if st.session_state.get('first_visit', True):
            with st.expander("🎓 Welcome to Telecom Intelligence!", expanded=True):
                st.markdown("""
                ### 🚀 Quick Start Guide
                
                Welcome to the Telecom Consumption Intelligence Platform!
                
                Here's how to get started:
                
                ---
                
                #### 📤 Step 1: Upload Data
                - Go to the sidebar
                - Click **"📂 Upload Dataset"**
                - Upload your CSV or Parquet file
                - Click **"📊 Use Data"**
                
                #### 🚀 Step 2: Train Model
                - Once data is loaded, click **"🔄 Retrain Model"** in the sidebar
                - This will train the ML model on your data
                
                #### 🎯 Step 3: Make Predictions
                - Go to the **"🎯 Predict & Explain"** tab
                - Configure user profile
                - Click **"🚀 Predict Usage"**
                
                #### 📊 Step 4: Explore Analytics
                - Check the **"📊 Analytics"** tab for insights
                - Explore **"👥 Segmentation"** for customer analysis
                - View **"📡 Network"** for network insights
                
                ---
                
                ### 💡 Need Help?
                - Check the **"📋 Monitoring"** tab for system health
                - View **"🧠 Model"** for model performance
                - Generate reports in the **"💰 Revenue"** tab
                
                Ready to begin?
                """)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🚀 Let's Go!", use_container_width=True):
                        st.session_state.first_visit = False
                        st.rerun()
    
    @staticmethod
    def show_tooltip(step: int, title: str, description: str):
        """Show a tooltip for a specific step"""
        if st.session_state.get('first_visit', True):
            with st.container():
                st.markdown(f"""
                <div style="background: #dbeafe; border-radius: 12px; padding: 1rem; border: 2px solid #93c5fd; margin: 0.5rem 0;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="background: #1a237e; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem;">{step}</span>
                        <span style="font-weight: 600; color: #1a237e;">{title}</span>
                    </div>
                    <div style="color: #64748b; margin-top: 0.3rem;">{description}</div>
                </div>
                """, unsafe_allow_html=True)