import os
from pathlib import Path

# Layout: <project>/training, <project>/models, <project>/modular (this app). The app reads the model and its
# metadata from the project's own models/ folder and only keeps what is specific to the dashboard in modular/assets.
APP_DIR = Path(__file__).resolve().parent.parent                    # .../modular
PROJECT_ROOT = Path(os.getenv("TELECOM_PROJECT_ROOT", APP_DIR.parent)).resolve()   # folder that holds training/ and models/
ROOT = APP_DIR                                                      # kept for older imports
ASSETS = APP_DIR / "assets"


def find(*candidates: Path) -> Path:
    """The first candidate that exists, else the first one (so error messages name the preferred location)."""
    return next((p for p in candidates if p.exists()), candidates[0])


DEFAULT_DATA = find(ASSETS / "default_sample.parquet", PROJECT_ROOT / "data" / "default_sample.parquet")
MODEL_PATH = find(PROJECT_ROOT / "models" / "mobile_data_consumption_pipeline.pkl", APP_DIR / "models" / "mobile_data_consumption_pipeline.pkl")

TARGET = "target_next_day_gb"
PRED = "pred_next_day_gb"
APP_NAME = "SA Telecom Analytics"

# Columns every uploaded file must have (daily usage plus customer profile).
REQUIRED_RAW = [
    "user_id", "date", "streaming_gb", "social_gb", "messaging_gb", "gaming_gb",
    "background_gb", "total_gb", "arpu", "congested", "plan_type", "device_type",
    "network_type", "age_group", "region", "contract_duration_months",
    "customer_tenure_months", "monthly_bill_zar", "support_calls_6months",
    "churn_probability", "churn_status",
]
# Columns built from daily usage. If an upload already has them, they are used as is.
ENGINEERED = [
    "lag_1d_total_gb", "lag_7d_total_gb", "rolling_7d_avg_gb", "rolling_30d_avg_gb",
    "delta_1d_gb", "lag_1d_streaming_gb", "lag_1d_social_gb", "lag_1d_gaming_gb",
    "lag_1d_messaging_gb",
]
# Not used by the model or any dashboard page. A file may leave them out.
OPTIONAL_RAW = ["arpu", "churn_status", "background_gb"]
MODEL_REQUIRED = [c for c in REQUIRED_RAW if c not in OPTIONAL_RAW]
CALENDAR = ["day_index", "day_of_week", "is_weekend", "day_of_month", "is_month_start", "is_month_end"]
# Rows missing any of these are removed, as in training. Other gaps are scored as unknown.
CRITICAL = ["age_group", "plan_type", "device_type", "network_type", "region", "lag_1d_total_gb",
            "rolling_7d_avg_gb", "rolling_30d_avg_gb"]

KNOWN = {
    "plan_type": ["Prepaid_Daily", "Prepaid_Monthly", "Postpaid_Basic", "Postpaid_Premium", "Postpaid_Unlimited"],
    "network_type": ["3G", "4G", "4G+", "5G"],
    "device_type": ["Basic_Phone", "Mid_Range", "Premium_Smartphone", "Tablet", "5G_Device"],
    "age_group": ["18-24", "25-34", "35-44", "45-54", "55+"],
}

NAVY, TEAL, TEAL_LIGHT, AMBER, GREY, LINE, BG = (
    "#0F1B2D", "#0E7C86", "#3FB7C1", "#E8833A", "#5B6B7F", "#E1E6EC", "#F3F5F7")

MODEL_INFO = find(PROJECT_ROOT / "models" / "model_info.json", ASSETS / "model_info.json")
REFERENCE_PROFILE = find(ASSETS / "reference_profile.json", PROJECT_ROOT / "models" / "reference_profile.json")
PREP_META = find(PROJECT_ROOT / "models" / "preparation_metadata.json", PROJECT_ROOT / "data" / "preparation_metadata.json",
                 ASSETS / "preparation_metadata.json")


def missing_files() -> list:
    """Files the app cannot start without, with where it looked. Empty when everything is in place."""
    need = {"the trained model": MODEL_PATH, "model_info.json": MODEL_INFO, "the default dataset": DEFAULT_DATA,
            "preparation_metadata.json": PREP_META}
    out = [f"{what}: {p}" for what, p in need.items() if not p.exists()]
    if not (PROJECT_ROOT / "training").is_dir():
        out.append(f"the training package (needed to open the saved model): {PROJECT_ROOT / 'training'}")
    return out

# Largest upload accepted, to protect memory on small hosts. Override with the MAX_UPLOAD_ROWS environment variable.
MAX_ROWS = int(os.getenv("MAX_UPLOAD_ROWS", "1000000"))
