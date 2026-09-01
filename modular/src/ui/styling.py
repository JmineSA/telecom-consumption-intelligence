"""
CSS styling for the application with Dark Mode support - Professional Edition
"""
import streamlit as st


def load_css():
    """Load all CSS styles with Dark Mode support - Professional Edition"""
    
    # Base CSS - Always applied
    base_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            box-sizing: border-box;
        }
        
        /* ============================================ */
        /* LIGHT MODE (Default) - Premium Design */
        /* ============================================ */
        .stApp {
            background: #f0f4f8;
        }
        
        /* Modern Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 28px;
            padding: 1.8rem;
            box-shadow: 0 8px 40px rgba(0, 0, 0, 0.04);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
            box-shadow: 0 16px 60px rgba(0, 0, 0, 0.08);
            transform: translateY(-4px);
            border-color: rgba(57, 73, 171, 0.2);
        }
        
        /* Modern Gradient Header */
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
        
        /* Premium Metric Cards */
        .metric-premium {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid #e8edf3;
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
            border-color: #dce3ed;
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
        
        /* Badge Styles */
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
        
        /* Insight Cards */
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
        
        /* Recommendation Cards */
        .rec-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid #e8edf3;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .rec-card:hover {
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            transform: translateY(-4px);
            border-color: #dce3ed;
        }
        
        .rec-card .icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .rec-card .title {
            font-weight: 700;
            color: #0f172a;
            font-size: 1rem;
        }
        
        .rec-card .desc {
            color: #64748b;
            font-size: 0.85rem;
            line-height: 1.5;
            margin-top: 0.3rem;
        }
        
        /* Source Badge */
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
        
        /* Status Pulse */
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
        
        /* No Data Message */
        .no-data-modern {
            text-align: center;
            padding: 4rem;
            background: white;
            border-radius: 28px;
            border: 2px dashed #e8edf3;
            color: #64748b;
        }
        
        .no-data-modern .icon {
            font-size: 5rem;
            margin-bottom: 1rem;
        }
        
        .no-data-modern h3 {
            color: #0f172a;
            font-weight: 700;
        }
        
        /* Footer */
        .app-footer {
            margin-top: 3rem;
            padding: 1.5rem 0;
            border-top: 1px solid #e8edf3;
            color: #94a3b8;
            font-size: 0.8rem;
            text-align: center;
        }
        
        /* Tab Styling - Premium */
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
        
        /* Button Styling - Premium Gradient */
        .stButton > button {
            background: linear-gradient(135deg, #1a237e 0%, #3949ab 50%, #5c6bc0 100%);
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
        
        .stButton > button:active {
            transform: scale(0.98);
        }
        
        /* Scrollbar - Premium */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
        ::-webkit-scrollbar-thumb { 
            background: linear-gradient(135deg, #cbd5e1, #94a3b8);
            border-radius: 10px; 
        }
        ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #94a3b8, #64748b); }
        
        /* Responsive */
        @media (max-width: 768px) {
            .main-header { font-size: 2rem; }
            .metric-premium .value { font-size: 1.6rem; }
            .stTabs [data-baseweb="tab"] { padding: 0.5rem 0.8rem; font-size: 0.75rem; }
        }
        
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1.5rem !important;
        }
        
        /* Sidebar styling - Light Mode Premium */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
            border-right: 1px solid #e8edf3 !important;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.02) !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: #0f172a !important;
        }
        
        section[data-testid="stSidebar"] label {
            color: #1e293b !important;
            font-weight: 500 !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff !important;
            border-color: #e8edf3 !important;
        }
        
        section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] {
            background: #e8edf3 !important;
        }
        
        /* Sidebar headings */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4 {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        
        /* Streamlit default overrides - Light Mode */
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
        
        /* Metric container */
        div[data-testid="metric-container"] {
            background: white !important;
            border: 1px solid #e8edf3 !important;
            border-radius: 16px !important;
            padding: 1rem !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        }
    </style>
    """
    
    # ================================================
    # DARK MODE CSS - Premium Dark Theme
    # ================================================
    dark_mode_css = """
    <style>
        /* ============================================ */
        /* MAIN APP - Dark Mode Premium */
        /* ============================================ */
        .stApp {
            background: #0a0e1a !important;
        }
        
        .main > div {
            background: #0a0e1a !important;
        }
        
        /* ============================================ */
        /* SIDEBAR - Premium Dark Mode */
        /* ============================================ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
            border-right: 1px solid #1e293b !important;
            box-shadow: 4px 0 30px rgba(0, 0, 0, 0.4) !important;
        }
        
        /* Sidebar content containers */
        section[data-testid="stSidebar"] .css-1d391kg,
        section[data-testid="stSidebar"] .st-emotion-cache-1d391kg,
        section[data-testid="stSidebar"] .css-1544g2n,
        section[data-testid="stSidebar"] .st-emotion-cache-1544g2n,
        section[data-testid="stSidebar"] .css-1v3fvcr,
        section[data-testid="stSidebar"] .st-emotion-cache-1v3fvcr {
            background: transparent !important;
        }
        
        /* Sidebar text - LIGHTER for better visibility */
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown div,
        section[data-testid="stSidebar"] div[data-testid="stMarkdown"] {
            color: #e8edf5 !important;
        }
        
        /* Sidebar headers - BRIGHT WHITE */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] h5,
        section[data-testid="stSidebar"] h6 {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        /* Sidebar labels - LIGHTER */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stMultiSelect label {
            color: #d1d9e6 !important;
            font-weight: 500 !important;
        }
        
        /* Sidebar select boxes */
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] input {
            color: #e8edf5 !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] svg {
            fill: #94a3b8 !important;
        }
        
        /* Sidebar sliders */
        section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] {
            background: #2d3748 !important;
        }
        
        section[data-testid="stSidebar"] .stSlider div[role="slider"] {
            background: linear-gradient(135deg, #5c6bc0, #8e99d6) !important;
            box-shadow: 0 0 12px rgba(92, 107, 192, 0.4) !important;
        }
        
        section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] div {
            color: #e8edf5 !important;
        }
        
        /* Sidebar number inputs */
        section[data-testid="stSidebar"] .stNumberInput input,
        section[data-testid="stSidebar"] .stTextInput input {
            background-color: #1e293b !important;
            border-color: #334155 !important;
            color: #e8edf5 !important;
        }
        
        section[data-testid="stSidebar"] .stNumberInput input:focus,
        section[data-testid="stSidebar"] .stTextInput input:focus {
            border-color: #5c6bc0 !important;
            box-shadow: 0 0 0 2px rgba(92, 107, 192, 0.2) !important;
        }
        
        /* Sidebar buttons */
        section[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #3949ab 0%, #5c6bc0 50%, #7986cb 100%) !important;
            color: white !important;
            box-shadow: 0 4px 16px rgba(57, 73, 171, 0.3) !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 32px rgba(57, 73, 171, 0.5) !important;
        }
        
        /* Sidebar expanders */
        section[data-testid="stSidebar"] .stExpander {
            background: rgba(30, 41, 59, 0.5) !important;
            border-color: #1e293b !important;
            border-radius: 12px !important;
        }
        
        section[data-testid="stSidebar"] .stExpander summary {
            color: #e8edf5 !important;
            font-weight: 600 !important;
        }
        
        section[data-testid="stSidebar"] .stExpander summary:hover {
            color: #ffffff !important;
        }
        
        section[data-testid="stSidebar"] .stExpander .stMarkdown {
            color: #d1d9e6 !important;
        }
        
        /* Sidebar file uploader */
        section[data-testid="stSidebar"] .stFileUploader {
            background: #1e293b !important;
            border: 2px dashed #334155 !important;
            border-radius: 12px !important;
        }
        
        section[data-testid="stSidebar"] .stFileUploader:hover {
            border-color: #5c6bc0 !important;
        }
        
        section[data-testid="stSidebar"] .stFileUploader div {
            color: #d1d9e6 !important;
        }
        
        /* Sidebar toggle/switch */
        section[data-testid="stSidebar"] .stToggle div[role="switch"] {
            background: #2d3748 !important;
        }
        
        section[data-testid="stSidebar"] .stToggle div[role="switch"][aria-checked="true"] {
            background: linear-gradient(135deg, #3949ab, #5c6bc0) !important;
        }
        
        section[data-testid="stSidebar"] .stToggle span {
            color: #e8edf5 !important;
        }
        
        /* Sidebar checkbox */
        section[data-testid="stSidebar"] .stCheckbox label span {
            color: #e8edf5 !important;
        }
        
        /* Sidebar radio buttons */
        section[data-testid="stSidebar"] .stRadio label div {
            color: #e8edf5 !important;
        }
        
        /* Sidebar selectbox dropdown */
        section[data-testid="stSidebar"] div[role="listbox"] {
            background: #1e293b !important;
            border-color: #334155 !important;
            border-radius: 12px !important;
        }
        
        section[data-testid="stSidebar"] div[role="listbox"] div[role="option"] {
            color: #d1d9e6 !important;
            padding: 8px 16px !important;
        }
        
        section[data-testid="stSidebar"] div[role="listbox"] div[role="option"]:hover {
            background: #2d3748 !important;
            color: #ffffff !important;
        }
        
        section[data-testid="stSidebar"] div[role="listbox"] div[role="option"][aria-selected="true"] {
            background: linear-gradient(135deg, #3949ab, #5c6bc0) !important;
            color: white !important;
        }
        
        /* Sidebar info/warning/success/error boxes */
        section[data-testid="stSidebar"] .stAlert {
            background: #1e293b !important;
            border-color: #334155 !important;
            border-radius: 12px !important;
        }
        
        section[data-testid="stSidebar"] .stAlert div {
            color: #e8edf5 !important;
        }
        
        /* Sidebar dataframes */
        section[data-testid="stSidebar"] .stDataFrame {
            background: transparent !important;
        }
        
        section[data-testid="stSidebar"] .stDataFrame thead tr th {
            background: #1e293b !important;
            color: #e8edf5 !important;
            border-color: #334155 !important;
        }
        
        section[data-testid="stSidebar"] .stDataFrame tbody tr td {
            background: transparent !important;
            color: #d1d9e6 !important;
            border-color: #1e293b !important;
        }
        
        section[data-testid="stSidebar"] .stDataFrame tbody tr:hover td {
            background: #1e293b !important;
        }
        
        /* ============================================ */
        /* MAIN CONTENT - Premium Dark Mode */
        /* ============================================ */
        
        /* Headers - BRIGHT */
        .main-header {
            background: linear-gradient(135deg, #e8edf5 0%, #ffffff 30%, #94a3b8 60%, #e8edf5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .sub-header {
            color: #94a3b8 !important;
        }
        
        /* Glass cards - Dark */
        .glass-card {
            background: rgba(17, 24, 39, 0.85) !important;
            border-color: rgba(255, 255, 255, 0.06) !important;
        }
        
        .glass-card:hover {
            border-color: rgba(92, 107, 192, 0.3) !important;
            box-shadow: 0 16px 60px rgba(0, 0, 0, 0.4) !important;
        }
        
        /* Metric Premium Cards - Dark */
        .metric-premium {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .metric-premium .value {
            color: #f8fafc !important;
        }
        
        .metric-premium .label {
            color: #94a3b8 !important;
        }
        
        .metric-premium:hover {
            border-color: #2d3748 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
        }
        
        .metric-premium::before {
            background: linear-gradient(90deg, #5c6bc0, #8e99d6) !important;
        }
        
        /* Insight Cards - Dark */
        .insight-modern {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .insight-modern .title {
            color: #f8fafc !important;
        }
        
        .insight-modern .desc {
            color: #94a3b8 !important;
        }
        
        .insight-modern.primary { border-left-color: #5c6bc0 !important; background: #111827 !important; }
        .insight-modern.success { border-left-color: #4ade80 !important; background: #0f1a0f !important; }
        .insight-modern.warning { border-left-color: #facc15 !important; background: #1a180f !important; }
        .insight-modern.danger { border-left-color: #f87171 !important; background: #1a0f0f !important; }
        
        /* Recommendation Cards - Dark */
        .rec-card {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .rec-card .title {
            color: #f8fafc !important;
        }
        
        .rec-card .desc {
            color: #94a3b8 !important;
        }
        
        .rec-card:hover {
            border-color: #2d3748 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
        }
        
        .rec-card .icon {
            color: #e8edf5 !important;
        }
        
        /* No Data Message - Dark */
        .no-data-modern {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .no-data-modern h3 {
            color: #f8fafc !important;
        }
        
        .no-data-modern p {
            color: #94a3b8 !important;
        }
        
        /* Tab Styling - Dark */
        .stTabs [data-baseweb="tab-list"] {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #94a3b8 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #f8fafc !important;
            background: rgba(57, 73, 171, 0.15) !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #1e293b !important;
            color: #f8fafc !important;
            border-color: #2d3748 !important;
        }
        
        /* Footer - Dark */
        .app-footer {
            border-top-color: #1e293b !important;
            color: #64748b !important;
        }
        
        /* Dark mode scrollbar */
        ::-webkit-scrollbar-track { background: #0f172a !important; }
        ::-webkit-scrollbar-thumb { 
            background: linear-gradient(135deg, #2d3748, #4a5568) !important;
            border-radius: 10px !important;
        }
        ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #4a5568, #5c6bc0) !important; }
        
        /* Dark mode status pulse - BRIGHTER */
        .status-pulse.green { background: #4ade80 !important; }
        .status-pulse.yellow { background: #facc15 !important; }
        .status-pulse.red { background: #f87171 !important; }
        
        /* Dark mode badges - CONTRAST */
        .badge-low { background: #0f1a0f !important; color: #4ade80 !important; border-color: #22c55e !important; }
        .badge-medium { background: #1a180f !important; color: #facc15 !important; border-color: #eab308 !important; }
        .badge-high { background: #1a0f0f !important; color: #f87171 !important; border-color: #ef4444 !important; }
        .badge-primary { background: #0f1a2a !important; color: #60a5fa !important; border-color: #3b82f6 !important; }
        .badge-success { background: #0f1a0f !important; color: #4ade80 !important; border-color: #22c55e !important; }
        .badge-warning { background: #1a180f !important; color: #facc15 !important; border-color: #eab308 !important; }
        .badge-danger { background: #1a0f0f !important; color: #f87171 !important; border-color: #ef4444 !important; }
        
        /* Dark mode source badge - CONTRAST */
        .source-badge.uploaded { background: #0f1a0f !important; color: #4ade80 !important; }
        .source-badge.default { background: #0f1a2a !important; color: #60a5fa !important; }
        .source-badge.none { background: #1a1a1a !important; color: #94a3b8 !important; }
        
        /* ============================================ */
        /* STREAMLIT DEFAULTS - Dark Mode */
        /* ============================================ */
        
        /* Selectbox */
        .stSelectbox label, .stSlider label, .stMultiSelect label {
            color: #e8edf5 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] {
            background-color: #111827 !important;
            border-color: #1e293b !important;
            color: #e8edf5 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] input {
            color: #e8edf5 !important;
        }
        
        /* DataFrame */
        .stDataFrame {
            background: #111827 !important;
            color: #e8edf5 !important;
        }
        
        .stDataFrame thead tr th {
            background: #1e293b !important;
            color: #e8edf5 !important;
            border-color: #2d3748 !important;
        }
        
        .stDataFrame tbody tr td {
            background: #111827 !important;
            color: #d1d9e6 !important;
            border-color: #1e293b !important;
        }
        
        .stDataFrame tbody tr:hover td {
            background: #1e293b !important;
        }
        
        /* Markdown - MAIN CONTENT */
        .stMarkdown {
            color: #e8edf5 !important;
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #ffffff !important;
        }
        
        .stMarkdown p, .stMarkdown li {
            color: #d1d9e6 !important;
        }
        
        /* Metric container */
        div[data-testid="metric-container"] {
            background: #111827 !important;
            border: 1px solid #1e293b !important;
            border-radius: 16px !important;
            padding: 1rem !important;
        }
        
        div[data-testid="metric-container"] label {
            color: #94a3b8 !important;
        }
        
        div[data-testid="metric-container"] div {
            color: #f8fafc !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3949ab 0%, #5c6bc0 50%, #7986cb 100%) !important;
            color: white !important;
            box-shadow: 0 4px 16px rgba(57, 73, 171, 0.3) !important;
        }
        
        .stButton > button:hover {
            box-shadow: 0 8px 32px rgba(57, 73, 171, 0.5) !important;
            transform: translateY(-2px) scale(1.02);
        }
        
        /* Expander */
        .stExpander {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .stExpander summary {
            color: #e8edf5 !important;
            font-weight: 600 !important;
        }
        
        .stExpander summary:hover {
            color: #ffffff !important;
        }
        
        /* Selectbox dropdown */
        div[role="listbox"] {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        div[role="listbox"] div[role="option"] {
            color: #d1d9e6 !important;
        }
        
        div[role="listbox"] div[role="option"]:hover {
            background: #1e293b !important;
            color: #ffffff !important;
        }
        
        div[role="listbox"] div[role="option"][aria-selected="true"] {
            background: linear-gradient(135deg, #3949ab, #5c6bc0) !important;
            color: white !important;
        }
        
        /* Slider */
        .stSlider div[data-baseweb="slider"] {
            background: #2d3748 !important;
        }
        
        .stSlider div[data-baseweb="slider"] div[role="slider"] {
            background: linear-gradient(135deg, #5c6bc0, #8e99d6) !important;
            box-shadow: 0 0 12px rgba(92, 107, 192, 0.4) !important;
        }
        
        /* Number input */
        .stNumberInput input {
            background: #111827 !important;
            border-color: #1e293b !important;
            color: #e8edf5 !important;
        }
        
        .stNumberInput input:focus {
            border-color: #5c6bc0 !important;
            box-shadow: 0 0 0 2px rgba(92, 107, 192, 0.2) !important;
        }
        
        /* Text input */
        .stTextInput input {
            background: #111827 !important;
            border-color: #1e293b !important;
            color: #e8edf5 !important;
        }
        
        .stTextInput input:focus {
            border-color: #5c6bc0 !important;
            box-shadow: 0 0 0 2px rgba(92, 107, 192, 0.2) !important;
        }
        
        /* Alerts */
        .stAlert {
            background: #111827 !important;
            border-color: #1e293b !important;
            color: #e8edf5 !important;
        }
        
        .stAlert div {
            color: #e8edf5 !important;
        }
        
        /* Plotly charts */
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
        .js-plotly-plot .plotly .ytick text {
            fill: #d1d9e6 !important;
        }
        
        .js-plotly-plot .plotly .legend .traces .legendtext {
            fill: #d1d9e6 !important;
        }
        
        .js-plotly-plot .plotly .gridlayer path,
        .js-plotly-plot .plotly .cartesianlayer path {
            stroke: #1e293b !important;
        }
        
        /* Code blocks */
        .stCodeBlock {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .stCodeBlock pre {
            color: #e8edf5 !important;
        }
        
        /* Download button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #3949ab 0%, #5c6bc0 50%, #7986cb 100%) !important;
            color: white !important;
        }
        
        /* Toggle/Switch */
        .stToggle div[role="switch"] {
            background: #2d3748 !important;
        }
        
        .stToggle div[role="switch"][aria-checked="true"] {
            background: linear-gradient(135deg, #3949ab, #5c6bc0) !important;
        }
        
        .stToggle div[role="switch"] span {
            color: #e8edf5 !important;
        }
        
        /* File uploader */
        .stFileUploader {
            background: #111827 !important;
            border: 2px dashed #1e293b !important;
        }
        
        .stFileUploader:hover {
            border-color: #5c6bc0 !important;
        }
        
        .stFileUploader div {
            color: #d1d9e6 !important;
        }
        
        /* Multi-select */
        .stMultiSelect div[data-baseweb="select"] {
            background: #111827 !important;
            border-color: #1e293b !important;
        }
        
        .stMultiSelect div[data-baseweb="select"] input {
            color: #e8edf5 !important;
        }
        
        .stMultiSelect div[data-baseweb="tag"] {
            background: #1e293b !important;
            color: #e8edf5 !important;
        }
        
        /* Checkbox */
        .stCheckbox label span {
            color: #d1d9e6 !important;
        }
        
        /* Radio */
        .stRadio label div {
            color: #d1d9e6 !important;
        }
        
        /* Select slider */
        .stSelectSlider label {
            color: #e8edf5 !important;
        }
    </style>
    """
    
    # Apply CSS based on dark mode setting
    if st.session_state.get('dark_mode', False):
        st.markdown(base_css + dark_mode_css, unsafe_allow_html=True)
    else:
        st.markdown(base_css, unsafe_allow_html=True)