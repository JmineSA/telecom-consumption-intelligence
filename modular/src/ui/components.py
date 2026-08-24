"""
Reusable UI components
"""
import streamlit as st
import pandas as pd
from typing import Optional, Callable, Any
from ..constants import COLORS, RISK_CATEGORIES


class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def metric_card(label: str, value: Any, 
                    trend: Optional[float] = None,
                    color: str = 'primary',
                    help_text: Optional[str] = None) -> None:
        """Display a metric card"""
        trend_html = ""
        if trend is not None:
            trend_class = 'trend-up' if trend > 0 else 'trend-down' if trend < 0 else 'trend-neutral'
            icon = '📈' if trend > 0 else '📉' if trend < 0 else '➡️'
            trend_html = f'<span class="trend {trend_class}">{icon} {trend:+.1f}%</span>'
        
        value_color = COLORS.get(color, '#0f172a')
        
        st.markdown(f"""
        <div class="metric-premium">
            <div class="label">{label}</div>
            <div class="value" style="color: {value_color};">{value}</div>
            {trend_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def insight_card(title: str, description: str, 
                     type: str = 'primary') -> None:
        """Display an insight card"""
        st.markdown(f"""
        <div class="insight-modern {type}">
            <div class="title">{title}</div>
            <div class="desc">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def recommendation_card(icon: str, title: str, 
                           description: str) -> None:
        """Display a recommendation card"""
        st.markdown(f"""
        <div class="rec-card">
            <div class="icon">{icon}</div>
            <div class="title">{title}</div>
            <div class="desc">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def badge(label: str, category: str = 'primary') -> str:
        """Generate an HTML badge"""
        return f'<span class="badge-modern badge-{category}">{label}</span>'
    
    @staticmethod
    def status_indicator(status: str) -> str:
        """Generate status indicator HTML"""
        color = 'green' if status in ['healthy', 'active'] else 'yellow' if status in ['warning', 'pending'] else 'red'
        return f'<span class="status-pulse {color}"></span>'
    
    @staticmethod
    def source_badge(source_type: str) -> str:
        """Generate source badge HTML"""
        labels = {
            'uploaded': ('📤 Uploaded', 'uploaded'),
            'default': ('📁 Default', 'default'),
            'none': ('⚪ No Data', 'none')
        }
        label, badge_class = labels.get(source_type, ('📊 Dataset', 'none'))
        return f'<span class="source-badge {badge_class}">{label}</span>'
    
    @staticmethod
    def no_data_message(icon: str = "📤", title: str = "No Data Available",
                        description: str = "Upload your dataset to get started.") -> None:
        """Display no data message"""
        st.markdown(f"""
        <div class="no-data-modern">
            <div class="icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def section_title(title: str, subtitle: Optional[str] = None) -> None:
        """Display a section title"""
        st.markdown(f'<h2 style="color: #0f172a; font-weight: 800;">{title}</h2>', 
                   unsafe_allow_html=True)
        if subtitle:
            st.markdown(f'<p style="color: #64748b;">{subtitle}</p>', 
                       unsafe_allow_html=True)