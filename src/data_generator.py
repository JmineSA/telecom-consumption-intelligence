import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# ============================================
# REALISTIC TELECOM USER BEHAVIOR SIMULATION
# ============================================

# Number of subscribers (scalable)
n_users = 10000

# User IDs (like actual subscriber IDs - alphanumeric)
user_ids = [f"SUB{np.random.randint(1000000, 9999999)}" for _ in range(n_users)]

# ============================================
# 1. USER DEMOGRAPHICS (Hidden but influencing behavior)
# ============================================

# Age groups influence usage patterns
age_groups = np.random.choice(
    ['18-24', '25-34', '35-44', '45-54', '55+'],
    n_users,
    p=[0.25, 0.30, 0.20, 0.15, 0.10]  # Younger users are heavier data consumers
)

# Plan types (like real telecom plans)
plan_types = np.random.choice(
    ['Prepaid_Daily', 'Prepaid_Monthly', 'Postpaid_Basic', 'Postpaid_Premium', 'Postpaid_Unlimited'],
    n_users,
    p=[0.20, 0.25, 0.20, 0.20, 0.15]
)

# Device type affects data consumption
device_types = np.random.choice(
    ['Basic_Phone', 'Mid_Range', 'Premium_Smartphone', '5G_Device', 'Tablet'],
    n_users,
    p=[0.10, 0.35, 0.30, 0.20, 0.05]
)

# Network type available to user
network_types = np.random.choice(
    ['3G', '4G', '5G', '4G+'],
    n_users,
    p=[0.15, 0.45, 0.25, 0.15]
)

# ============================================
# 2. BASE USAGE PATTERNS (Hours per day)
# ============================================

# Create base usage influenced by demographics
def generate_base_usage(age, plan, device, network):
    """Generate realistic base hours based on user profile"""
    
    # Base hours influenced by age
    age_multiplier = {
        '18-24': 1.4,    # Heavy users
        '25-34': 1.3,    # Very active
        '35-44': 1.0,    # Baseline
        '45-54': 0.7,    # Moderate
        '55+': 0.4       # Light users
    }[age]
    
    # Plan type multiplier (unlimited users consume more)
    plan_multiplier = {
        'Prepaid_Daily': 0.6,
        'Prepaid_Monthly': 0.8,
        'Postpaid_Basic': 1.0,
        'Postpaid_Premium': 1.3,
        'Postpaid_Unlimited': 1.6
    }[plan]
    
    # Device multiplier (better devices = more usage)
    device_multiplier = {
        'Basic_Phone': 0.3,
        'Mid_Range': 0.8,
        'Premium_Smartphone': 1.2,
        '5G_Device': 1.4,
        'Tablet': 1.1
    }[device]
    
    # Network multiplier (faster network = more consumption)
    network_multiplier = {
        '3G': 0.7,
        '4G': 1.0,
        '5G': 1.3,
        '4G+': 1.15
    }[network]
    
    combined_multiplier = age_multiplier * plan_multiplier * device_multiplier * network_multiplier
    
    # Base hours per activity type (in hours/day)
    streaming_base = np.random.gamma(shape=1.5, scale=0.8) * combined_multiplier
    social_base = np.random.gamma(shape=2.0, scale=0.6) * combined_multiplier
    messaging_base = np.random.gamma(shape=1.0, scale=0.4) * combined_multiplier
    gaming_base = np.random.gamma(shape=0.8, scale=0.5) * combined_multiplier
    
    return streaming_base, social_base, messaging_base, gaming_base

# Generate base usage for all users
base_usage = np.array([generate_base_usage(age, plan, device, network) 
                       for age, plan, device, network in zip(age_groups, plan_types, device_types, network_types)])

streaming_base, social_base, messaging_base, gaming_base = base_usage.T

# ============================================
# 3. TIME-BASED VARIATIONS (Peak hours & Weekend effects)
# ============================================

# Is this measurement during peak hours? (6-9 PM)
is_peak_hour = np.random.choice([0, 1], n_users, p=[0.7, 0.3])  # 30% of measurements during peak

# Is it weekend?
is_weekend = np.random.choice([0, 1], n_users, p=[0.72, 0.28])  # ~2/7 days are weekend

# Peak hour multiplier (20-40% increase)
peak_multiplier = np.where(is_peak_hour == 1, 
                          np.random.uniform(1.2, 1.4, n_users), 
                          1.0)

# Weekend multiplier (15-35% increase)
weekend_multiplier = np.where(is_weekend == 1, 
                             np.random.uniform(1.15, 1.35, n_users), 
                             1.0)

# ============================================
# 4. RANDOM VARIATION & NOISE (Real-world randomness)
# ============================================

# Individual daily variation (±30%)
daily_variation = np.random.uniform(0.7, 1.3, (n_users, 4))

# Special events (5% of users have unusual patterns)
special_event = np.random.choice([1, 0], (n_users, 4), p=[0.05, 0.95])
special_event_multiplier = np.where(special_event == 1, 
                                   np.random.uniform(2.0, 5.0, (n_users, 4)), 
                                   1.0)

# ============================================
# 5. FINAL HOURS CALCULATION
# ============================================

hours_streaming = streaming_base * peak_multiplier * weekend_multiplier * daily_variation[:, 0] * special_event_multiplier[:, 0]
hours_social = social_base * peak_multiplier * weekend_multiplier * daily_variation[:, 1] * special_event_multiplier[:, 1]
hours_messaging = messaging_base * peak_multiplier * weekend_multiplier * daily_variation[:, 2] * special_event_multiplier[:, 2]
hours_gaming = gaming_base * peak_multiplier * weekend_multiplier * daily_variation[:, 3] * special_event_multiplier[:, 3]

# Cap at reasonable daily limits (24 hours)
hours_streaming = np.clip(hours_streaming, 0, 8)
hours_social = np.clip(hours_social, 0, 6)
hours_messaging = np.clip(hours_messaging, 0, 4)
hours_gaming = np.clip(hours_gaming, 0, 6)

# Round to 2 decimal places
hours_streaming = np.round(hours_streaming, 2)
hours_social = np.round(hours_social, 2)
hours_messaging = np.round(hours_messaging, 2)
hours_gaming = np.round(hours_gaming, 2)

# ============================================
# 6. BACKGROUND DATA (Always present)
# ============================================

# Background data depends on device and network
base_background = np.where(device_types == 'Basic_Phone', 
                          np.random.uniform(10, 30, n_users),
                          np.where(device_types == 'Mid_Range',
                                  np.random.uniform(30, 60, n_users),
                                  np.random.uniform(50, 100, n_users)))

# Background increases with better network
network_bg_multiplier = {
    '3G': 0.7,
    '4G': 1.0,
    '5G': 1.5,
    '4G+': 1.3
}
bg_multiplier = np.array([network_bg_multiplier[net] for net in network_types])

background_data_mb = base_background * bg_multiplier * peak_multiplier * weekend_multiplier
background_data_mb = np.round(background_data_mb + np.random.normal(0, 5, n_users), 2)
background_data_mb = np.clip(background_data_mb, 5, 200)

# ============================================
# 7. CREATE DATASET 1: user_activity
# ============================================

user_activity = pd.DataFrame({
    'user_id': user_ids,
    'hours_streaming': hours_streaming,
    'hours_social': hours_social,
    'hours_messaging': hours_messaging,
    'hours_gaming': hours_gaming,
    'background_data_mb': background_data_mb,
    'is_peak_hour_user': is_peak_hour,
    'is_weekend': is_weekend,
    # Additional columns for more realistic analysis
    'age_group': age_groups,
    'plan_type': plan_types,
    'device_type': device_types,
    'network_type': network_types,
    'measurement_date': [datetime.now().date() - timedelta(days=np.random.randint(0, 30)) for _ in range(n_users)]
})

# ============================================
# 8. DATA CONSUMPTION RATES (MB per hour) - REALISTIC TELECOM VALUES
# ============================================

# Data consumption rates based on quality (typical telecom values)
def get_streaming_rate(network):
    """Streaming rates based on network capability"""
    rates = {
        '3G': np.random.uniform(300, 500),     # SD quality
        '4G': np.random.uniform(700, 1200),    # HD quality
        '5G': np.random.uniform(1500, 2500),   # 4K capable
        '4G+': np.random.uniform(1000, 1800)   # Full HD
    }
    return rates[network]

def get_social_rate(network):
    """Social media data consumption (video autoplay affects this)"""
    rates = {
        '3G': np.random.uniform(80, 150),
        '4G': np.random.uniform(150, 300),
        '5G': np.random.uniform(250, 400),
        '4G+': np.random.uniform(200, 350)
    }
    return rates[network]

# Calculate individual consumption rates
streaming_rates = np.array([get_streaming_rate(net) for net in network_types])
social_rates = np.array([get_social_rate(net) for net in network_types])
messaging_rates = np.random.uniform(5, 20, n_users)  # Messaging uses very little data
gaming_rates = np.random.uniform(40, 200, n_users)   # Gaming varies by game type

# ============================================
# 9. CALCULATE TOTAL DATA USAGE
# ============================================

# Calculate data from each activity
streaming_data = hours_streaming * streaming_rates
social_data = hours_social * social_rates
messaging_data = hours_messaging * messaging_rates
gaming_data = hours_gaming * gaming_rates

# Add quality adjustment factor (premium plans get HD video by default)
is_premium = np.isin(plan_types, ['Postpaid_Premium', 'Postpaid_Unlimited'])
quality_multiplier = np.where(
    is_premium,
    np.random.uniform(1.3, 1.8, n_users),  # HD/4K streaming
    1.0
)

streaming_data = streaming_data * quality_multiplier

# Total data in MB
total_data_mb = (streaming_data + social_data + messaging_data + gaming_data + background_data_mb)

# Add some random variation (±10%)
total_data_mb = total_data_mb * np.random.uniform(0.9, 1.1, n_users)

# Round to 2 decimal places
total_data_mb = np.round(total_data_mb, 2)
total_data_gb = np.round(total_data_mb / 1024, 3)

# ============================================
# 10. CREATE DATASET 2: user_data_usage
# ============================================

user_data_usage = pd.DataFrame({
    'user_id': user_ids,
    'total_data_mb': total_data_mb,
    'total_data_gb': total_data_gb,
    'streaming_data_mb': np.round(streaming_data, 2),
    'social_data_mb': np.round(social_data, 2),
    'messaging_data_mb': np.round(messaging_data, 2),
    'gaming_data_mb': np.round(gaming_data, 2),
    'data_usage_category': pd.cut(total_data_gb, 
                                   bins=[0, 0.5, 2, 5, 10, float('inf')],
                                   labels=['Very_Light', 'Light', 'Moderate', 'Heavy', 'Power_User'])
})

# ============================================
# 11. VALIDATION & QUALITY CHECKS
# ============================================

# Ensure no missing values
assert user_activity.isnull().sum().sum() == 0, "Missing values found in user_activity"
assert user_data_usage.isnull().sum().sum() == 0, "Missing values found in user_data_usage"

# Ensure user_ids match perfectly
assert all(user_activity['user_id'] == user_data_usage['user_id']), "User IDs don't match"

# ============================================
# 12. DISPLAY DATASETS
# ============================================

print("=" * 80)
print("DATASET 1: USER_ACTIVITY (Raw Behavioral Data)")
print("=" * 80)
print(f"Shape: {user_activity.shape}")
print(f"\nFirst 10 rows:")
print(user_activity.head(10))
print(f"\nData Types:\n{user_activity.dtypes}")
print(f"\nSummary Statistics:")
print(user_activity.describe())

print("\n" + "=" * 80)
print("DATASET 2: USER_DATA_USAGE (Derived Target Data)")
print("=" * 80)
print(f"Shape: {user_data_usage.shape}")
print(f"\nFirst 10 rows:")
print(user_data_usage.head(10))
print(f"\nData Types:\n{user_data_usage.dtypes}")
print(f"\nSummary Statistics:")
print(user_data_usage.describe())

print("\n" + "=" * 80)
print("DATA QUALITY INSIGHTS")
print("=" * 80)
print(f"Total unique users: {user_activity['user_id'].nunique()}")
print(f"Date range: {user_activity['measurement_date'].min()} to {user_activity['measurement_date'].max()}")
print(f"\nPlan distribution:")
print(user_activity['plan_type'].value_counts(normalize=True).round(3) * 100)
print(f"\nData usage by category:")
print(user_data_usage['data_usage_category'].value_counts().sort_index())

# ============================================
# 13. EXPORT TO CSV (Ready for Database)
# ============================================

user_activity.to_csv('user_activity.csv', index=False)
user_data_usage.to_csv('user_data_usage.csv', index=False)
print("\n✅ Datasets exported to CSV files:")
print("   - user_activity.csv")
print("   - user_data_usage.csv")

print("\n" + "=" * 80)
print("🎯 MACHINE LEARNING READY")
print("=" * 80)
print("""
Features available for ML regression:
- Hours streaming, social, messaging, gaming
- Background data
- Time features (peak hour, weekend)
- Demographics (age group, plan type)
- Device and network characteristics

Target variable: total_data_gb or total_data_mb

This structure allows for:
✅ Feature engineering (create ratios, interaction terms)
✅ Time-series analysis (with measurement_date)
✅ Cohort analysis (by plan type, device)
✅ Anomaly detection (unusual usage patterns)
✅ Customer segmentation (by usage category)
""")