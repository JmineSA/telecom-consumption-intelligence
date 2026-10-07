"""
Modern corporate styling — Clean & Corporate aesthetic.

- Navy accent (#1a237e)
- Inter-style typography
- Subtle shadows, rounded corners
- Light + dark mode via prefers-color-scheme
- Streamlit default chrome hidden
"""
import streamlit as st


def load_css():
    st.markdown("""
    <style>
    /* ============================================================ */
    /* FONT STACK                                                    */
    /* ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ============================================================ */
    /* HIDE STREAMLIT DEFAULT CHROME                                 */
    /* ============================================================ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}

    /* ============================================================ */
    /* LAYOUT SPACING                                                */
    /* ============================================================ */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px;
    }

    /* ============================================================ */
    /* THEME VARIABLES (light default, dark override below)          */
    /* ============================================================ */
    :root {
        --bg-card: #ffffff;
        --bg-subtle: #f8fafc;
        --border: #eef2f7;
        --border-strong: #e2e8f0;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --accent: #1a237e;
        --accent-light: #eef2ff;
        --accent-border: #c7d2fe;
        --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
        --shadow-md: 0 2px 6px rgba(15, 23, 42, 0.06);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-card: #1a1f2e;
            --bg-subtle: #151923;
            --border: #252b3a;
            --border-strong: #2f3748;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #64748b;
            --accent: #8b9cff;
            --accent-light: #1e2749;
            --accent-border: #3d4a7a;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 2px 6px rgba(0, 0, 0, 0.5);
        }
    }

    /* ============================================================ */
    /* PAGE HEADER                                                   */
    /* ============================================================ */
    .page-header { margin-bottom: 2rem; }

    .page-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 0.4rem;
    }

    .page-subtitle {
        font-size: 1.05rem;
        color: var(--text-secondary);
        line-height: 1.5;
        max-width: 700px;
    }

    /* ============================================================ */
    /* SECTION HEADER                                                */
    /* ============================================================ */
    .section-header {
        margin: 2.5rem 0 1.25rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }

    .section-subtitle {
        font-size: 0.9rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* ============================================================ */
    /* METRIC CARD                                                   */
    /* ============================================================ */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.15s ease, transform 0.15s ease;
        height: 100%;
    }

    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .metric-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    .metric-subtext {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.35rem;
    }

    /* ============================================================ */
    /* INSIGHT CARD                                                  */
    /* ============================================================ */
    .insight-card {
        background: var(--bg-subtle);
        border-left: 3px solid var(--accent);
        border-radius: 10px;
        padding: 1.15rem 1.35rem;
        margin-bottom: 0.85rem;
        transition: background 0.15s ease;
    }

    .insight-card:hover { background: var(--bg-card); }

    .insight-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .insight-icon { font-size: 1.1rem; }

    .insight-body {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.55;
    }

    /* ============================================================ */
    /* RESULT CARD (Predict page)                                    */
    /* ============================================================ */
    .result-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        margin: 1rem 0;
    }

    .result-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.9px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 1rem;
    }

    .result-value {
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        color: var(--text-primary);
        line-height: 1;
        display: inline-flex;
        align-items: baseline;
        gap: 0.4rem;
    }

    .result-unit {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-muted);
    }

    .result-tag {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        margin-top: 1.25rem;
    }

    /* ============================================================ */
    /* SIDEBAR                                                       */
    /* ============================================================ */
    [data-testid="stSidebar"] {
        background: var(--bg-subtle);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Sidebar radio nav */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 2px;
        padding: 0;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 8px 12px !important;
        border-radius: 8px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        transition: all 0.12s ease !important;
        cursor: pointer !important;
        border: 1px solid transparent !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: var(--accent-light) !important;
        border-color: var(--accent-border) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* ============================================================ */
    /* BUTTONS                                                       */
    /* ============================================================ */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: var(--accent);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: -0.01em;
        padding: 0.6rem 1.2rem;
        transition: all 0.15s ease;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 10px;
        font-weight: 500;
        border: 1px solid var(--border-strong);
        background: var(--bg-card);
        color: var(--text-primary);
        transition: all 0.15s ease;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: var(--accent-border);
        background: var(--accent-light);
    }

    /* ============================================================ */
    /* FORMS / INPUTS                                                */
    /* ============================================================ */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] .stNumberInput input {
        border-radius: 8px !important;
    }

    /* ============================================================ */
    /* METRIC (Streamlit native st.metric)                           */
    /* ============================================================ */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        box-shadow: var(--shadow-sm);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.7px !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
    }

    /* ============================================================ */
    /* DATAFRAME                                                     */
    /* ============================================================ */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid var(--border);
        overflow: hidden;
    }

    /* ============================================================ */
    /* CODE BLOCK (for business summary)                             */
    /* ============================================================ */
    [data-testid="stCode"] {
        border-radius: 10px;
        border: 1px solid var(--border);
    }

    /* ============================================================ */
    /* FOOTER                                                        */
    /* ============================================================ */
    .app-footer {
        text-align: center;
        color: var(--text-muted);
        padding: 3rem 0 1rem 0;
        font-size: 0.75rem;
        border-top: 1px solid var(--border);
        margin-top: 4rem;
        letter-spacing: 0.2px;
    }

    /* ============================================================ */
    /* SCROLLBAR                                                     */
    /* ============================================================ */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--border-strong);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
    </style>
    """, unsafe_allow_html=True)