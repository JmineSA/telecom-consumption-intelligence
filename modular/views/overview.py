import streamlit as st

from src import actions, charts, insights, kpis, report_pages, reports, state, theme
from src.theme import gb, int_, label, pct, rand

b = state.bundle()
df = b["df"]
st.title("Overview")
theme.data_label(b)

if df.empty:
    st.info("No records match the filters. Widen the period or select more regions, plans, or networks.")
    st.stop()

k = kpis.overview(df, b["prev"], b["threshold"])
cols = st.columns(5)

if k["avg_gb_prev"]:
    ch = k["avg_gb"] / k["avg_gb_prev"] - 1
    sub, tone = f"{pct(ch, True)} vs previous period", "good" if ch >= 0 else "flat"
else:
    sub, tone = "No earlier period in the data", "flat"
fc_ch = k["fc_avg"] / k["recent_avg"] - 1 if k["recent_avg"] else 0

theme.kpi(cols[0], "Total customers", int_(k["customers"]), "In the selected period", "flat")
theme.kpi(cols[1], "Data per customer per day", gb(k["avg_gb"]), sub, tone)
theme.kpi(cols[2], "Average monthly bill", rand(k["bill"]), "Per customer", "flat")
theme.kpi(cols[3], "Customers at churn risk", int_(k["at_risk"]),
          f"{pct(k['at_risk_pct'])} of customers, {rand(k['bill_at_risk'])} a month", "bad", accent="risk")
theme.kpi(cols[4], "Next-day forecast", f"{k['fc_total']:,.0f} GB",
          f"{pct(fc_ch, True)} per customer vs last 7 days", "flat")

st.write("")
left, right = st.columns([2, 1])
with left:
    st.subheader("Data usage: actual vs forecast")
    theme.show(charts.trend(df))
with right:
    st.subheader("Customers by plan")
    theme.show(charts.plan_mix(kpis.latest_per_customer(df)))

st.subheader("Needs attention")
rows = insights.overview_alerts(df, k, b["threshold"])
html = "".join(f'<div class="alert"><span class="tag">{t}</span><span>{m}</span></div>' for t, m in rows)
st.markdown(f'<div class="panel">{html}</div>', unsafe_allow_html=True)
st.caption("The next-day forecast uses each customer's latest record. Churn risk means churn probability "
           "at or above the threshold set in the sidebar.")

st.subheader("Business Actions")
st.caption("Suggested actions based on current forecast and business intelligence.")
cards = actions.overview_cards(b)
if cards:
    theme.action_cards(cards)
else:
    st.info("No recommendations meet the current thresholds. The rules can be changed under Business assumptions.")
st.caption(actions.FOOTNOTE)

reports.panel("overview", lambda: report_pages.overview(b), "Download this page as a report")
reports.panel("full", lambda: report_pages.full(b), "Download the full report (all pages)")
