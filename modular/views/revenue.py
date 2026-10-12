import streamlit as st

from src import actions, charts, kpis, report_pages, reports, state, theme
from src.config import AMBER, TEAL
from src.theme import int_, label, pct, rand

ss = st.session_state
b = state.bundle()
df = b["df"]
st.title("Revenue Analysis")
theme.data_label(b, checks=False)

if df.empty:
    st.info("No records match the filters. Widen the period or select more regions, plans, or networks.")
    st.stop()

r = kpis.revenue(df, b["threshold"])
gap = kpis.persistent_gap(df, ss["topup_gb"], ss["topup_days"], 1) if b["report"]["has_actuals"] else None
topup = None if gap is None else float((gap["avg_gap"] * 30 * ss["price_gb"] * ss["takeup"] / 100).sum())

cols = st.columns(4)
theme.kpi(cols[0], "Monthly revenue", rand(r["total"]), f"From {int_(len(r['cust']))} customers' bills", "flat")
theme.kpi(cols[1], "Average revenue per customer", rand(r["arpu"]), "Monthly bill", "flat")
theme.kpi(cols[2], "Potential top-up revenue", "n/a" if topup is None else rand(topup),
          f"{ss['takeup']}% take-up at R {ss['price_gb']} per GB, 30 days", "flat")
theme.kpi(cols[3], "Revenue at risk", rand(r["at_risk"]),
          f"{int_(r['at_risk_n'])} customers at {b['threshold']:.0%} churn risk or more", "bad", accent="risk")

st.write("")
left, right = st.columns(2)
with left:
    st.subheader("Monthly revenue by plan")
    econ = kpis.plan_economics(df)
    theme.show(charts.hbar(econ["revenue"], TEAL, "R {:,.0f}"))
with right:
    st.subheader("Revenue at risk by region")
    risk = r["risk"].groupby("region")["monthly_bill_zar"].sum().sort_values(ascending=False)
    if risk.empty:
        st.info("No customers are above the churn-risk threshold.")
    else:
        theme.show(charts.hbar(risk, AMBER, "R {:,.0f}"))

st.subheader("What each plan earns")
t = econ.assign(plan=[label(i) for i in econ.index])[["plan", "customers", "revenue", "avg_bill", "avg_gb_day", "rand_per_gb"]]
t.columns = ["Plan", "Customers", "Monthly revenue (R)", "Average bill (R)", "GB per customer per day", "Revenue per GB (R)"]
st.dataframe(t.round(1), hide_index=True)
st.caption("Potential top-up revenue = extra GB per day for customers on the top-up rule x 30 days x price per GB x take-up rate. "
           "Price and take-up are assumptions you set in the sidebar, not figures from the data. "
           "Revenue per GB = average bill divided by 30 days of average usage.")

st.subheader("Business Actions")

cards = actions.revenue_cards(b)
if cards:
    theme.action_cards(cards)
else:
    st.info("No recommendations meet the current thresholds. The rules can be changed under Business assumptions.")
st.caption(actions.FOOTNOTE)

reports.panel("revenue", lambda: report_pages.revenue(b), "Download this page as a report")
