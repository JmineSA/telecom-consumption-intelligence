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

# Contract duration in months (influences churn)
contract_duration = np.random.choice(
    [1, 3, 6, 12, 24],
    n_users,
    p=[0.15, 0.15, 0.20, 0.30, 0.20]
)

# Customer tenure in months (how long they've been with the company)
customer_tenure = np.random.choice(
    [1, 3, 6, 12, 18, 24, 36, 48, 60],
    n_users,
    p=[0.10, 0.12, 0.15, 0.18, 0.15, 0.12, 0.08, 0.05, 0.05]
)

# Monthly bill amount in USD
monthly_bill = np.where(
    plan_types == 'Prepaid_Daily',
    np.random.uniform(5, 15, n_users),
    np.where(plan_types == 'Prepaid_Monthly',
             np.random.uniform(15, 30, n_users),
             np.where(plan_types == 'Postpaid_Basic',
                      np.random.uniform(30, 50, n_users),
                      np.where(plan_types == 'Postpaid_Premium',
                               np.random.uniform(50, 90, n_users),
                               np.random.uniform(80, 120, n_users))))
)

# Number of customer support calls in last 6 months
support_calls = np.random.poisson(lam=2, size=n_users)

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
# 11. CREATE DATASET 3: user_churn (NEW!)
# ============================================

# Calculate churn probability based on realistic factors
def calculate_churn_probability(age_group, plan_type, tenure, support_calls, 
                                total_data_gb, monthly_bill, device_type, network_type):
    """
    Calculate churn probability based on telecom industry patterns.
    
    High churn risk factors:
    - Prepaid customers (no contract lock-in)
    - High support calls (frustrated customers)
    - Low tenure (new customers still evaluating)
    - High bill relative to usage (poor value perception)
    - Old devices/network (poor experience)
    - Very low or very high usage (dissatisfaction)
    """
    
    # Base churn probability
    base_prob = 0.15  # 15% industry average churn rate
    
    # Age factor (younger customers churn more)
    age_factor = {
        '18-24': 1.5,   # High churn - always looking for deals
        '25-34': 1.3,   # Above average churn
        '35-44': 1.0,   # Baseline
        '45-54': 0.7,   # More loyal
        '55+': 0.5      # Most loyal
    }[age_group]
    
    # Plan factor (prepaid churns more, contract less)
    plan_factor = {
        'Prepaid_Daily': 2.0,      # Very easy to leave
        'Prepaid_Monthly': 1.5,    # Easy to leave
        'Postpaid_Basic': 1.0,     # Some commitment
        'Postpaid_Premium': 0.7,   # Satisfied with premium
        'Postpaid_Unlimited': 0.5  # Very satisfied
    }[plan_type]
    
    # Tenure factor (longer tenure = more loyal)
    if tenure <= 3:
        tenure_factor = 2.0     # New customer - high churn risk
    elif tenure <= 6:
        tenure_factor = 1.5     # Still evaluating
    elif tenure <= 12:
        tenure_factor = 1.2     # Settling in
    elif tenure <= 24:
        tenure_factor = 1.0     # Established
    elif tenure <= 36:
        tenure_factor = 0.7     # Loyal
    else:
        tenure_factor = 0.5     # Very loyal
    
    # Support calls factor (more calls = more frustration)
    if support_calls == 0:
        support_factor = 0.8    # Happy customer
    elif support_calls <= 2:
        support_factor = 1.0    # Normal
    elif support_calls <= 4:
        support_factor = 1.5    # Some frustration
    elif support_calls <= 6:
        support_factor = 2.0    # Frustrated
    else:
        support_factor = 3.0    # Very frustrated
    
    # Bill-to-usage ratio (value perception)
    # High bill with low usage = poor value → high churn
    if total_data_gb > 0:
        cost_per_gb = monthly_bill / (total_data_gb * 30)  # Monthly estimate
        if cost_per_gb > 10:  # Very expensive per GB
            value_factor = 2.0
        elif cost_per_gb > 5:
            value_factor = 1.5
        elif cost_per_gb > 2:
            value_factor = 1.0
        else:
            value_factor = 0.7  # Good value
    else:
        value_factor = 1.0
    
    # Device/Network factor (old tech = poor experience)
    tech_factor = 1.0
    if device_type == 'Basic_Phone':
        tech_factor = 1.3  # Outdated device
    if network_type == '3G':
        tech_factor *= 1.3  # Slow network
    
    # Usage pattern factor (extreme usage patterns indicate dissatisfaction)
    if total_data_gb < 0.1:  # Barely using service
        usage_factor = 1.8
    elif total_data_gb > 15:  # Extremely heavy usage (might switch for better deal)
        usage_factor = 1.3
    else:
        usage_factor = 1.0
    
    # Calculate final probability
    churn_prob = (base_prob * age_factor * plan_factor * tenure_factor * 
                  support_factor * value_factor * tech_factor * usage_factor)
    
    # Cap probability between 0.01 and 0.95
    churn_prob = np.clip(churn_prob, 0.01, 0.95)
    
    return churn_prob

# Calculate churn probability for each user
churn_probabilities = np.array([
    calculate_churn_probability(age, plan, tenure, calls, gb, bill, device, network)
    for age, plan, tenure, calls, gb, bill, device, network in 
    zip(age_groups, plan_types, customer_tenure, support_calls, 
        total_data_gb, monthly_bill, device_types, network_types)
])

# Determine churn status based on probability
churn_status = np.random.binomial(1, churn_probabilities)

# Churn reason assignment (only for churned customers)
def assign_churn_reason(plan_type, support_calls, monthly_bill, total_data_gb, tenure):
    """Assign realistic churn reasons based on user profile"""
    
    reasons_pool = []
    weights = []
    
    # Price sensitivity (higher for prepaid and high bills)
    if plan_type in ['Prepaid_Daily', 'Prepaid_Monthly']:
        reasons_pool.append('Price Too High')
        weights.append(0.3)
    
    if monthly_bill > 70:
        reasons_pool.append('Better Competitor Offer')
        weights.append(0.25)
    
    # Service quality
    if support_calls > 3:
        reasons_pool.append('Poor Customer Service')
        weights.append(0.25)
    
    # Network quality
    reasons_pool.append('Network Quality Issues')
    weights.append(0.15)
    
    # Low usage
    if total_data_gb < 0.5:
        reasons_pool.append('Service Not Needed')
        weights.append(0.2)
    
    # Relocation
    reasons_pool.append('Relocation/Moving')
    weights.append(0.1)
    
    # Normalize weights
    weights = np.array(weights) / sum(weights)
    
    return np.random.choice(reasons_pool, p=weights)

churn_reasons = [
    assign_churn_reason(plan, calls, bill, gb, tenure) if churned else None
    for plan, calls, bill, gb, tenure, churned in 
    zip(plan_types, support_calls, monthly_bill, total_data_gb, customer_tenure, churn_status)
]

# Create churn dataset
user_churn = pd.DataFrame({
    'user_id': user_ids,
    'customer_tenure_months': customer_tenure,
    'contract_duration_months': contract_duration,
    'monthly_bill_usd': np.round(monthly_bill, 2),
    'support_calls_6months': support_calls,
    'churn_probability': np.round(churn_probabilities, 3),
    'churn_status': churn_status,  # 0 = Stayed, 1 = Churned
    'churn_reason': churn_reasons,
    'churn_risk_category': pd.cut(churn_probabilities, 
                                   bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                   labels=['Very_Low', 'Low', 'Medium', 'High', 'Very_High'])
})

# ============================================
# 12. VALIDATION & QUALITY CHECKS
# ============================================

# Ensure no missing values (except churn_reason for non-churned)
assert user_activity.isnull().sum().sum() == 0, "Missing values found in user_activity"
assert user_data_usage.isnull().sum().sum() == 0, "Missing values found in user_data_usage"
assert user_churn[['user_id', 'churn_status', 'churn_probability']].isnull().sum().sum() == 0, "Missing values in critical churn columns"

# Ensure user_ids match perfectly across all datasets
assert all(user_activity['user_id'] == user_data_usage['user_id']), "User IDs don't match: activity vs usage"
assert all(user_activity['user_id'] == user_churn['user_id']), "User IDs don't match: activity vs churn"

# Validate churn logic
assert user_churn['churn_status'].isin([0, 1]).all(), "Invalid churn status values"
assert (user_churn['churn_probability'] >= 0).all() and (user_churn['churn_probability'] <= 1).all(), "Invalid probability range"

# ============================================
# 13. DISPLAY DATASETS
# ============================================

print("=" * 80)
print("DATASET 1: USER_ACTIVITY (Raw Behavioral Data)")
print("=" * 80)
print(f"Shape: {user_activity.shape}")
print(f"\nFirst 5 rows:")
print(user_activity.head())
print(f"\nData Types:\n{user_activity.dtypes}")

print("\n" + "=" * 80)
print("DATASET 2: USER_DATA_USAGE (Derived Target Data)")
print("=" * 80)
print(f"Shape: {user_data_usage.shape}")
print(f"\nFirst 5 rows:")
print(user_data_usage.head())

print("\n" + "=" * 80)
print("DATASET 3: USER_CHURN (Churn Prediction Data) 🆕")
print("=" * 80)
print(f"Shape: {user_churn.shape}")
print(f"\nFirst 5 rows:")
print(user_churn.head())
print(f"\nData Types:\n{user_churn.dtypes}")
print(f"\nChurn Summary Statistics:")
print(user_churn.describe())

print("\n" + "=" * 80)
print("DATA QUALITY INSIGHTS")
print("=" * 80)
print(f"Total unique users: {user_activity['user_id'].nunique()}")
print(f"Date range: {user_activity['measurement_date'].min()} to {user_activity['measurement_date'].max()}")

print(f"\n📊 Churn Rate: {user_churn['churn_status'].mean() * 100:.1f}%")
print(f"   - Stayed: {(1 - user_churn['churn_status'].mean()) * 100:.1f}%")
print(f"   - Churned: {user_churn['churn_status'].mean() * 100:.1f}%")

print(f"\nChurn Risk Distribution:")
print(user_churn['churn_risk_category'].value_counts().sort_index())

print(f"\nTop Churn Reasons (among churned users):")
churned_users = user_churn[user_churn['churn_status'] == 1]
print(churned_users['churn_reason'].value_counts())

print(f"\nChurn Rate by Plan Type:")
churn_by_plan = user_churn.groupby(user_activity['plan_type'])['churn_status'].mean() * 100
print(churn_by_plan.round(2))

print(f"\nImpact of Support Calls on Churn:")
user_churn['support_calls_group'] = pd.cut(user_churn['support_calls_6months'], 
                                            bins=[-1, 0, 2, 4, 10],
                                            labels=['0 calls', '1-2 calls', '3-4 calls', '5+ calls'])
print(user_churn.groupby('support_calls_group')['churn_status'].mean().round(3) * 100)

# ============================================
# 14. EXPORT TO CSV (Ready for Database)
# ============================================

user_activity.to_csv('user_activity.csv', index=False)
user_data_usage.to_csv('user_data_usage.csv', index=False)
user_churn.to_csv('user_churn.csv', index=False)

print("\n" + "=" * 80)
print("Datasets exported to CSV files:")
print("=" * 80)
print("   1. user_activity.csv    - Raw behavioral data")
print("   2. user_data_usage.csv  - Derived usage metrics")
print("   3. user_churn.csv       - Churn prediction data 🆕")

print("\n" + "=" * 80)
print("MACHINE LEARNING READY - THREE DATASETS")
print("=" * 80)
print("""
DATASET 1: user_activity (Features for ML)
   - Regression: Predict data consumption
   - Clustering: Segment users by behavior

DATASET 2: user_data_usage (Targets for Regression)
   - Target: total_data_gb
   - Classification: data_usage_category

DATASET 3: user_churn (Classification Target)
   - Binary Classification: churn_status (0/1)
   - Probability Prediction: churn_probability
   - Multi-class: churn_reason prediction

🔗 Join all three on: user_id

 Churn Analysis Ideas:
   - Feature importance: What drives churn?
   - Early warning system: Flag high-risk users
   - Retention ROI: Which users are worth saving?
   - A/B testing: Test retention offers on high-risk segments
""")

# ============================================
# 15. SAMPLE ANALYSIS QUERIES (Bonus)
# ============================================

print("\n" + "=" * 80)
print(" QUICK ANALYTICS PREVIEW")
print("=" * 80)

# Correlation between usage and churn
print("\nData Usage vs Churn Rate:")
churn_by_usage = user_churn.groupby(user_data_usage['data_usage_category'])['churn_status'].mean() * 100
print(churn_by_usage.round(2))

# High-value customers at risk
high_value_at_risk = (
    (user_churn['churn_probability'] > 0.5) & 
    (user_data_usage['total_data_gb'] > 5)
).sum()
print(f"\n High-value customers at risk (high usage + high churn probability): {high_value_at_risk}")

# Loyal customers
loyal_customers = (
    (user_churn['churn_probability'] < 0.2) & 
    (user_churn['customer_tenure_months'] > 24)
).sum()
print(f" Loyal customers (low churn + long tenure): {loyal_customers}")