"""
CSS styling for the application with COMPLETE Dark Mode support
"""
import streamlit as st


def load_css():
    """Load all CSS styles with COMPLETE Dark Mode support"""
    
    # Base CSS - Always applied
    base_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            box-sizing: border-box;
        }
        
        /* ============================================ */
        /* LIGHT MODE (Default) */
        /* ============================================ */
        .stApp {
            background: #f8fafc;
        }
        
        .main-header {
            font-size: 3.2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #0f172a 0%, #1a237e 30%, #3949ab 60%, #5c6bc0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            padding: 0.5rem 0;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }
        
        .sub-header {
            color: #64748b;
            font-size: 1.05rem;
            font-weight: 400;
            letter-spacing: 0.2px;
            margin-top: 0.2rem;
        }
        
        .metric-premium {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid #f1f5f9;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-premium::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #1a237e, #5c6bc0);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .metric-premium:hover::before {
            opacity: 1;
        }
        
        .metric-premium:hover {
            box-shadow: 0 8px 30px rgba(26, 35, 126, 0.08);
            border-color: #e8edf3;
            transform: translateY(-2px);
        }
        
        .metric-premium .label {
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-premium .value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0.3rem 0 0.1rem 0;
        }
        
        .metric-premium .trend {
            font-size: 0.85rem;
            font-weight: 600;
            padding: 0.2rem 0.8rem;
            border-radius: 40px;
            display: inline-block;
        }
        
        .trend-up { background: #dcfce7; color: #16a34a; }
        .trend-down { background: #fee2e2; color: #dc2626; }
        .trend-neutral { background: #f1f5f9; color: #64748b; }
        
        .badge-modern {
            padding: 0.3rem 1.2rem;
            border-radius: 40px;
            font-weight: 600;
            font-size: 0.8rem;
            display: inline-block;
        }
        
        .badge-low { background: #dcfce7; color: #16a34a; border: 1px solid #86efac; }
        .badge-medium { background: #fef3c7; color: #d97706; border: 1px solid #fcd34d; }
        .badge-high { background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }
        .badge-primary { background: #dbeafe; color: #2563eb; border: 1px solid #93c5fd; }
        .badge-success { background: #dcfce7; color: #16a34a; border: 1px solid #86efac; }
        .badge-warning { background: #fef3c7; color: #d97706; border: 1px solid #fcd34d; }
        .badge-danger { background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }
        
        .insight-modern {
            background: white;
            border-radius: 16px;
            padding: 1rem 1.5rem;
            border-left: 4px solid;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            margin: 0.5rem 0;
        }
        
        .insight-modern.primary { border-left-color: #1a237e; background: #f8fafc; }
        .insight-modern.success { border-left-color: #22c55e; background: #f0fdf4; }
        .insight-modern.warning { border-left-color: #eab308; background: #fefce8; }
        .insight-modern.danger { border-left-color: #ef4444; background: #fef2f2; }
        
        .insight-modern .title {
            font-weight: 600;
            color: #0f172a;
            font-size: 0.9rem;
        }
        
        .insight-modern .desc {
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 0.2rem;
        }
        
        .rec-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid #f1f5f9;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .rec-card:hover {
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            transform: translateY(-4px);
            border-color: #e8edf3;
        }
        
        .rec-card .icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .rec-card .title { font-weight: 700; color: #0f172a; font-size: 1rem; }
        .rec-card .desc { color: #64748b; font-size: 0.85rem; line-height: 1.5; margin-top: 0.3rem; }
        
        .source-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.2rem 1rem;
            border-radius: 40px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .source-badge.uploaded { background: #dcfce7; color: #16a34a; }
        .source-badge.default { background: #dbeafe; color: #2563eb; }
        .source-badge.none { background: #f1f5f9; color: #64748b; }
        
        .status-pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.85); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .status-pulse.green { background: #22c55e; }
        .status-pulse.yellow { background: #eab308; }
        .status-pulse.red { background: #ef4444; }
        
        .no-data-modern {
            text-align: center;
            padding: 4rem;
            background: white;
            border-radius: 28px;
            border: 2px dashed #e8edf3;
            color: #64748b;
        }
        
        .no-data-modern .icon { font-size: 5rem; margin-bottom: 1rem; }
        .no-data-modern h3 { color: #0f172a; font-weight: 700; }
        
        .app-footer {
            margin-top: 3rem;
            padding: 1.5rem 0;
            border-top: 1px solid #f1f5f9;
            color: #94a3b8;
            font-size: 0.8rem;
            text-align: center;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: #f1f5f9;
            border-radius: 16px;
            padding: 5px;
            border: 1px solid #e8edf3;
            flex-wrap: wrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: 0.7rem 1.4rem;
            color: #64748b;
            font-weight: 500;
            font-size: 0.85rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: transparent !important;
            border: none !important;
            white-space: nowrap;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #1a237e;
            background: rgba(26, 35, 126, 0.06) !important;
            transform: scale(1.02);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: white !important;
            color: #1a237e !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            border: 1px solid #e8edf3 !important;
            font-weight: 600;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
            color: white;
            font-weight: 600;
            font-size: 0.95rem;
            border: none;
            padding: 0.7rem 2.5rem;
            border-radius: 60px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 16px rgba(26, 35, 126, 0.2);
            letter-spacing: 0.3px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 32px rgba(26, 35, 126, 0.3);
        }
        
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        
        @media (max-width: 768px) {
            .main-header { font-size: 2rem; }
            .metric-premium .value { font-size: 1.6rem; }
            .stTabs [data-baseweb="tab"] { padding: 0.5rem 0.8rem; font-size: 0.75rem; }
        }
        
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1.5rem !important;
        }
        
        /* Sidebar styling - Light Mode */
        .css-1d391kg, .st-emotion-cache-1d391kg {
            background-color: white !important;
        }
        
        .stSelectbox label, .stSlider label, .stMultiSelect label {
            color: #0f172a !important;
        }
        
        .stSelectbox div[data-baseweb="select"] {
            background-color: white !important;
        }
        
        .stDataFrame {
            background: white !important;
        }
        
        .stMarkdown {
            color: #0f172a !important;
        }
        
        div[data-testid="metric-container"] {
            background: white !important;
            border: 1px solid #f1f5f9 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }
    </style>
    """
    
    # ================================================================
    # COMPLETE DARK MODE CSS - Applied when dark_mode is True
    # ================================================================
    dark_mode_css = """
    <style>
        /* ============================================ */
        /* MAIN BACKGROUNDS */
        /* ============================================ */
        .stApp, .main > div, .stApp > div {
            background: #0f172a !important;
        }
        
        /* ============================================ */
        /* SIDEBAR - COMPLETE DARK */
        /* ============================================ */
        .css-1d391kg, .st-emotion-cache-1d391kg,
        section[data-testid="stSidebar"] > div,
        .stSidebar > div,
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b !important;
        }
        
        .css-1d391kg .stMarkdown, .st-emotion-cache-1d391kg .stMarkdown,
        .css-1d391kg p, .st-emotion-cache-1d391kg p,
        .css-1d391kg label, .st-emotion-cache-1d391kg label,
        .css-1d391kg div, .st-emotion-cache-1d391kg div {
            color: #e2e8f0 !important;
        }
        
        .css-1d391kg .stSelectbox label, .st-emotion-cache-1d391kg .stSelectbox label,
        .css-1d391kg .stSlider label, .st-emotion-cache-1d391kg .stSlider label {
            color: #e2e8f0 !important;
        }
        
        .css-1d391kg .stSelectbox div[data-baseweb="select"],
        .st-emotion-cache-1d391kg .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .css-1d391kg .stSelectbox input, .st-emotion-cache-1d391kg .stSelectbox input {
            color: #e2e8f0 !important;
        }
        
        .css-1d391kg .stSlider div[data-baseweb="slider"],
        .st-emotion-cache-1d391kg .stSlider div[data-baseweb="slider"] {
            background: #334155 !important;
        }
        
        .css-1d391kg .stExpander, .st-emotion-cache-1d391kg .stExpander {
            background: #0f172a !important;
            border-color: #1e293b !important;
        }
        
        .css-1d391kg .stExpander summary, .st-emotion-cache-1d391kg .stExpander summary {
            color: #e2e8f0 !important;
        }
        
        .css-1d391kg .stExpander .stMarkdown, .st-emotion-cache-1d391kg .stExpander .stMarkdown {
            color: #e2e8f0 !important;
        }
        
        .css-1d391kg .stButton > button, .st-emotion-cache-1d391kg .stButton > button {
            background: linear-gradient(135deg, #3949ab 0%, #5c6bc0 100%) !important;
            color: white !important;
        }
        
        /* ============================================ */
        /* HEADERS */
        /* ============================================ */
        .main-header {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 30%, #94a3b8 60%, #64748b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .sub-header {
            color: #94a3b8 !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #f8fafc !important;
        }
        
        /* ============================================ */
        /* METRIC CARDS - COMPLETE DARK FIX */
        /* ============================================ */
        .metric-premium {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .metric-premium .value {
            color: #f8fafc !important;
        }
        
        .metric-premium .label {
            color: #94a3b8 !important;
        }
        
        .metric-premium .trend {
            color: #e2e8f0 !important;
        }
        
        .metric-premium .trend-up {
            background: #1a3a1a !important;
            color: #4ade80 !important;
        }
        
        .metric-premium .trend-down {
            background: #3a1a1a !important;
            color: #f87171 !important;
        }
        
        .metric-premium .trend-neutral {
            background: #2a2a2a !important;
            color: #94a3b8 !important;
        }
        
        .metric-premium:hover {
            border-color: #4a5568 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
        }
        
        .metric-premium::before {
            background: linear-gradient(90deg, #5c6bc0, #8e99d6) !important;
        }
        
        /* Small text inside metrics */
        .metric-premium .value span {
            color: #94a3b8 !important;
        }
        
        .metric-premium div:not(.label):not(.value) {
            color: #94a3b8 !important;
        }
        
        /* ============================================ */
        /* INSIGHT CARDS */
        /* ============================================ */
        .insight-modern {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .insight-modern .title {
            color: #f8fafc !important;
        }
        
        .insight-modern .desc {
            color: #94a3b8 !important;
        }
        
        .insight-modern.primary { border-left-color: #5c6bc0 !important; background: #1a2332 !important; }
        .insight-modern.success { border-left-color: #22c55e !important; background: #1a2a1a !important; }
        .insight-modern.warning { border-left-color: #eab308 !important; background: #2a241a !important; }
        .insight-modern.danger { border-left-color: #ef4444 !important; background: #2a1a1a !important; }
        
        /* ============================================ */
        /* RECOMMENDATION CARDS */
        /* ============================================ */
        .rec-card {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .rec-card .title {
            color: #f8fafc !important;
        }
        
        .rec-card .desc {
            color: #94a3b8 !important;
        }
        
        .rec-card .icon {
            color: #e2e8f0 !important;
        }
        
        .rec-card:hover {
            border-color: #4a5568 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* ============================================ */
        /* NO DATA MESSAGE */
        /* ============================================ */
        .no-data-modern {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .no-data-modern h3 {
            color: #f8fafc !important;
        }
        
        .no-data-modern p {
            color: #94a3b8 !important;
        }
        
        /* ============================================ */
        /* TABS */
        /* ============================================ */
        .stTabs [data-baseweb="tab-list"] {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #94a3b8 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #f8fafc !important;
            background: rgba(57, 73, 171, 0.2) !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #2d3748 !important;
            color: #f8fafc !important;
            border-color: #4a5568 !important;
        }
        
        /* ============================================ */
        /* BUTTONS */
        /* ============================================ */
        .stButton > button {
            background: linear-gradient(135deg, #3949ab 0%, #5c6bc0 100%) !important;
            color: white !important;
            box-shadow: 0 4px 16px rgba(57, 73, 171, 0.3) !important;
        }
        
        .stButton > button:hover {
            box-shadow: 0 8px 32px rgba(57, 73, 171, 0.4) !important;
        }
        
        /* ============================================ */
        /* FOOTER */
        /* ============================================ */
        .app-footer {
            border-top-color: #334155 !important;
            color: #64748b !important;
        }
        
        /* ============================================ */
        /* SCROLLBAR */
        /* ============================================ */
        ::-webkit-scrollbar-track { background: #1a2332 !important; }
        ::-webkit-scrollbar-thumb { background: #4a5568 !important; }
        ::-webkit-scrollbar-thumb:hover { background: #5c6bc0 !important; }
        
        /* ============================================ */
        /* BADGES - DARK */
        /* ============================================ */
        .badge-low { background: #1a3a1a !important; color: #4ade80 !important; border-color: #22c55e !important; }
        .badge-medium { background: #3a2a1a !important; color: #facc15 !important; border-color: #eab308 !important; }
        .badge-high { background: #3a1a1a !important; color: #f87171 !important; border-color: #ef4444 !important; }
        .badge-primary { background: #1a2a4a !important; color: #60a5fa !important; border-color: #3b82f6 !important; }
        .badge-success { background: #1a3a1a !important; color: #4ade80 !important; border-color: #22c55e !important; }
        .badge-warning { background: #3a2a1a !important; color: #facc15 !important; border-color: #eab308 !important; }
        .badge-danger { background: #3a1a1a !important; color: #f87171 !important; border-color: #ef4444 !important; }
        
        /* ============================================ */
        /* SOURCE BADGE */
        /* ============================================ */
        .source-badge.uploaded { background: #1a3a1a !important; color: #4ade80 !important; }
        .source-badge.default { background: #1a2a4a !important; color: #60a5fa !important; }
        .source-badge.none { background: #2a2a2a !important; color: #94a3b8 !important; }
        
        /* ============================================ */
        /* STREAMLIT DEFAULTS - COMPLETE DARK */
        /* ============================================ */
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {
            color: #e2e8f0 !important;
        }
        
        .stMarkdown a {
            color: #60a5fa !important;
        }
        
        /* Select boxes */
        .stSelectbox label, .stSlider label, .stMultiSelect label,
        .stNumberInput label, .stTextInput label {
            color: #e2e8f0 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            border-color: #334155 !important;
            color: #e2e8f0 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] input {
            color: #e2e8f0 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] svg {
            fill: #e2e8f0 !important;
        }
        
        /* Dropdown options */
        div[role="listbox"] {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        div[role="listbox"] div[role="option"] {
            color: #e2e8f0 !important;
        }
        
        div[role="listbox"] div[role="option"]:hover {
            background: #2d3748 !important;
        }
        
        div[role="listbox"] div[role="option"][aria-selected="true"] {
            background: #3949ab !important;
            color: white !important;
        }
        
        /* Sliders */
        .stSlider div[data-baseweb="slider"] {
            background: #334155 !important;
        }
        
        .stSlider div[data-baseweb="slider"] div[role="slider"] {
            background: #5c6bc0 !important;
        }
        
        .stSlider div[data-baseweb="slider"] div[role="slider"]:hover {
            background: #7c8cd0 !important;
        }
        
        /* Number inputs */
        .stNumberInput input, .stTextInput input {
            background: #1e293b !important;
            border-color: #334155 !important;
            color: #e2e8f0 !important;
        }
        
        .stNumberInput input:focus, .stTextInput input:focus {
            border-color: #5c6bc0 !important;
        }
        
        /* DataFrames - COMPLETE DARK */
        .stDataFrame {
            background: #1e293b !important;
        }
        
        .stDataFrame table {
            background: #1e293b !important;
        }
        
        .stDataFrame thead tr th {
            background: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        
        .stDataFrame tbody tr td {
            background: #1e293b !important;
            color: #e2e8f0 !important;
            border-color: #334155 !important;
        }
        
        .stDataFrame tbody tr:hover td {
            background: #2d3748 !important;
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }
        
        div[data-testid="metric-container"] label {
            color: #94a3b8 !important;
        }
        
        div[data-testid="metric-container"] div {
            color: #f8fafc !important;
        }
        
        /* Expanders */
        .stExpander {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .stExpander summary {
            color: #e2e8f0 !important;
        }
        
        .stExpander summary:hover {
            color: #f8fafc !important;
        }
        
        .stExpander .stMarkdown {
            color: #e2e8f0 !important;
        }
        
        /* Alerts */
        .stAlert {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .stAlert div {
            color: #e2e8f0 !important;
        }
        
        .stAlert .stMarkdown {
            color: #e2e8f0 !important;
        }
        
        .stAlert[data-testid="stInfo"] { background: #1a2a4a !important; border-color: #3b82f6 !important; }
        .stAlert[data-testid="stSuccess"] { background: #1a3a1a !important; border-color: #22c55e !important; }
        .stAlert[data-testid="stWarning"] { background: #3a2a1a !important; border-color: #eab308 !important; }
        .stAlert[data-testid="stError"] { background: #3a1a1a !important; border-color: #ef4444 !important; }
        
        /* ============================================ */
        /* PLOTLY CHARTS - DARK MODE */
        /* ============================================ */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }
        
        .js-plotly-plot .plotly .cartesianlayer {
            background: transparent !important;
        }
        
        .js-plotly-plot .plotly .bg {
            fill: transparent !important;
        }
        
        .js-plotly-plot .plotly .annotation-text,
        .js-plotly-plot .plotly .xtick text,
        .js-plotly-plot .plotly .ytick text,
        .js-plotly-plot .plotly .legend .traces .legendtext {
            fill: #e2e8f0 !important;
        }
        
        .js-plotly-plot .plotly .gridlayer path,
        .js-plotly-plot .plotly .cartesianlayer path {
            stroke: #334155 !important;
        }
        
        .js-plotly-plot .plotly .legend .traces {
            fill: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* STATUS PULSE - DARK */
        /* ============================================ */
        .status-pulse.green { background: #4ade80 !important; }
        .status-pulse.yellow { background: #facc15 !important; }
        .status-pulse.red { background: #f87171 !important; }
        
        /* ============================================ */
        /* FILE UPLOADER - DARK */
        /* ============================================ */
        .stFileUploader {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .stFileUploader div {
            color: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* MULTI-SELECT - DARK */
        /* ============================================ */
        .stMultiSelect div[data-baseweb="select"] {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .stMultiSelect div[data-baseweb="select"] input {
            color: #e2e8f0 !important;
        }
        
        .stMultiSelect div[data-baseweb="tag"] {
            background: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* CODE BLOCKS - DARK */
        /* ============================================ */
        .stCodeBlock {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        .stCodeBlock pre {
            color: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* TOGGLE/SWITCH - DARK */
        /* ============================================ */
        .stToggle div[role="switch"] {
            background: #334155 !important;
        }
        
        .stToggle div[role="switch"][aria-checked="true"] {
            background: #5c6bc0 !important;
        }
        
        .stToggle div[role="switch"] span {
            color: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* DOWNLOAD BUTTON - DARK */
        /* ============================================ */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #3949ab 0%, #5c6bc0 100%) !important;
            color: white !important;
        }
        
        /* ============================================ */
        /* PANDAS STYLED DATAFRAME - DARK */
        /* ============================================ */
        .dataframe {
            background: #1e293b !important;
            color: #e2e8f0 !important;
        }
        
        .dataframe thead tr th {
            background: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        
        .dataframe tbody tr td {
            color: #e2e8f0 !important;
            border-color: #334155 !important;
        }
        
        .dataframe tbody tr:nth-child(even) {
            background: #1a2332 !important;
        }
        
        .dataframe tbody tr:hover {
            background: #2d3748 !important;
        }
        
        /* ============================================ */
        /* STREAMLIT CONTAINERS - DARK */
        /* ============================================ */
        .stContainer, .stBlock {
            background: transparent !important;
        }
        
        .stColumn > div {
            background: transparent !important;
        }
        
        /* ============================================ */
        /* SLIDER LABELS - DARK */
        /* ============================================ */
        .stSlider .stMarkdown {
            color: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* SELECTBOX PLACEHOLDER - DARK */
        /* ============================================ */
        .stSelectbox div[data-baseweb="select"] div[role="combobox"] {
            color: #e2e8f0 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] div[role="combobox"]:hover {
            color: #f8fafc !important;
        }
        
        /* ============================================ */
        /* MULTISELECT PLACEHOLDER - DARK */
        /* ============================================ */
        .stMultiSelect div[data-baseweb="select"] div[role="combobox"] {
            color: #e2e8f0 !important;
        }
        
        /* ============================================ */
        /* INPUT PLACEHOLDER - DARK */
        /* ============================================ */
        .stTextInput input::placeholder,
        .stNumberInput input::placeholder {
            color: #64748b !important;
        }
    </style>
    """
    
    # Apply CSS based on dark mode setting
    if st.session_state.get('dark_mode', False):
        st.markdown(base_css + dark_mode_css, unsafe_allow_html=True)
    else:
        st.markdown(base_css, unsafe_allow_html=True)