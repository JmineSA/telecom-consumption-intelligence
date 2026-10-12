"""Plain-English insights and formatted customer lists, shared by pages and reports."""
from . import kpis
from .theme import int_, label, pct, rand


def overview_alerts(df, k, threshold):
    rows = []
    rd = kpis.region_demand(df)
    top = rd.index[0]
    rows.append(("Capacity", f"{top} is forecast to need {pct(rd.loc[top, 'demand_share'])} of next-day demand "
                 f"with {pct(rd.loc[top, 'customer_share'])} of customers."))
    rows.append(("Churn", f"{int_(k['at_risk'])} customers have a churn probability of {threshold:.0%} or more. "
                 f"Their bills add up to {rand(k['bill_at_risk'])} a month."))
    ce = kpis.congestion_error(df)
    if ce and ce["congested"] is not None and ce["normal"] is not None:
        rows.append(("Network", f"{pct(ce['share'])} of records were on congested networks. Forecasts miss by "
                     f"{ce['congested']:.2f} GB there, against {ce['normal']:.2f} GB otherwise."))
    return rows


def topup_table(hits):
    act = hits["plan_type"].map(lambda p: "Offer a data top-up" if str(p).startswith("Prepaid") else "Offer a larger bundle")
    t = hits.assign(plan=hits["plan_type"].map(label), action=act)[
        ["user_id", "plan", "region", "streak", "avg_gap", "next_forecast", "monthly_bill_zar", "action"]]
    t.columns = ["Customer", "Plan", "Region", "Days above forecast", "Extra GB per day", "Next-day forecast (GB)",
                 "Monthly bill (R)", "Suggested action"]
    return t.round(2)


def retention_table(hits, threshold):
    act = hits["churn_probability"].map(lambda p: "Retention call and loyalty offer" if p >= threshold else "Send a usage nudge")
    t = hits.assign(plan=hits["plan_type"].map(label), action=act)[
        ["user_id", "plan", "region", "streak", "avg_gap", "churn_probability", "monthly_bill_zar", "action"]]
    t.columns = ["Customer", "Plan", "Region", "Days below forecast", "GB below forecast per day",
                 "Churn probability", "Monthly bill (R)", "Suggested action"]
    return t.round(2)
