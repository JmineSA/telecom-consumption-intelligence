"""
Minimal CSS for the app — light + dark mode support.
"""
import streamlit as st


def load_css():
    """Inject minimal custom CSS."""
    st.markdown("""
    <style>
        /* Clean metric cards */
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 1.25rem;
            border: 1px solid #eef2f7;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .metric-value {
            color: #0f172a;
            font-size: 1.75rem;
            font-weight: 800;
            margin-top: 0.25rem;
        }

        /* Section headers */
        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #0f172a;
            margin: 1.5rem 0 0.75rem 0;
        }

        /* Insight cards */
        .insight-card {
            background: #f8fafc;
            border-left: 4px solid #1a237e;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
        }
        .insight-title {
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.25rem;
        }
        .insight-body {
            color: #475569;
            font-size: 0.9rem;
        }

        /* Result card */
        .result-card {
            background: linear-gradient(145deg, #f8fafc, #eef2f7);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        .result-value {
            font-size: 3rem;
            font-weight: 900;
        }
        .result-unit {
            font-size: 1.2rem;
            color: #64748b;
        }

        /* App footer */
        .app-footer {
            text-align: center;
            color: #94a3b8;
            padding: 2rem 0 1rem 0;
            font-size: 0.75rem;
            border-top: 1px solid #eef2f7;
            margin-top: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)