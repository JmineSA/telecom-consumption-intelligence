# src/pipelines/preprocessing_pipeline.py
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
from training.core.custom_transformers import DropColumns, CyclicalDayOfWeek


DROP_COLS = [
    "user_id",
    "date",
    "total_gb",
    "streaming_gb",
    "social_gb",
    "messaging_gb",
    "gaming_gb",
    "background_gb",
    "arpu",
    "region",
    "is_month_start",
    "is_month_end",
    "churn_status",
]


ORDINAL_COLS = ["age_group", "plan_type", "network_type", "device_type"]

AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55+"]
PLAN_ORDER = [
    "Prepaid_Daily",
    "Prepaid_Monthly",
    "Postpaid_Basic",
    "Postpaid_Premium",
    "Postpaid_Unlimited",
]
NETWORK_ORDER = ["3G", "4G", "4G+", "5G"]
DEVICE_ORDER = [
    "Basic_Phone",
    "Mid_Range",
    "Premium_Smartphone",
    "Tablet",
    "5G_Device",
]


NUMERIC_COLS = [
    "day_index",
    "day_of_week",
    "is_weekend",
    "day_of_month",
    "congested",
    "contract_duration_months",
    "customer_tenure_months",
    "monthly_bill_zar",
    "support_calls_6months",
    "churn_probability",
    "lag_1d_total_gb",
    "lag_7d_total_gb",
    "rolling_7d_avg_gb",
    "rolling_30d_avg_gb",
    "delta_1d_gb",
    "lag_1d_streaming_gb",
    "lag_1d_social_gb",
    "lag_1d_gaming_gb",
    "lag_1d_messaging_gb",
]


def build_pipeline():
    ordinal_encoder = OrdinalEncoder(
        categories=[
            AGE_ORDER,
            PLAN_ORDER,
            NETWORK_ORDER,
            DEVICE_ORDER,
        ],
        handle_unknown="use_encoded_value",
        unknown_value=-1,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("ord", ordinal_encoder, ORDINAL_COLS),
            ("num", "passthrough", NUMERIC_COLS),
        ],
        verbose_feature_names_out=False,
        remainder="drop",
    )

    pipeline = Pipeline(steps=[
        ("drop_cols", DropColumns(DROP_COLS)),
        ("cyclical_dow", CyclicalDayOfWeek(keep_original=True)),
        ("encoding", preprocessor),
    ])

    return pipeline
