import streamlit as st

from src import charts, insights, kpis, report_pages, reports, state, theme
from src.config import AMBER, TEAL
from src.theme import gb, int_, label, pct

ss = st.session_state
b = state.bundle()
df = b["df"]
st.title("Tomorrow's Forecast")
theme.data_label(b, checks=False)

if df.empty:
    st.info("No records match the filters. Widen the period or select more regions, plans, or networks.")
    st.stop()

k = kpis.overview(df, b["prev"], b["threshold"])
cap = k["fc_total"] * (1 + ss["buffer"] / 100)
gap = kpis.persistent_gap(df, ss["topup_gb"], ss["topup_days"], direction=1) if b["report"]["has_actuals"] else None
ce = kpis.congestion_error(df)

cols = st.columns(4)
theme.kpi(cols[0], "Forecast for the next day", f"{k['fc_total']:,.0f} GB", f"{gb(k['fc_avg'])} per customer", "flat")
theme.kpi(cols[1], "Capacity to provision", f"{cap:,.0f} GB", f"Includes a {ss['buffer']}% safety buffer", "flat")
theme.kpi(cols[2], "Customers using more than expected", "n/a" if gap is None else int_(len(gap)),
          f"{ss['topup_gb']:g} GB or more above forecast, {ss['topup_days']} days in a row", "flat")
theme.kpi(cols[3], "Records on congested networks", "n/a" if ce is None else pct(ce["share"]),
          "Forecast error is higher when the network is congested" if ce and ce["congested"] > ce["normal"]
          else "Forecast error is similar on congested days", "bad" if ce and ce["congested"] > ce["normal"] else "flat",
          accent="watch" if ce and ce["congested"] > ce["normal"] else "neutral")

st.write("")
c1, c2, c3 = st.columns(3)
for col, field, title, color in [(c1, "region", "Forecast by region", TEAL),
                                 (c2, "plan_type", "Forecast by plan", TEAL),
                                 (c3, "network_type", "Forecast by network", TEAL)]:
    with col:
        st.subheader(title)
        theme.show(charts.hbar(kpis.forecast_by(df, field), color, "{:,.0f}", " GB"))

st.subheader("Customers using more than expected")
if gap is None:
    st.info("This file has no next-day actuals, so usage cannot be compared with the forecast.")
elif gap.empty:
    st.info(f"No customer has been {ss['topup_gb']:g} GB or more above forecast for {ss['topup_days']} days in a row. "
            "Lower the rule in Business assumptions, or load data with more days per customer.")
else:
    t = insights.topup_table(gap)
    st.dataframe(t, hide_index=True)
    st.download_button("Download this list (CSV)", t.round(2).to_csv(index=False).encode(),
                       "top_up_candidates.csv", "text/csv")
st.caption("Forecasts use each customer's latest record. Capacity is the forecast plus the safety buffer. "
           "Rules and buffer are set under Business assumptions in the sidebar.")

reports.panel("forecast", lambda: report_pages.forecast(b), "Download this page as a report")
