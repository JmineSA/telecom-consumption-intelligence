"""
Constants for the forecasting app.

The feature list matches what the trained pipeline expects — do NOT
change without retraining the model.
"""

# The exact input features the pipeline consumes.
# Includes `measurement_date` because the pipeline's DateFeatures transformer
# needs it to extract day_of_week and month.
EXPECTED_FEATURES = [
    "measurement_date",
    "age_group",
    "plan_type",
    "network_type",
    "device_type",
    "hours_streaming",
    "hours_social",
    "hours_messaging",
    "hours_gaming",
    "is_peak_hour_user",
    "is_weekend",
]

# Nav labels
NAV_OVERVIEW = "🏠 Overview"
NAV_PREDICT = "🎯 Predict"
NAV_INSIGHTS = "📊 Insights"

NAV_ITEMS = [NAV_OVERVIEW, NAV_PREDICT, NAV_INSIGHTS]

# Chart filenames (must match reports/insights/)
INSIGHT_CHARTS = [
    ("Model Performance", "01_model_performance.png"),
    ("Congestion Breakdown", "02_congestion.png"),
    ("Feature Correlation", "03_feature_correlation.png"),
    ("Permutation Importance", "04_permutation_importance.png"),
    ("Segment Analysis", "05_segments.png"),
    ("Revenue Opportunity", "06_revenue_opportunity.png"),
]