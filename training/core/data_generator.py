"""
Telecom Consumption Intelligence — Synthetic Data Generator (v2)

South African telecom context:
- Currency: ZAR (South African Rand)
- Plans priced to match real Vodacom / MTN / Telkom / Cell C / Rain tiers
- Regions: Gauteng, Western Cape, KZN, Eastern Cape

Outputs:
- data/raw/users.csv             (one row per user)
- data/raw/daily_usage.parquet   (one row per user per active day)
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
SEED = 42
N_USERS = 10_000
N_DAYS = 90
START_DATE = pd.Timestamp("2026-01-01")
DRIFT_DAY = 45  # policy change mid-window

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)


# ------------------------------------------------------------------
# 1. USER PROFILES
# ------------------------------------------------------------------
def generate_users(n: int = N_USERS) -> pd.DataFrame:
    age_groups = rng.choice(
        ["18-24", "25-34", "35-44", "45-54", "55+"],
        n, p=[0.25, 0.30, 0.20, 0.15, 0.10],
    )

    plan_types = rng.choice(
        ["Prepaid_Daily", "Prepaid_Monthly", "Postpaid_Basic",
         "Postpaid_Premium", "Postpaid_Unlimited"],
        n, p=[0.20, 0.25, 0.20, 0.20, 0.15],
    )

    device_types = rng.choice(
        ["Basic_Phone", "Mid_Range", "Premium_Smartphone", "5G_Device", "Tablet"],
        n, p=[0.10, 0.35, 0.30, 0.20, 0.05],
    )

    network_types = rng.choice(
        ["3G", "4G", "5G", "4G+"],
        n, p=[0.15, 0.45, 0.25, 0.15],
    )

    contract_duration = rng.choice(
        [1, 3, 6, 12, 24], n, p=[0.15, 0.15, 0.20, 0.30, 0.20],
    )

    customer_tenure = rng.choice(
        [1, 3, 6, 12, 18, 24, 36, 48, 60],
        n, p=[0.10, 0.12, 0.15, 0.18, 0.15, 0.12, 0.08, 0.05, 0.05],
    )

    support_calls = rng.poisson(lam=2, size=n)

    region = rng.choice(
        ["Gauteng", "Western Cape", "KZN", "Eastern Cape"],
        n, p=[0.40, 0.25, 0.20, 0.15],
    )

    # ------------------------------------------------------------------
    # REALISTIC SOUTH AFRICAN MONTHLY BILL (ZAR)
    # Ranges based on current Vodacom / MTN / Telkom / Cell C / Rain plans
    # ------------------------------------------------------------------
    monthly_bill_zar = np.select(
        [plan_types == "Prepaid_Daily",      # R50  – R250
         plan_types == "Prepaid_Monthly",    # R150 – R400
         plan_types == "Postpaid_Basic",     # R300 – R600
         plan_types == "Postpaid_Premium"],  # R600 – R1,100
        [rng.uniform(50, 250, n),
         rng.uniform(150, 400, n),
         rng.uniform(300, 600, n),
         rng.uniform(600, 1100, n)],
        default=rng.uniform(900, 1800, n),   # Postpaid_Unlimited: R900 – R1,800
    )

    user_ids = [f"SUB{1_000_000 + i}" for i in range(n)]

    return pd.DataFrame({
        "user_id": user_ids,
        "age_group": age_groups,
        "plan_type": plan_types,
        "device_type": device_types,
        "network_type": network_types,
        "contract_duration_months": contract_duration,
        "customer_tenure_months": customer_tenure,
        "monthly_bill_zar": np.round(monthly_bill_zar, 2),
        "support_calls_6months": support_calls,
        "region": region,
    })


# ------------------------------------------------------------------
# 2. INTRINSIC BEHAVIOUR BASELINES (per user)
# ------------------------------------------------------------------
AGE_MULT = {"18-24": 1.4, "25-34": 1.3, "35-44": 1.0, "45-54": 0.7, "55+": 0.4}
PLAN_MULT = {
    "Prepaid_Daily": 0.6, "Prepaid_Monthly": 0.8,
    "Postpaid_Basic": 1.0, "Postpaid_Premium": 1.3, "Postpaid_Unlimited": 1.6,
}
DEVICE_MULT = {
    "Basic_Phone": 0.3, "Mid_Range": 0.8,
    "Premium_Smartphone": 1.2, "5G_Device": 1.4, "Tablet": 1.1,
}
NETWORK_MULT = {"3G": 0.7, "4G": 1.0, "5G": 1.3, "4G+": 1.15}


def assign_baselines(users: pd.DataFrame) -> pd.DataFrame:
    combined = (
        users["age_group"].map(AGE_MULT)
        * users["plan_type"].map(PLAN_MULT)
        * users["device_type"].map(DEVICE_MULT)
        * users["network_type"].map(NETWORK_MULT)
    )

    users["streaming_base"] = rng.gamma(1.5, 0.8, len(users)) * combined
    users["social_base"] = rng.gamma(2.0, 0.6, len(users)) * combined
    users["messaging_base"] = rng.gamma(1.0, 0.4, len(users)) * combined
    users["gaming_base"] = rng.gamma(0.8, 0.5, len(users)) * combined

    # Churn
    base_prob = 0.15
    age_factor = users["age_group"].map(
        {"18-24": 1.5, "25-34": 1.3, "35-44": 1.0, "45-54": 0.7, "55+": 0.5}
    )
    plan_factor = users["plan_type"].map(
        {"Prepaid_Daily": 2.0, "Prepaid_Monthly": 1.5, "Postpaid_Basic": 1.0,
         "Postpaid_Premium": 0.7, "Postpaid_Unlimited": 0.5}
    )
    tenure_factor = np.select(
        [users["customer_tenure_months"] <= 3,
         users["customer_tenure_months"] <= 6,
         users["customer_tenure_months"] <= 12,
         users["customer_tenure_months"] <= 24,
         users["customer_tenure_months"] <= 36],
        [2.0, 1.5, 1.2, 1.0, 0.7],
        default=0.5,
    )
    support_factor = np.select(
        [users["support_calls_6months"] == 0,
         users["support_calls_6months"] <= 2,
         users["support_calls_6months"] <= 4,
         users["support_calls_6months"] <= 6],
        [0.8, 1.0, 1.5, 2.0],
        default=3.0,
    )

    churn_prob = np.clip(
        base_prob * age_factor * plan_factor * tenure_factor * support_factor,
        0.01, 0.95,
    )
    users["churn_probability"] = np.round(churn_prob, 3)
    users["churn_status"] = rng.binomial(1, churn_prob)

    users["churn_day"] = np.where(
        users["churn_status"] == 1,
        rng.integers(30, N_DAYS, len(users)),
        -1,
    )

    return users


# ------------------------------------------------------------------
# 3. DAY-LEVEL GENERATION
# ------------------------------------------------------------------
DOW_MULT = {0: 0.95, 1: 0.90, 2: 0.92, 3: 0.95, 4: 1.15, 5: 1.30, 6: 1.20}

# ARPU per GB by service (ZAR) — SA telecom benchmarks
ARPU_PER_GB = {"Streaming": 72.12, "Gaming": 76.57,
               "Social": 75.74, "Messaging": 75.80}

BACKGROUND_GB = {
    "Basic_Phone": 0.05, "Mid_Range": 0.10,
    "Premium_Smartphone": 0.20, "5G_Device": 0.30, "Tablet": 0.15,
}


def generate_daily_usage(users: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(START_DATE, periods=N_DAYS, freq="D")
    records = []

    uids = users["user_id"].values
    streaming_base = users["streaming_base"].values
    social_base = users["social_base"].values
    messaging_base = users["messaging_base"].values
    gaming_base = users["gaming_base"].values
    churn_day = users["churn_day"].values
    plan = users["plan_type"].values
    device = users["device_type"].values
    network = users["network_type"].values
    age = users["age_group"].values
    region = users["region"].values

    for day_idx, date in enumerate(dates):
        dow = date.dayofweek
        is_weekend = int(dow >= 5)
        dow_mult = DOW_MULT[dow]

        # Drift on day 45 — policy change
        drift_mult = np.ones(len(users))
        if day_idx >= DRIFT_DAY:
            drift_mult = np.where(
                np.char.startswith(plan.astype(str), "Prepaid"), 1.20, 0.95
            )

        active_mask = (churn_day == -1) | (day_idx < churn_day)

        # Congestion — more likely on weekends/peak, SUPPRESSES usage
        congestion_p = np.where(is_weekend, 0.35, 0.15)
        congested = rng.random(len(users)) < congestion_p
        congestion_factor = np.where(congested, 0.65, 1.0)

        noise = rng.lognormal(0, 0.30, len(users))

        base_mult = dow_mult * drift_mult * noise * congestion_factor

        streaming_gb = streaming_base * 3.0 * base_mult
        social_gb = social_base * 1.0 * base_mult
        messaging_gb = messaging_base * 0.2 * base_mult
        gaming_gb = gaming_base * 2.0 * base_mult
        background_gb = np.array([BACKGROUND_GB[d] for d in device]) * base_mult

        total_gb = streaming_gb + social_gb + messaging_gb + gaming_gb + background_gb

        arpu = (
            streaming_gb * ARPU_PER_GB["Streaming"]
            + social_gb * ARPU_PER_GB["Social"]
            + messaging_gb * ARPU_PER_GB["Messaging"]
            + gaming_gb * ARPU_PER_GB["Gaming"]
        ) * rng.normal(1.0, 0.05, len(users))

        for i in range(len(users)):
            if not active_mask[i]:
                continue
            records.append({
                "user_id": uids[i],
                "date": date,
                "day_index": day_idx,
                "day_of_week": dow,
                "is_weekend": is_weekend,
                "streaming_gb": round(max(streaming_gb[i], 0), 4),
                "social_gb": round(max(social_gb[i], 0), 4),
                "messaging_gb": round(max(messaging_gb[i], 0), 4),
                "gaming_gb": round(max(gaming_gb[i], 0), 4),
                "background_gb": round(max(background_gb[i], 0), 4),
                "total_gb": round(max(total_gb[i], 0), 4),
                "arpu": round(max(arpu[i], 0), 2),
                "congested": int(congested[i]),
                "plan_type": plan[i],
                "device_type": device[i],
                "network_type": network[i],
                "age_group": age[i],
                "region": region[i],
            })

    return pd.DataFrame(records)


# ------------------------------------------------------------------
# 4. INJECT MESSINESS
# ------------------------------------------------------------------
def inject_messiness(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1% duplicate rows
    dupes = df.sample(frac=0.01, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)

    # 3% missing in non-critical columns
    for col in ["network_type", "age_group", "region"]:
        mask = rng.random(len(df)) < 0.03
        df.loc[mask, col] = np.nan

    # Inconsistent region encoding
    mask = df["region"] == "Gauteng"
    df.loc[mask, "region"] = rng.choice(
        ["Gauteng", "gauteng", "GP"], size=mask.sum(), p=[0.7, 0.2, 0.1]
    )

    return df


# ------------------------------------------------------------------
# 5. MAIN
# ------------------------------------------------------------------
def main():
    print("Generating users...")
    users = generate_users()
    users = assign_baselines(users)

    print("Generating daily usage across 90 days...")
    usage = generate_daily_usage(users)

    print("Injecting realistic messiness...")
    usage = inject_messiness(usage)

    users.drop(columns=["churn_day"]).to_csv(RAW_DIR / "users.csv", index=False)
    usage.to_parquet(RAW_DIR / "daily_usage.parquet", index=False)

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"Users:              {len(users):,}")
    print(f"Daily usage rows:   {len(usage):,}")
    print(f"Date range:         {usage['date'].min().date()} → {usage['date'].max().date()}")
    print(f"Churn rate:         {users['churn_status'].mean() * 100:.1f}%")
    print(f"Congestion rate:    {usage['congested'].mean() * 100:.1f}%")
    print(f"\nMonthly bill (ZAR) summary:")
    print(users["monthly_bill_zar"].describe().round(2))
    print(f"\nUsage stats:")
    print(usage["total_gb"].describe().round(3))


if __name__ == "__main__":
    main()