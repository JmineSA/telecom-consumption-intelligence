import pandas as pd
import streamlit as st

from src import config, state, theme, tour
from src.theme import label

st.set_page_config(page_title=config.APP_NAME, page_icon=":material/signal_cellular_alt:", layout="wide")
theme.inject()
_missing = config.missing_files()
if _missing:
    st.error("Some files the dashboard needs were not found.")
    st.markdown("\n".join(f"- {m}" for m in _missing))
    st.caption("Expected layout: training/, models/ and modular/ side by side in the project folder. "
               "Set TELECOM_PROJECT_ROOT if your project folder is somewhere else.")
    st.stop()
state.init()
ss = st.session_state
ss.setdefault("uploader_n", 0)

dq_page = st.Page("views/data_checks.py", title="Data Checks", icon=":material/fact_check:")
pages = {
    "Business": [
        st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", default=True),
        st.Page("views/forecast.py", title="Tomorrow's Forecast", icon=":material/trending_up:"),
        st.Page("views/revenue.py", title="Revenue Analysis", icon=":material/payments:"),
        st.Page("views/geography.py", title="Geography", icon=":material/map:"),
        st.Page("views/insights.py", title="Customer Insights", icon=":material/groups:"),
        st.Page("views/compare.py", title="Compare Data", icon=":material/compare_arrows:"),
    ],
    "Model and data": [
        st.Page("views/monitoring.py", title="Model Monitoring", icon=":material/monitoring:"),
        dq_page,
        st.Page("views/about.py", title="About", icon=":material/info:"),
    ],
}
pg = st.navigation(pages)
theme.begin_page(pg.url_path or pg.title)

with st.sidebar:
    if st.button("How to read this dashboard", icon=":material/help:", key="tour_open"):
        ss["tour_i"] = 0
        tour.show()
    st.markdown('<div class="side-h">Data and filters</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload new data", type=["csv", "parquet"], key=f"up_{ss['uploader_n']}",
                          help="CSV or Parquet. Include daily usage and customer columns. Lag features are built if missing.")
    blocked_now = False
    if up is not None and ss["last_upload"] != (up.name, up.size):
        ss["last_upload"] = (up.name, up.size)
        with st.spinner("Checking and scoring your data"):
            blocked_now = not state.load_upload(up)
    theme.gate_badge(ss["quality"], ss["quality_blocked"])
    if st.button("Reset to default data"):
        state.reset_to_default()
        ss["last_upload"] = None
        ss["uploader_n"] += 1
        st.rerun()

    df, v = ss["data"], ss["version"]
    dmin, dmax = df["date"].min().date(), df["date"].max().date()
    rng = st.date_input("Period", value=(dmin, dmax), min_value=dmin, max_value=dmax, key=f"dates_{v}")
    start, end = (rng if len(rng) == 2 else (dmin, dmax))
    regions = sorted(df["region"].unique())
    plans = [p for p in config.KNOWN["plan_type"] if p in set(df["plan_type"])] + \
            sorted(set(df["plan_type"]) - set(config.KNOWN["plan_type"]))
    nets = [n for n in config.KNOWN["network_type"] if n in set(df["network_type"])] + \
           sorted(set(df["network_type"]) - set(config.KNOWN["network_type"]))
    sel_r = st.multiselect("Region", regions, default=regions, key=f"region_{v}")
    sel_p = st.multiselect("Plan", plans, default=plans, key=f"plan_{v}", format_func=label)
    sel_n = st.multiselect("Network", nets, default=nets, key=f"net_{v}")
    st.slider("Churn-risk threshold", 0.1, 0.9, 0.5, 0.05, key="threshold",
              help="Customers at or above this churn probability count as at risk.")

    with st.expander("Business assumptions"):
        st.caption("Change these to match your business. They feed the forecast and revenue pages.")
        st.slider("Capacity safety buffer (%)", 0, 30, 8, key="buffer")
        st.slider("Top-up rule: days in a row", 2, 7, 3, key="topup_days")
        st.slider("Top-up rule: GB above forecast", 0.5, 10.0, 2.0, 0.5, key="topup_gb")
        st.slider("Retention rule: days in a row", 2, 10, 5, key="retain_days")
        st.slider("Retention rule: GB below forecast", 0.5, 10.0, 2.0, 0.5, key="retain_gb")
        st.number_input("Top-up price (R per GB)", 5, 200, 30, 5, key="price_gb")
        st.slider("Top-up take-up rate (%)", 5, 60, 20, 5, key="takeup")

    st.caption("Appearance follows your device. To change it, open the top-right menu (three dots) and choose System, Light, or Dark.")

if blocked_now:
    st.switch_page(dq_page)  # show why the file was not scored

ss["filters"] = {"start": pd.Timestamp(start), "end": pd.Timestamp(end),
                 "region": sel_r, "plan": sel_p, "network": sel_n}
pg.run()
