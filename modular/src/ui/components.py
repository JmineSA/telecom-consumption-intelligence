"""
Reusable UI components — thin wrappers around st.markdown for styled HTML.
"""
import streamlit as st


def metric_card(label: str, value: str, subtext: str = "", accent: str = None):
    """
    Render a metric card.

    accent: optional hex color for the value text (default: theme color)
    """
    value_style = f"color: {accent};" if accent else ""
    sub = f'<div class="metric-subtext">{subtext}</div>' if subtext else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="{value_style}">{value}</div>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def insight_card(title: str, body: str, icon: str = "", accent: str = None):
    """Render an insight card with optional left accent bar."""
    style = f'style="border-left-color: {accent};"' if accent else ""
    icon_html = f'<span class="insight-icon">{icon}</span> ' if icon else ""
    st.markdown(f"""
    <div class="insight-card" {style}>
        <div class="insight-title">{icon_html}{title}</div>
        <div class="insight-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(text: str, subtitle: str = ""):
    """Render a section header with optional subtitle."""
    sub = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">{text}</div>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Top-of-page header (larger than section header)."""
    sub = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{title}</div>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def result_card(value: float, unit: str = "GB", label: str = "",
                tag: str = "", tag_color: str = "#1a237e"):
    """Large centered result card for predictions."""
    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">{label}</div>
        <div class="result-value">
            {value:.2f}<span class="result-unit">{unit}</span>
        </div>
        <div class="result-tag" style="background: {tag_color}15; color: {tag_color};">
            {tag}
        </div>
    </div>
    """, unsafe_allow_html=True)