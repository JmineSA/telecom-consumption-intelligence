import json

import pandas as pd
import streamlit as st

from src import charts, explain, kpis, report_pages, reports, retrain, state, theme
from src.config import AMBER, MODEL_INFO, TEAL
from src.data_loader import DataError
from src.scoring import load_model
from src.theme import label

ss = st.session_state
b = state.bundle()
st.title("Model Monitoring")
theme.data_label(b, checks=False)

df = b["df"]
if not b["report"]["has_actuals"]:
    st.info("This file has no next-day actuals, so forecast accuracy cannot be measured.")
    st.stop()
ev = df if ss["eval_from"] is None else df[df["date"] >= ss["eval_from"]]
ev = ev.dropna(subset=["target_next_day_gb"])
if ev.empty:
    st.info("No records with actuals match the filters. Widen the period or selections.")
    st.stop()

ref = json.loads(MODEL_INFO.read_text())["val_metrics"]
m = kpis.metrics(ev)
ratio = m["mae"] / ref["mae"]
health, tone = (("Healthy", "good") if ratio <= 1.10 else ("Watch", "flat") if ratio <= 1.25 else ("Action needed", "bad"))

if ss["eval_from"] is None:
    st.caption(f"Accuracy is measured on {m['n']:,} rows with actuals. These rows are new to the model.")
else:
    st.caption(f"Accuracy is measured on {m['n']:,} rows from {ss['eval_from']:%d %b %Y} onward, "
               "which the model did not see in training." if ss["model_name"] == "Original model"
               else f"Accuracy is measured on {m['n']:,} rows from {ss['eval_from']:%d %b %Y} onward, held out from retraining.")

c = st.columns(5)
theme.kpi(c[0], "Model health", health, f"Error is {ratio:.2f} times the error at training", tone,
          accent="risk" if tone == "bad" else "watch" if tone == "flat" else "ok")
theme.kpi(c[1], "Average error (MAE)", f"{m['mae']:.2f} GB", f"At training: {ref['mae']:.2f} GB", "flat")
theme.kpi(c[2], "Typical large error (RMSE)", f"{m['rmse']:.2f} GB", f"At training: {ref['rmse']:.2f} GB", "flat")
theme.kpi(c[3], "Variance explained (R²)", f"{m['r2']:.2f}", f"At training: {ref['r2']:.2f}", "flat")
theme.kpi(c[4], "Average bias", f"{m['bias']:+.2f} GB", "Positive: actual use is above forecast", "flat")
st.caption("Health compares today's average error with the error measured at training: healthy up to 10% higher, "
           "watch up to 25% higher, action needed above that. Using the model name: " + ss["model_name"] + ".")

st.write("")
l, r = st.columns(2)
with l:
    st.subheader("Average error over time")
    theme.show(charts.error_trend(ev, ref["mae"]))
with r:
    st.subheader("Actual vs forecast")
    theme.show(charts.actual_vs_forecast(ev))

l, r = st.columns(2)
with l:
    st.subheader("Error spread")
    theme.show(charts.residual_hist(ev))
with r:
    st.subheader("Where the model struggles")
    by = st.radio("Break down error by", ["Plan", "Region", "Network", "Congestion"], horizontal=True)
    colname = {"Plan": "plan_type", "Region": "region", "Network": "network_type", "Congestion": "congested"}[by]
    e = kpis.error_by(ev, colname)
    if by == "Congestion":
        e.index = ["Congested" if i == 1 else "Not congested" for i in e.index]
    theme.show(charts.hbar(e, AMBER, "{:.2f}", " GB"))

st.subheader("What drives the forecast")
view = st.radio("Explain the model with", ["Feature importance", "SHAP values", "Both"], horizontal=True, key="explain_view",
                help="Importance shows which features the model relies on. SHAP shows how each one pushes forecasts up or down.")
key = (ss["version"], ss["model_name"])


def _importance():
    cache = ss.setdefault("imp_cache", {})
    if key not in cache and st.button("Calculate feature importance"):
        with st.spinner("Shuffling each feature to see how much the error grows"):
            cache[key] = explain.importance(ss["model"] or load_model(), ev)
    if key in cache:
        imp = cache[key].head(10)
        imp.index = [label(i) for i in imp.index]
        theme.show(charts.hbar(imp.clip(lower=0), TEAL, "{:.2f}", " GB"))
        st.caption(f"The bars show how much the average error grows when a feature is shuffled. "
                   f"{imp.index[0]} matters most. Importance says what the model relies on, not which way it pushes.")
    else:
        st.caption("This takes a few seconds on a sample of 3,000 rows.")


def _shap():
    cache = ss.setdefault("shap_cache", {})
    if key not in cache and st.button("Calculate SHAP values"):
        with st.spinner("Working out how each feature moves each forecast (about 15 seconds)"):
            cache[key] = explain.shap_values(ss["model"] or load_model(), ev)
    if key not in cache:
        st.caption("SHAP explains the forecast in GB. It runs on a sample of 300 rows, so it is not shown until you ask for it.")
        return
    res = cache[key]
    summ = explain.shap_summary(res)
    st.markdown("**Which features move the forecast most**")
    top = summ.head(10).set_index("feature")["size"]
    top.index = [label(i) for i in top.index]
    theme.show(charts.hbar(top, TEAL, "{:.2f}", " GB"))
    st.info(explain.shap_sentence(summ, res["base"]))
    t = summ.head(10).assign(feature=lambda x: x["feature"].map(label), size=lambda x: x["size"].round(2))
    st.dataframe(t.rename(columns={"feature": "Feature", "size": "Average effect (GB)", "note": "How it pushes the forecast"})
                 [["Feature", "Average effect (GB)", "How it pushes the forecast"]], hide_index=True)
    st.markdown("**Why one forecast came out as it did**")
    ids = res["values"].index
    pick = st.selectbox("Pick a record from the sample", ids, key="shap_pick",
                        format_func=lambda i: f"Customer {ev.loc[i, 'user_id']}, {pd.Timestamp(ev.loc[i, 'forecast_date']):%d %b %Y}"
                        if i in ev.index else str(i))
    contrib = res["values"].loc[pick].sort_values(key=abs, ascending=False).head(8)
    contrib.index = [label(i) for i in contrib.index]
    theme.show(charts.contrib(contrib))
    st.write(explain.shap_row_text(res, pick))
    st.caption("SHAP values are in GB and add up to the gap between this forecast and the sample average. "
               "They describe how the model behaves, not what causes a customer's usage. Teal bars raise the forecast, amber bars lower it.")


if view in ("Feature importance", "Both"):
    if view == "Both":
        st.markdown("**Feature importance**")
    _importance()
if view in ("SHAP values", "Both"):
    if view == "Both":
        st.markdown("**SHAP values**")
    _shap()

st.subheader("Retrain on the loaded data")
st.write("Trains a new model with the same settings on the first 70% of dates, then checks it on the last 15%. "
         "Both models are compared on those same last dates.")
if st.button("Retrain model"):
    with st.spinner("Training the model"):
        try:
            model, res, test_start, sizes = retrain.run(ss["data"])
            state.use_model(model, "Retrained model", test_start)
            ss["retrain_result"] = (res, sizes)
            st.rerun()
        except DataError as exc:
            st.error(str(exc))
if ss["retrain_result"]:
    res, sizes = ss["retrain_result"]
    t = {k: {"Average error (GB)": v["mae"], "Typical large error (GB)": v["rmse"], "R²": v["r2"], "Rows tested": v["n"]}
         for k, v in res.items()}
    import pandas as pd
    st.dataframe(pd.DataFrame(t).T.round(3).reset_index().rename(columns={"index": "Model"}), hide_index=True)
    import io, joblib
    buf = io.BytesIO()
    joblib.dump(ss["model"], buf)
    c1, c2 = st.columns(2)
    c1.download_button("Download retrained model (.pkl)", buf.getvalue(), "retrained_pipeline.pkl")
    if c2.button("Switch back to the original model"):
        state.use_model(None, "Original model", ss["eval_from_base"])
        ss["retrain_result"] = None
        st.rerun()

reports.panel("monitoring", lambda: report_pages.monitoring(b), "Download this page as a report")
