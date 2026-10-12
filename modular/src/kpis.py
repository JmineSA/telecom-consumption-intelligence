"""Business KPIs. Every number is calculated from the loaded data."""
import numpy as np
import pandas as pd

from .config import PRED, TARGET


def latest_per_customer(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df.groupby("user_id")["date"].idxmax()]


def overview(df, prev, threshold) -> dict:
    cust = latest_per_customer(df)  # one row per customer, most recent record
    risk = cust[cust["churn_probability"] >= threshold]
    recent = df[df["date"] > df["date"].max() - pd.Timedelta(days=7)]
    k = {
        "customers": len(cust),
        "avg_gb": df["total_gb"].mean(),
        "avg_gb_prev": prev["total_gb"].mean() if len(prev) else None,
        "bill": cust["monthly_bill_zar"].mean(),
        "at_risk": len(risk),
        "at_risk_pct": len(risk) / len(cust),
        "bill_at_risk": risk["monthly_bill_zar"].sum(),
        "fc_total": cust[PRED].sum(),
        "fc_avg": cust[PRED].mean(),
        "recent_avg": recent["total_gb"].mean(),
        "fc_dates": (cust["forecast_date"].min(), cust["forecast_date"].max()),
    }
    return k


def region_demand(df) -> pd.DataFrame:
    cust = latest_per_customer(df)
    g = cust.groupby("region").agg(forecast_gb=(PRED, "sum"), customers=("user_id", "count"))
    g["demand_share"] = g["forecast_gb"] / g["forecast_gb"].sum()
    g["customer_share"] = g["customers"] / g["customers"].sum()
    return g.sort_values("forecast_gb", ascending=False)


def congestion_error(df):
    """Average forecast error (GB) on congested vs normal days. None without actuals."""
    d = df.dropna(subset=[TARGET])
    if d.empty or d["congested"].nunique() < 2:
        return None
    mae = d.assign(ae=d["residual"].abs()).groupby("congested")["ae"].mean()
    return {"congested": mae.get(1), "normal": mae.get(0), "share": d["congested"].mean()}


def forecast_by(df, col) -> pd.Series:
    """Next-day forecast (GB) summed over customers, using each customer's latest record."""
    return latest_per_customer(df).groupby(col)[PRED].sum().sort_values(ascending=False)


def persistent_gap(df, gb_threshold, min_days, direction=1) -> pd.DataFrame:
    """Customers whose actual use beat the forecast by more than gb_threshold for min_days in a row.

    direction=1: using more than forecast (top-up candidates).
    direction=-1: using less than forecast (disengaging).
    Only the streak that is still running at the customer's latest actual day counts.
    """
    d = df.dropna(subset=[TARGET]).sort_values(["user_id", "date"])
    if d.empty:
        return d.head(0)
    flag = direction * d["residual"] > gb_threshold
    same = d["user_id"].eq(d["user_id"].shift()) & (d["date"].diff().dt.days == 1)
    cont = flag & flag.shift(fill_value=False) & same
    gid = (~cont).cumsum()
    d = d.assign(streak=flag.groupby(gid).cumsum(),
                 avg_gap=d["residual"].groupby(gid).transform("mean") * direction)
    last = d.groupby("user_id").tail(1)
    hits = last[last["streak"] >= min_days]
    nxt = latest_per_customer(df).set_index("user_id")[PRED]
    return hits.assign(next_forecast=hits["user_id"].map(nxt)).sort_values(["streak", "avg_gap"], ascending=False)


def revenue(df, threshold) -> dict:
    cust = latest_per_customer(df)
    risk = cust[cust["churn_probability"] >= threshold]
    return {"total": cust["monthly_bill_zar"].sum(), "arpu": cust["monthly_bill_zar"].mean(),
            "at_risk": risk["monthly_bill_zar"].sum(), "at_risk_n": len(risk), "cust": cust, "risk": risk}


def plan_economics(df) -> pd.DataFrame:
    cust = latest_per_customer(df)
    g = cust.groupby("plan_type").agg(customers=("user_id", "count"), revenue=("monthly_bill_zar", "sum"),
                                      avg_bill=("monthly_bill_zar", "mean"))
    g["avg_gb_day"] = df.groupby("plan_type")["total_gb"].mean()
    g["rand_per_gb"] = g["avg_bill"] / (g["avg_gb_day"] * 30)
    return g.sort_values("revenue", ascending=False)


def region_table(df, threshold) -> pd.DataFrame:
    cust = latest_per_customer(df)
    g = cust.groupby("region").agg(customers=("user_id", "count"), revenue=("monthly_bill_zar", "sum"),
                                   forecast_gb=(PRED, "sum"),
                                   at_risk_pct=("churn_probability", lambda s: (s >= threshold).mean()))
    g["avg_gb_day"] = df.groupby("region")["total_gb"].mean()
    g["congested_share"] = df.groupby("region")["congested"].mean()
    return g


def metrics(d) -> dict:
    """MAE, RMSE, R2 and average bias (actual minus forecast) on rows that have actuals."""
    d = d.dropna(subset=[TARGET])
    if d.empty:
        return {}
    err = d["residual"]
    ss_tot = ((d[TARGET] - d[TARGET].mean()) ** 2).sum()
    return {"n": len(d), "mae": err.abs().mean(), "rmse": float(np.sqrt((err ** 2).mean())),
            "r2": 1 - (err ** 2).sum() / ss_tot if ss_tot else float("nan"), "bias": err.mean()}


def error_by(d, col) -> pd.Series:
    d = d.dropna(subset=[TARGET])
    return d.assign(ae=d["residual"].abs()).groupby(col)["ae"].mean().sort_values(ascending=False)
