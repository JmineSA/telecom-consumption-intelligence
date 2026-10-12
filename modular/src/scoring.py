import joblib
import numpy as np
import pandas as pd
import streamlit as st

from .config import MODEL_PATH, PRED, TARGET


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


def score(df: pd.DataFrame, model=None) -> pd.DataFrame:
    """Add next-day predictions, the date they are for, and the forecast error."""
    out = df  # scored in place: callers pass freshly prepared data, and a copy would double the memory
    out[PRED] = np.clip((model or load_model()).predict(out.drop(columns=[TARGET], errors="ignore")), 0, None)
    out["forecast_date"] = out["date"] + pd.Timedelta(days=1)
    out["residual"] = out[TARGET] - out[PRED]
    return out
