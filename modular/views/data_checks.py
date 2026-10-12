import pandas as pd
import streamlit as st

from src import quality, report_pages, reports, theme, viewer_ui
from src.theme import int_

ss = st.session_state
q = ss["quality"]

st.title("Data Checks")
st.caption("Is this dataset valid and safe to use for scoring?")

if ss.get("quality_blocked"):
    st.warning(f"{q.source} was not loaded. The dashboard is still showing {ss['source']}.")
else:
    st.caption(f"Checked: {q.source}. This is the dataset the dashboard is showing.")

c = st.columns(4)
theme.kpi(c[0], "Passed", int_(q.count("pass")), "Checks that are acceptable", "good", accent="ok")
theme.kpi(c[1], "Warnings", int_(q.count("warn")), "Scoring can continue, attention recommended", "flat",
          accent="watch" if q.count("warn") else "neutral")
theme.kpi(c[2], "Critical", int_(q.count("crit")), "Scoring is blocked" if q.count("crit") else "Nothing blocks scoring",
          "bad" if q.count("crit") else "good", accent="risk" if q.count("crit") else "ok")
theme.kpi(c[3], "Usable rows", f"{q.rows_scored:,}" if q.rows_scored else "n/a",
          f"of {q.rows_in:,} in the file" if q.rows_in else "Not reached", "flat")
st.write("")

for group in q.groups:
    theme.check_group(group, [x for x in q.checks if x.group == group])
if q.stopped_early:
    st.caption("Not run: " + q.stopped_early.replace("The remaining checks were not run because", "later checks need").rstrip("."))

if q.actions_taken:
    st.subheader("What was cleaned")
    st.markdown("\n".join(f"- {a}" for a in q.actions_taken))

st.write("")
viewer_ui.render()
st.write("")

with st.expander("How the checks decide"):
    st.write("A dataset is ready for scoring when no check is critical. A warning does not stop scoring.")
    st.dataframe(pd.DataFrame(quality.THRESHOLDS, columns=["Check", "Warning when", "Critical when"]), hide_index=True)
    ref = quality.reference()
    if ref:
        st.caption(f"Distribution checks compare the data with {ref['source']} ({ref['rows']:,} rows, built {ref['built']}). "
                   "For a true training reference run: python scripts/make_reference_profile.py --input data/processed/train.parquet")

theme.gate_banner(q, ss["source"])
st.write("")
reports.panel("dataquality", lambda: report_pages.data_checks({"report": ss["report"], "source": q.source}),
              "Download this page as a report")
