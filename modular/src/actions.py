"""Business Actions: decision-support cards built only from numbers the dashboard already calculates.

Each function returns a card dict, or None when the data does not support the recommendation.
A card is {"state", "title", "text", "metrics": [(label, value)], "note"}.
States: opportunity, attention, risk, monitor.
"""
import json

import streamlit as st

from . import kpis
from .config import MODEL_INFO
from .theme import int_, label, pct, rand

FOOTNOTE = ("Recommendations are based on model outputs and configured business assumptions and are intended for "
            "decision support. The data is simulated and not connected to a live operator.")
ELEVATED = 1.03     # a region counts as high demand when forecast use per customer is 3% above average
ERROR_WATCH = 1.10  # same health threshold as Model Monitoring


def _gap(b, kind):
    ss = st.session_state
    if not b["report"]["has_actuals"]:
        return None
    if kind == "more":
        g = kpis.persistent_gap(b["df"], ss["topup_gb"], ss["topup_days"], 1)
    else:
        g = kpis.persistent_gap(b["df"], ss["retain_gb"], ss["retain_days"], -1)
    return None if g.empty else g


def top_up(b):
    ss = st.session_state
    g = _gap(b, "more")
    if g is None:
        return None
    revenue = float((g["avg_gap"] * 30 * ss["price_gb"] * ss["takeup"] / 100).sum())
    return {"state": "opportunity", "title": "Target potential top-up customers",
            "text": (f"Subscribers using {ss['topup_gb']:g} GB or more above forecast for {ss['topup_days']} days in a row "
                     "may represent an opportunity for targeted top-up or plan recommendations."),
            "metrics": [("Subscribers", int_(len(g))), ("Extra data per day", f"{g['avg_gap'].sum():,.0f} GB"),
                        ("Potential revenue a month", rand(revenue))],
            "note": f"Uses R {ss['price_gb']} per GB and a {ss['takeup']}% take-up rate from Business assumptions."}


def under_use(b):
    ss = st.session_state
    g = _gap(b, "less")
    if g is None:
        return None
    at_risk = int((g["churn_probability"] >= b["threshold"]).sum())
    return {"state": "attention", "title": "Review lower-than-expected usage",
            "text": (f"Subscribers using {ss['retain_gb']:g} GB or more below forecast for {ss['retain_days']} days in a row "
                     "may indicate under-used plans or early disengagement. Consider reviewing their plans or including "
                     "them in retention outreach."),
            "metrics": [("Subscribers", int_(len(g))), ("Below forecast per day", f"{g['avg_gap'].sum():,.0f} GB"),
                        ("Also at churn risk", int_(at_risk))],
            "note": ""}


def capacity(b):
    df, ss = b["df"], st.session_state
    rd = kpis.region_demand(df)
    cong = kpis.region_table(df, b["threshold"])["congested_share"]
    overall_cong = float(df["congested"].mean())
    overall_pc = rd["forecast_gb"].sum() / rd["customers"].sum()
    rd = rd.assign(per_customer=rd["forecast_gb"] / rd["customers"], congested=cong)
    hit = rd[(rd["per_customer"] >= ELEVATED * overall_pc) & (rd["congested"] > overall_cong)]
    if hit.empty:
        return None
    hit = hit.sort_values("per_customer", ascending=False)
    name, r = hit.index[0], hit.iloc[0]
    more = f" {len(hit) - 1} other region(s) also meet this condition." if len(hit) > 1 else ""
    return {"state": "risk", "title": f"Prioritise {name} for capacity review",
            "text": (f"{name} has above-average expected consumption and a higher share of congested records, which may "
                     f"require additional capacity planning attention.{more}"),
            "metrics": [("Forecast per customer", f"{r['per_customer']:.1f} GB ({pct(r['per_customer'] / overall_pc - 1, True)})"),
                        ("On congested networks", f"{pct(r['congested'])} vs {pct(overall_cong)}"),
                        ("Capacity with buffer", f"{r['forecast_gb'] * (1 + ss['buffer'] / 100):,.0f} GB")],
            "note": f"Buffer of {ss['buffer']}% from Business assumptions. Congestion is the share of records on congested networks."}


def reliability(b):
    ss = st.session_state
    if not b["report"]["has_actuals"]:
        return None
    ev = b["df"] if ss["eval_from"] is None else b["df"][b["df"]["date"] >= ss["eval_from"]]
    ev = ev.dropna(subset=["target_next_day_gb"])
    if ev.empty:
        return None
    ref = json.loads(MODEL_INFO.read_text())["val_metrics"]["mae"]
    m = kpis.metrics(ev)
    worst = kpis.error_by(ev, "plan_type")
    high = m["mae"] / ref > ERROR_WATCH
    return {"state": "risk" if high else "monitor",
            "title": "Review lower-confidence forecasts" if high else "Monitor forecast reliability",
            "text": ("Forecast error is above the level measured at training. Consider treating forecasts with additional "
                     "caution when supporting operational decisions." if high else
                     "Forecasts with higher historical error should be treated with additional caution when supporting "
                     "operational decisions. The segment with the highest error is shown for reference."),
            "metrics": [("Average error", f"{m['mae']:.2f} GB"), ("At training", f"{ref:.2f} GB"),
                        ("Highest-error plan", f"{label(worst.index[0])}: {worst.iloc[0]:.2f} GB")],
            "note": "Error is measured on rows with known next-day actuals. See Model Monitoring."}


def at_risk_revenue(b):
    r = kpis.revenue(b["df"], b["threshold"])
    if r["at_risk_n"] == 0:
        return None
    return {"state": "risk", "title": "Prioritise at-risk revenue for review",
            "text": (f"Subscribers with a churn probability of {b['threshold']:.0%} or more account for part of monthly "
                     "revenue. Consider prioritising them for retention review."),
            "metrics": [("Subscribers", int_(r["at_risk_n"])), ("Monthly revenue", rand(r["at_risk"])),
                        ("Share of revenue", pct(r["at_risk"] / r["total"]) if r["total"] else "n/a")],
            "note": "Churn probability comes from the data. The threshold is set in the sidebar."}


def overview_cards(b):
    return [c for c in (top_up(b), under_use(b), capacity(b), reliability(b)) if c]


def revenue_cards(b):
    return [c for c in (top_up(b), at_risk_revenue(b)) if c]
