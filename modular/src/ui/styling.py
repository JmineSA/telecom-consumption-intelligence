"""
CSS styling for the application
"""
import streamlit as st


def load_css():
    """Load all CSS styles"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            box-sizing: border-box;
        }
        
        .stApp {
            background: #f8fafc;
        }
        
        /* Modern Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.4);
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
            border: 1px solid #f1f5f9;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .rec-card:hover {
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            transform: translateY(-4px);
            border-color: #e8edf3;
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
            border-top: 1px solid #f1f5f9;
            color: #94a3b8;
            font-size: 0.8rem;
            text-align: center;
        }
        
        /* Tab Styling */
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
        
        /* Button Styling */
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
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        
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
    </style>
    """, unsafe_allow_html=True)