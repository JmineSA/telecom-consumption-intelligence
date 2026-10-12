"""Shared data for every page. One place loads, scores and filters the data."""
import json

import pandas as pd
import streamlit as st

from .config import DEFAULT_DATA, PREP_META
from . import quality
from .data_loader import ingest
from .scoring import score


@st.cache_data(show_spinner=False)
def _default():
    df, qrep, prep = ingest(DEFAULT_DATA, DEFAULT_DATA.name, DEFAULT_DATA.stat().st_size)
    if df is None:
        raise RuntimeError("The default dataset did not pass its own data checks: "
                           + "; ".join(c.finding for c in qrep.checks if c.status == quality.CRIT))
    # Rows from the original test period are new to the model; earlier rows were used in training.
    test_start = pd.Timestamp(json.loads(PREP_META.read_text())["split"]["test_dates"][0])
    return score(df), prep, test_start, qrep


def _set_default(version):
    df, report, test_start, qrep = _default()
    st.session_state.update(data=df, report=report, source="default sample", version=version, model=None,
                            model_name="Original model", eval_from=test_start, eval_from_base=test_start,
                            retrain_result=None, quality=qrep, quality_blocked=False)


def init():
    if "data" not in st.session_state:
        st.session_state["last_upload"] = None
        _set_default(0)


def reset_to_default():
    _set_default(st.session_state["version"] + 1)


def load_upload(file) -> bool:
    """Check an upload and, if it is safe to score, replace the data with it.

    Returns True when the data was replaced. When the dataset is NOT READY FOR SCORING the previous data stays
    loaded and the report for the rejected file is kept for the Data Checks page.
    """
    ss = st.session_state
    df, qrep, prep = ingest(file, file.name, getattr(file, "size", None))
    if df is not None:
        try:
            df = score(df)
        except Exception as exc:  # scoring itself is part of "safe to score"
            qrep.add("Scoring readiness", "Model can score the data", quality.CRIT,
                     f"Scoring failed with {type(exc).__name__}.",
                     "The model could not run on this data, so no forecasts can be shown.",
                     "Check the column types against the Upload format section of the README.")
            df = None
    if df is None:
        ss.update(quality=qrep, quality_blocked=True)
        return False
    qrep.add("Scoring readiness", "Model can score the data", quality.PASS, "Forecasts were produced for every usable row.")
    ss.update(data=df, report=prep, source=file.name, model=None, model_name="Original model", eval_from=None,
              eval_from_base=None, retrain_result=None, quality=qrep, quality_blocked=False,
              version=ss["version"] + 1)
    return True


def use_model(model, name, eval_from):
    """Switch the scoring model and re-score the loaded data with it."""
    ss = st.session_state
    ss.update(data=score(ss["data"], model), model=model, model_name=name, eval_from=eval_from)


def apply_filters(df, f, dates=True):
    m = df["region"].isin(f["region"]) & df["plan_type"].isin(f["plan"]) & df["network_type"].isin(f["network"])
    if dates:
        m &= (df["date"] >= f["start"]) & (df["date"] <= f["end"])
    return df[m]


def bundle() -> dict:
    """Filtered data for the selected period, plus the equal-length period before it."""
    ss = st.session_state
    f = ss["filters"]
    span = (f["end"] - f["start"]).days + 1
    prev_f = {**f, "start": f["start"] - pd.Timedelta(days=span), "end": f["start"] - pd.Timedelta(days=1)}
    return {"all": ss["data"], "df": apply_filters(ss["data"], f), "prev": apply_filters(ss["data"], prev_f),
            "filters": f, "report": ss["report"], "source": ss["source"], "threshold": ss["threshold"]}
