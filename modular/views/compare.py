from datetime import datetime

import pandas as pd
import streamlit as st

from src import charts, compare, data_loader, quality, reports, scoring, state, theme
from src.reports import Report
from src.theme import label

ss = st.session_state
data = ss["data"]
f = ss["filters"]
seg = state.apply_filters(data, f, dates=False)      # region, plan and network filters apply; dates are chosen here

st.title("Compare Data")
st.caption("How does one period, or one file, differ from another? Region, plan and network filters in the sidebar still apply.")

mode = st.radio("Compare", ["Two periods in the loaded data", "Loaded data against another file"], horizontal=True, key="cmp_mode")
a = b = None
name_a, name_b = "Period A", "Period B"
if seg.empty:
    st.info("No records match the filters. Select more regions, plans, or networks.")
    st.stop()

if mode.startswith("Two periods"):
    dmin, dmax = seg["date"].min().normalize(), seg["date"].max().normalize()
    span_all = (dmax - dmin).days + 1
    presets = {"Last 30 days against the 30 days before": 30, "Last 7 days against the 7 days before": 7,
               "Second half against the first half": max(1, span_all // 2), "Choose the dates myself": 0}
    pick = st.selectbox("Periods", list(presets), key="cmp_preset")
    n = presets[pick]
    if n:
        b_rng = (dmax - pd.Timedelta(days=n - 1), dmax)
        a_rng = (b_rng[0] - pd.Timedelta(days=n), b_rng[0] - pd.Timedelta(days=1))
        if a_rng[0] < dmin:
            st.warning(f"The data covers {span_all} days, which is not enough for two periods of {n} days. Showing what exists.")
            a_rng = (dmin, max(dmin, a_rng[1]))
        st.caption(f"{name_a}: {a_rng[0]:%d %b %Y} to {a_rng[1]:%d %b %Y}. {name_b}: {b_rng[0]:%d %b %Y} to {b_rng[1]:%d %b %Y}.")
    else:
        c1, c2 = st.columns(2)
        ra = c1.date_input("Period A", value=(dmin.date(), (dmin + pd.Timedelta(days=span_all // 2 - 1)).date()),
                           min_value=dmin.date(), max_value=dmax.date(), key="cmp_a")
        rb = c2.date_input("Period B", value=((dmin + pd.Timedelta(days=span_all // 2)).date(), dmax.date()),
                           min_value=dmin.date(), max_value=dmax.date(), key="cmp_b")
        if len(ra) != 2 or len(rb) != 2:
            st.info("Pick a start and an end date for both periods.")
            st.stop()
        a_rng, b_rng = tuple(map(pd.Timestamp, ra)), tuple(map(pd.Timestamp, rb))
    a = seg[(seg["date"] >= a_rng[0]) & (seg["date"] < a_rng[1] + pd.Timedelta(days=1))]
    b = seg[(seg["date"] >= b_rng[0]) & (seg["date"] < b_rng[1] + pd.Timedelta(days=1))]
    la, lb = (a_rng[1] - a_rng[0]).days + 1, (b_rng[1] - b_rng[0]).days + 1
    if la != lb:
        st.warning(f"Period A is {la} days and Period B is {lb} days. Averages are comparable, record counts are not.")
    meta = (f"Loaded data: {ss['source']}. {name_a}: {a_rng[0]:%d %b %Y} to {a_rng[1]:%d %b %Y}. "
            f"{name_b}: {b_rng[0]:%d %b %Y} to {b_rng[1]:%d %b %Y}.")
else:
    name_a, name_b = "Loaded data", "Other file"
    st.caption(f"{name_a} is {ss['source']}. Choose the file to compare it with. It goes through the same Data Checks, "
               "and the loaded data is not replaced.")
    up = st.file_uploader("File to compare with", type=["csv", "parquet"], key="cmp_file")
    store = ss.setdefault("cmp_store", {})
    if up is None:
        st.info("Upload a CSV or Parquet file to compare.")
        st.stop()
    sig = (up.name, up.size)
    if store.get("sig") != sig:
        with st.spinner("Checking and scoring the other file"):
            df2, q2, _ = data_loader.ingest(up, up.name, up.size)
            if df2 is not None:
                try:
                    df2 = scoring.score(df2, ss["model"])
                except Exception:
                    df2 = None
                    q2.add("Scoring readiness", "Model can score the data", quality.CRIT, "Scoring failed.", "No forecasts can be shown.", "")
        store.clear()
        store.update(sig=sig, df=df2, q=q2)
    df2, q2 = store["df"], store["q"]
    if df2 is None:
        st.error(f"{up.name} is not ready for scoring, so it cannot be compared.")
        for c in q2.checks:
            if c.status == quality.CRIT:
                st.markdown(f"- **{c.name}.** {c.finding} {c.impact}")
        st.stop()
    a, b = seg, state.apply_filters(df2, f, dates=False)
    if b.empty:
        st.info("The other file has no records for the selected regions, plans and networks.")
        st.stop()
    meta = f"{name_a}: {ss['source']}. {name_b}: {up.name}."

if a.empty or b.empty:
    st.info("One of the two periods has no records. Choose different dates.")
    st.stop()

t = compare.table(compare.summary(a, ss["threshold"]), compare.summary(b, ss["threshold"]))
byk = t.set_index("key")

# headline cards: B with its change from A
cols = st.columns(4)
for col, key in zip(cols, ["customers", "avg_gb", "revenue", "at_risk"]):
    r = byk.loc[key]
    chg = "n/a" if pd.isna(r["Change %"]) else f"{r['Change %']:+.1%} against {name_a}"
    accent = {"good": "ok", "neutral": "neutral", "bad": "risk" if key == "at_risk" else "watch"}[r["verdict"]]
    theme.kpi(col, f"{r['Measure']} ({name_b})", compare.fmt(r["kind"], r["B"]), chg, "bad" if r["verdict"] == "bad" else "flat", accent=accent)
st.write("")
st.subheader("What changed")
for line in compare.headline(t, name_a, name_b):
    st.markdown(f"- {line}")
both = compare.common_customers(a, b)
st.caption(f"{both:,} customers appear in both. Green or red wording follows what the change means for the business: more revenue is good, "
           "more customers at churn risk is not. Usage and forecast changes are shown without a verdict.")

st.subheader("All measures")
d = compare.display(t).rename(columns={"A": name_a, "B": name_b})
st.dataframe(d, hide_index=True)

st.subheader("By group")
g1, g2 = st.columns(2)
col = g1.selectbox("Group by", ["region", "plan_type", "network_type"], format_func=label, key="cmp_by")
meas = g2.selectbox("Measure", ["Data per customer per day (GB)", "Customers", "Monthly revenue (R)"], key="cmp_meas")
key = {"Data per customer per day (GB)": "avg_gb", "Customers": "customers", "Monthly revenue (R)": "revenue"}[meas]
seg_t = compare.by_segment(a, b, col, key)
theme.show(charts.compare_bars(seg_t, name_a, name_b))
show = seg_t.rename(columns={"A": name_a, "B": name_b}).reset_index()
show["Change %"] = show["Change %"].map(lambda v: "n/a" if pd.isna(v) else f"{v:+.1%}")
st.dataframe(show.round(2), hide_index=True)


def _report():
    rep = Report("Compare Data", f"{meta} Generated {datetime.now():%d %b %Y %H:%M}.")
    rep.kpis([(r["Measure"], compare.fmt(r["kind"], r["B"]), "" if pd.isna(r["Change %"]) else f"{r['Change %']:+.1%} vs {name_a}")
              for r in (byk.loc[k] for k in ["customers", "avg_gb", "revenue", "at_risk"])])
    rep.text("What changed", compare.headline(t, name_a, name_b))
    rep.table("All measures", d)
    rep.table(f"{meas} by {label(col)}", show.round(2))
    return rep


st.write("")
reports.panel("compare", _report, "Download this comparison as a report", extra=meta + str((col, key)))
