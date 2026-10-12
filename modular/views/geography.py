import streamlit as st

from src import charts, kpis, report_pages, reports, state, theme
from src.config import TEAL
from src.theme import label, pct

b = state.bundle()
df = b["df"]
st.title("Geography")
theme.data_label(b, checks=False)

if df.empty:
    st.info("No records match the filters. Widen the period or select more regions, plans, or networks.")
    st.stop()

METRICS = {
    "Customers": ("customers", "{:,.0f}", ""),
    "Data per customer per day": ("avg_gb_day", "{:.2f}", " GB"),
    "Next-day forecast": ("forecast_gb", "{:,.0f}", " GB"),
    "Monthly revenue": ("revenue", "R {:,.0f}", ""),
    "Customers at churn risk": ("at_risk_pct", "{:.1%}", ""),
    "Records on congested networks": ("congested_share", "{:.1%}", ""),
}
t = kpis.region_table(df, b["threshold"])
name = st.selectbox("Compare regions by", list(METRICS))
col, fmt, unit = METRICS[name]

left, right = st.columns([3, 2])
with left:
    st.subheader(name)
    theme.show(charts.hbar(t[col].sort_values(ascending=False), TEAL, fmt, unit))
with right:
    st.subheader("What stands out")
    s = t[col].sort_values(ascending=False)
    hi, lo = s.index[0], s.index[-1]
    spread = (s.iloc[0] / s.iloc[-1] - 1) if s.iloc[-1] else 0
    rows = [("Highest", f"{hi} leads on {name.lower()}."), ("Lowest", f"{lo} is lowest."),
            ("Spread", f"The gap between top and bottom region is {pct(spread)}. "
                       + ("Regions are close, so one plan for all of them is reasonable." if spread < 0.10
                          else "The gap is large enough to justify region-specific offers."))]
    html = "".join(f'<div class="alert"><span class="tag teal">{a}</span><span>{m}</span></div>' for a, m in rows)
    st.markdown(f'<div class="panel">{html}</div>', unsafe_allow_html=True)

st.subheader("All regions")
show = t.rename(columns={"customers": "Customers", "revenue": "Monthly revenue (R)", "forecast_gb": "Next-day forecast (GB)",
                         "at_risk_pct": "At churn risk", "avg_gb_day": "GB per customer per day",
                         "congested_share": "On congested networks"})
show["At churn risk"] = (show["At churn risk"] * 100).round(1)
show["On congested networks"] = (show["On congested networks"] * 100).round(1)
show = show.rename(columns={"At churn risk": "At churn risk (%)", "On congested networks": "On congested networks (%)"})
st.dataframe(show.round(2).reset_index().rename(columns={"region": "Region"}), hide_index=True)
st.caption("The data contains the regions listed here. Customers, revenue and forecasts use each customer's latest record.")

reports.panel("geography", lambda: report_pages.geography(b), "Download this page as a report")
