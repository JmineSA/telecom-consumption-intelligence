"""
Streamlit page configuration and global settings.
"""
from pathlib import Path

# Project paths
MODULAR_DIR = Path(__file__).resolve().parent.parent  # modular/
PROJECT_ROOT = MODULAR_DIR.parent                     # repo root

MODELS_DIR = PROJECT_ROOT / "models"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
INSIGHTS_DIR = REPORTS_DIR / "insights"

MODEL_PATH = MODELS_DIR / "mobile_data_consumption_pipeline.pkl"
MODEL_INFO_PATH = MODELS_DIR / "model_info.json"
TEST_PATH = DATA_PROCESSED / "test.parquet"
TRAIN_PATH = DATA_PROCESSED / "train.parquet"
PREP_META_PATH = DATA_PROCESSED / "preparation_metadata.json"
BUSINESS_SUMMARY_PATH = REPORTS_DIR / "business_summary.txt"

# Streamlit page config
PAGE_TITLE = "Telecom Forecasting"
PAGE_ICON = "📶"
PAGE_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Model target
TARGET_COLUMN = "target_next_day_gb"

# Categorical options (must match training schema)
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
PLAN_TYPES = ["Prepaid_Daily", "Prepaid_Monthly", "Postpaid_Basic",
              "Postpaid_Premium", "Postpaid_Unlimited"]
NETWORK_TYPES = ["3G", "4G", "4G+", "5G"]
DEVICE_TYPES = ["Basic_Phone", "Mid_Range", "Premium_Smartphone",
                "5G_Device", "Tablet"]