import streamlit as st

from src import charts, insights, kpis, report_pages, reports, state, theme
from src.config import AMBER, TEAL, TARGET
from src.theme import gb, label, pct, rand

ss = st.session_state
b = state.bundle()
df = b["df"]
st.title("Customer Insights")
theme.data_label(b, checks=False)

if df.empty:
    st.info("No records match the filters. Widen the period or select more regions, plans, or networks.")
    st.stop()

SEG = {"Plan": "plan_type", "Device": "device_type", "Age group": "age_group", "Network": "network_type"}
seg = st.radio("Group customers by", list(SEG), horizontal=True)
col = SEG[seg]
cust = kpis.latest_per_customer(df)
usage = df.groupby(col)["total_gb"].mean().sort_values(ascending=False)
bill = cust.groupby(col)["monthly_bill_zar"].mean().reindex(usage.index)

l, r = st.columns(2)
with l:
    st.subheader("Data per customer per day")
    theme.show(charts.hbar(usage, TEAL, "{:.1f}", " GB"))
with r:
    st.subheader("Average monthly bill")
    theme.show(charts.hbar(bill, TEAL, "R {:,.0f}"))
if len(usage) > 1 and usage.iloc[-1] > 0:
    st.caption(f"{label(usage.index[0])} customers use {usage.iloc[0] / usage.iloc[-1]:.1f} times as much data per day as "
               f"{label(usage.index[-1])} customers.")

st.subheader("Customers to contact")
has_actuals = b["report"]["has_actuals"]
tab_more, tab_less, tab_one = st.tabs(["Using more than expected", "Using less than expected", "Customer lookup"])


def list_table(hits, kind):
    if hits is None:
        st.info("This file has no next-day actuals, so usage cannot be compared with the forecast.")
        return
    if hits.empty:
        st.info("No customers meet this rule in the loaded data. Change the rule under Business assumptions, "
                "or load data with more days per customer.")
        return
    t = insights.topup_table(hits) if kind == "more" else insights.retention_table(hits, b["threshold"])
    st.write(f"{len(t):,} customers.")
    st.dataframe(t.round(2), hide_index=True)
    st.download_button("Download this list (CSV)", t.round(2).to_csv(index=False).encode(),
                       f"customers_{kind}.csv", "text/csv", key=f"dl_{kind}")


with tab_more:
    st.caption(f"Actual use is {ss['topup_gb']:g} GB or more above forecast for {ss['topup_days']} days in a row.")
    list_table(kpis.persistent_gap(df, ss["topup_gb"], ss["topup_days"], 1) if has_actuals else None, "more")
with tab_less:
    st.caption(f"Actual use is {ss['retain_gb']:g} GB or more below forecast for {ss['retain_days']} days in a row. "
               "Falling use can be an early sign that a customer is disengaging.")
    list_table(kpis.persistent_gap(df, ss["retain_gb"], ss["retain_days"], -1) if has_actuals else None, "less")
with tab_one:
    ids = sorted(df["user_id"].unique())
    uid = st.selectbox("Customer", ids, index=None, placeholder="Choose or type a customer ID")
    if uid is not None:
        d = df[df["user_id"] == uid]
        last = d.loc[d["date"].idxmax()]
        c = st.columns(4)
        theme.kpi(c[0], "Plan", label(last["plan_type"]), last["region"], "flat")
        theme.kpi(c[1], "Monthly bill", rand(last["monthly_bill_zar"]), f"{label(last['device_type'])}", "flat")
        theme.kpi(c[2], "Churn probability", pct(last["churn_probability"]), "Latest record",
                  "bad" if last["churn_probability"] >= b["threshold"] else "flat",
                  accent="risk" if last["churn_probability"] >= b["threshold"] else "neutral")
        theme.kpi(c[3], "Next-day forecast", gb(last["pred_next_day_gb"]), f"For {last['forecast_date']:%d %b %Y}", "flat")
        st.write("")
        if d[TARGET].notna().any():
            theme.show(charts.customer_line(d))
        else:
            st.info("This customer has no next-day actuals to chart.")

reports.panel("customers", lambda: report_pages.customers(b), "Download this page as a report")
