"""One report per dashboard page, plus a full report that joins them."""
import json

import streamlit as st

from . import insights, kpis
from .config import AMBER, MODEL_INFO, TARGET, TEAL
from .reports import Report, make_meta
from .theme import gb, int_, label, pct, rand


def _empty(title, b, why="No records match the filters."):
    r = Report(title, make_meta(b))
    r.text("", [why])
    return r


def overview(b):
    df, ss = b["df"], st.session_state
    if df.empty:
        return _empty("Overview", b)
    k = kpis.overview(df, b["prev"], b["threshold"])
    rep = Report("Overview", make_meta(b))
    sub = f"{pct(k['avg_gb'] / k['avg_gb_prev'] - 1, True)} vs previous period" if k["avg_gb_prev"] else "No earlier period"
    fc_ch = k["fc_avg"] / k["recent_avg"] - 1 if k["recent_avg"] else 0
    rep.kpis([("Total customers", int_(k["customers"]), ""), ("Data per customer per day", gb(k["avg_gb"]), sub),
              ("Average monthly bill", rand(k["bill"]), ""),
              ("Customers at churn risk", int_(k["at_risk"]), f"{pct(k['at_risk_pct'])} of customers"),
              ("Next-day forecast", f"{k['fc_total']:,.0f} GB", f"{pct(fc_ch, True)} per customer vs last 7 days")])
    rep.text("Needs attention", [f"{t}: {m}" for t, m in insights.overview_alerts(df, k, b["threshold"])])
    g = df.groupby("forecast_date").agg(Actual=(TARGET, "mean"), Forecast=("pred_next_day_gb", "mean"))
    rep.line("Average data per customer per day (GB): actual vs forecast", g)
    cust = kpis.latest_per_customer(df)
    rep.bars("Customers by plan", cust["plan_type"].value_counts(), TEAL, "{:,.0f}")
    return rep


def forecast(b):
    df, ss = b["df"], st.session_state
    if df.empty:
        return _empty("Tomorrows Forecast", b)
    k = kpis.overview(df, b["prev"], b["threshold"])
    cap = k["fc_total"] * (1 + ss["buffer"] / 100)
    gap = kpis.persistent_gap(df, ss["topup_gb"], ss["topup_days"], 1) if b["report"]["has_actuals"] else None
    rep = Report("Tomorrows Forecast", make_meta(b))
    rep.kpis([("Forecast for the next day", f"{k['fc_total']:,.0f} GB", f"{gb(k['fc_avg'])} per customer"),
              ("Capacity to provision", f"{cap:,.0f} GB", f"Includes a {ss['buffer']}% safety buffer"),
              ("Customers using more than expected", "n/a" if gap is None else int_(len(gap)),
               f"{ss['topup_gb']:g} GB above forecast, {ss['topup_days']} days in a row")])
    for field, title in (("region", "Forecast by region (GB)"), ("plan_type", "Forecast by plan (GB)"),
                         ("network_type", "Forecast by network (GB)")):
        rep.bars(title, kpis.forecast_by(df, field), TEAL, "{:,.0f}", " GB")
    if gap is not None and not gap.empty:
        rep.table("Customers using more than expected", insights.topup_table(gap))
    return rep


def revenue(b):
    df, ss = b["df"], st.session_state
    if df.empty:
        return _empty("Revenue Analysis", b)
    r = kpis.revenue(df, b["threshold"])
    gap = kpis.persistent_gap(df, ss["topup_gb"], ss["topup_days"], 1) if b["report"]["has_actuals"] else None
    topup = None if gap is None else float((gap["avg_gap"] * 30 * ss["price_gb"] * ss["takeup"] / 100).sum())
    rep = Report("Revenue Analysis", make_meta(b))
    rep.kpis([("Monthly revenue", rand(r["total"]), ""), ("Average revenue per customer", rand(r["arpu"]), "Monthly bill"),
              ("Potential top-up revenue", "n/a" if topup is None else rand(topup),
               f"{ss['takeup']}% take-up at R {ss['price_gb']} per GB (assumptions)"),
              ("Revenue at risk", rand(r["at_risk"]), f"{int_(r['at_risk_n'])} customers")])
    econ = kpis.plan_economics(df)
    rep.bars("Monthly revenue by plan (R)", econ["revenue"], TEAL, "R {:,.0f}")
    risk = r["risk"].groupby("region")["monthly_bill_zar"].sum().sort_values(ascending=False)
    rep.bars("Revenue at risk by region (R)", risk, AMBER, "R {:,.0f}")
    t = econ.assign(plan=[label(i) for i in econ.index])[["plan", "customers", "revenue", "avg_bill", "avg_gb_day", "rand_per_gb"]]
    t.columns = ["Plan", "Customers", "Monthly revenue (R)", "Average bill (R)", "GB per customer per day", "Revenue per GB (R)"]
    rep.table("What each plan earns", t.round(2))
    return rep


def geography(b):
    df = b["df"]
    if df.empty:
        return _empty("Geography", b)
    t = kpis.region_table(df, b["threshold"])
    rep = Report("Geography", make_meta(b))
    rep.bars("Data per customer per day by region (GB)", t["avg_gb_day"].sort_values(ascending=False), TEAL, "{:.2f}", " GB")
    rep.bars("Monthly revenue by region (R)", t["revenue"].sort_values(ascending=False), TEAL, "R {:,.0f}")
    rep.bars("Customers at churn risk by region", t["at_risk_pct"].sort_values(ascending=False), AMBER, "{:.1%}")
    show = t.reset_index().rename(columns={"region": "Region", "customers": "Customers", "revenue": "Monthly revenue (R)",
                                           "forecast_gb": "Next-day forecast (GB)", "at_risk_pct": "At churn risk",
                                           "avg_gb_day": "GB per customer per day", "congested_share": "On congested networks"})
    rep.table("All regions", show.round(3))
    return rep


def customers(b):
    df, ss = b["df"], st.session_state
    if df.empty:
        return _empty("Customer Insights", b)
    rep = Report("Customer Insights", make_meta(b))
    usage = df.groupby("plan_type")["total_gb"].mean().sort_values(ascending=False)
    rep.bars("Data per customer per day by plan (GB)", usage, TEAL, "{:.1f}", " GB")
    if b["report"]["has_actuals"]:
        more = kpis.persistent_gap(df, ss["topup_gb"], ss["topup_days"], 1)
        less = kpis.persistent_gap(df, ss["retain_gb"], ss["retain_days"], -1)
        rep.text("", [f"{len(more):,} customers are using more than expected ({ss['topup_gb']:g} GB above forecast, "
                      f"{ss['topup_days']} days in a row).",
                      f"{len(less):,} customers are using less than expected ({ss['retain_gb']:g} GB below forecast, "
                      f"{ss['retain_days']} days in a row)."])
        if not more.empty:
            rep.table("Using more than expected", insights.topup_table(more))
        if not less.empty:
            rep.table("Using less than expected", insights.retention_table(less, b["threshold"]))
    return rep


def _explanations(rep, ss):
    """Feature importance and SHAP, when they have been calculated on the Model Monitoring page."""
    import pandas as pd
    from . import explain
    key = (ss["version"], ss["model_name"])
    imp = ss.get("imp_cache", {}).get(key)
    res = ss.get("shap_cache", {}).get(key)
    if imp is not None:
        top = imp.head(10).clip(lower=0)
        rep.bars("Feature importance: error added when a feature is shuffled (GB)", top.rename(index=label), TEAL, "{:.2f}", " GB")
    if res is not None:
        summ = explain.shap_summary(res)
        top = summ.head(10).set_index("feature")["size"].rename(index=label)
        rep.bars("SHAP: average effect of each feature on a forecast (GB)", top, TEAL, "{:.2f}", " GB")
        rep.text("What SHAP says", [explain.shap_sentence(summ, res["base"]),
                                    "SHAP values are in GB and add up to the gap between a forecast and the sample average. "
                                    f"They describe how the model behaves, not what causes usage. Calculated on {len(res['values']):,} sampled rows."])
        t = summ.head(10).assign(feature=lambda x: x["feature"].map(label), size=lambda x: x["size"].round(2))
        rep.table("How each feature pushes the forecast",
                  t.rename(columns={"feature": "Feature", "size": "Average effect (GB)", "note": "How it pushes the forecast"})
                  [["Feature", "Average effect (GB)", "How it pushes the forecast"]])
    if imp is None and res is None:
        rep.text("", ["Feature importance and SHAP were not calculated when this report was made. "
                      "Calculate them on the Model Monitoring page, then prepare the report again."])


def monitoring(b):
    df, ss = b["df"], st.session_state
    rep = Report("Model Monitoring", make_meta(b))
    if not b["report"]["has_actuals"]:
        rep.text("", ["This file has no next-day actuals, so forecast accuracy cannot be measured."])
        return rep
    ev = df if ss["eval_from"] is None else df[df["date"] >= ss["eval_from"]]
    ev = ev.dropna(subset=[TARGET])
    if ev.empty:
        return _empty("Model Monitoring", b)
    ref = json.loads(MODEL_INFO.read_text())["val_metrics"]
    m = kpis.metrics(ev)
    ratio = m["mae"] / ref["mae"]
    health = "Healthy" if ratio <= 1.10 else "Watch" if ratio <= 1.25 else "Action needed"
    rep.kpis([("Model health", health, f"{ratio:.2f} times the error at training"),
              ("Average error (MAE)", f"{m['mae']:.2f} GB", f"At training: {ref['mae']:.2f} GB"),
              ("Typical large error (RMSE)", f"{m['rmse']:.2f} GB", f"At training: {ref['rmse']:.2f} GB"),
              ("Variance explained (R2)", f"{m['r2']:.2f}", f"At training: {ref['r2']:.2f}")])
    rep.text("", [f"Measured on {m['n']:,} rows with actuals. Average bias {m['bias']:+.2f} GB "
                  "(positive means actual use is above forecast)."])
    e = ev.assign(ae=ev["residual"].abs()).groupby("forecast_date")["ae"].mean().to_frame("Average error (GB)")
    rep.line("Average error over time (GB)", e)
    rep.bars("Average error by plan (GB)", kpis.error_by(ev, "plan_type"), AMBER, "{:.2f}", " GB")
    rep.bars("Average error by region (GB)", kpis.error_by(ev, "region"), AMBER, "{:.2f}", " GB")
    _explanations(rep, ss)
    if ss.get("retrain_result"):
        import pandas as pd
        res, _ = ss["retrain_result"]
        t = pd.DataFrame({k: {"Average error (GB)": v["mae"], "Typical large error (GB)": v["rmse"], "R2": v["r2"],
                              "Rows tested": v["n"]} for k, v in res.items()}).T.round(3).reset_index()
        rep.table("Original vs retrained model", t.rename(columns={"index": "Model"}))
    return rep


def data_checks(b):
    import pandas as pd
    q = st.session_state["quality"]
    rep = Report("Data Checks", make_meta({"report": st.session_state["report"], "source": q.source}))
    status = "READY FOR SCORING" if q.ready else "NOT READY FOR SCORING"
    rep.kpis([("Dataset status", status, q.source), ("Passed", int_(q.count("pass")), ""),
              ("Warnings", int_(q.count("warn")), ""), ("Critical", int_(q.count("crit")), "")])
    labels = {"pass": "Passed", "warn": "Warning", "crit": "Critical"}
    rep.table("All checks", pd.DataFrame([(c.group, c.name, labels[c.status], c.finding, c.impact, c.action) for c in q.checks],
                                         columns=["Group", "Check", "Status", "Finding", "Why it matters", "What to do"]))
    if q.actions_taken:
        rep.text("What was cleaned", q.actions_taken)
    rep.text("", [f"Dataset Status: {status}"])
    return rep


def full(b):
    rep = Report("Full Report", make_meta(b))
    for name, fn in (("Overview", overview), ("Tomorrows Forecast", forecast), ("Revenue Analysis", revenue),
                     ("Geography", geography), ("Customer Insights", customers), ("Model Monitoring", monitoring), ("Data Checks", data_checks)):
        rep.heading(name)
        rep.extend(fn(b))
    return rep
