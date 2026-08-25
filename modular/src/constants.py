"""
Constants and mapping dictionaries for the application
"""
from typing import Dict, Any

# Feature definitions
EXPECTED_FEATURES = [
    'age_group', 'plan_type', 'network_type',
    'device_type_Basic_Phone', 'device_type_Mid_Range',
    'device_type_Premium_Smartphone', 'device_type_Tablet',
    'hours_streaming', 'hours_social', 'hours_messaging', 'hours_gaming',
    'is_peak_hour_user', 'is_weekend'
]

# Categorical mappings
AGE_MAPPING: Dict[str, int] = {
    '18-24': 0, '25-34': 1, '35-44': 2, '45-54': 3, '55+': 4
}

PLAN_MAPPING: Dict[str, int] = {
    'Prepaid_Daily': 0, 'Prepaid_Monthly': 1,
    'Postpaid_Basic': 2, 'Postpaid_Premium': 3, 'Postpaid_Unlimited': 4
}

NETWORK_MAPPING: Dict[str, int] = {
    '3G': 0, '4G': 1, '4G+': 2, '5G': 3
}

DEVICE_TYPES = ['Basic_Phone', 'Mid_Range', 'Premium_Smartphone', 'Tablet']

# Reverse mappings
REV_AGE = {v: k for k, v in AGE_MAPPING.items()}
REV_PLAN = {v: k for k, v in PLAN_MAPPING.items()}
REV_NETWORK = {v: k for k, v in NETWORK_MAPPING.items()}

# Pricing benchmarks (ZAR)
PRICING_BENCHMARKS = {
    'Postpaid': {'base_rate_per_gb': 49.00, 'monthly_fee': 99.00},
    'Prepaid': {'base_rate_per_gb': 69.00, 'monthly_fee': 29.00},
    'Prepaid_Daily': {'base_rate_per_gb': 99.00, 'monthly_fee': 15.00},
    'Postpaid_Basic': {'base_rate_per_gb': 59.00, 'monthly_fee': 79.00}
}

# Usage thresholds
USAGE_THRESHOLDS = {
    'low': 2,
    'medium': 5,
    'high': 10
}

# Risk categories
RISK_CATEGORIES = {
    'low': {'label': 'Low Risk', 'color': '#16a34a', 'badge': 'badge-low'},
    'medium': {'label': 'Medium Risk', 'color': '#d97706', 'badge': 'badge-medium'},
    'high': {'label': 'High Risk', 'color': '#dc2626', 'badge': 'badge-high'}
}

# Default UI colors
COLORS = {
    'primary': '#1a237e',
    'secondary': '#3949ab',
    'success': '#22c55e',
    'warning': '#eab308',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'dark': '#0f172a',
    'light': '#f8fafc',
    'gray': '#64748b'
}

# Tab configurations - UPDATED WITH ALL TABS
TABS = {
    'command_centre': {'icon': '🏠', 'label': 'Command Centre'},
    'predict': {'icon': '🎯', 'label': 'Predict & Explain'},
    'analytics': {'icon': '📊', 'label': 'Analytics'},
    'forecast': {'icon': '🔮', 'label': 'Forecast'},
    'segmentation': {'icon': '👥', 'label': 'Segmentation'},
    'cohorts': {'icon': '📊', 'label': 'Cohort Analysis'},
    'ab_testing': {'icon': '🧪', 'label': 'A/B Testing'},
    'revenue': {'icon': '💰', 'label': 'Revenue'},
    'network': {'icon': '📡', 'label': 'Network'},
    'maintenance': {'icon': '🔧', 'label': 'Maintenance'},
    'model': {'icon': '🧠', 'label': 'Model'},
    'data_explorer': {'icon': '📊', 'label': 'Data Explorer'},
    'monitoring': {'icon': '📋', 'label': 'Monitoring'}
}

# Get tab keys in order
TAB_KEYS = list(TABS.keys())