import pandas as pd
import pytest

from src import compare, config, scoring


@pytest.fixture(scope="module")
def df():
    return scoring.score(pd.read_parquet(config.DEFAULT_DATA).head(6000))


def test_summary_and_table(df):
    d = df["date"].median()
    a, b = df[df["date"] < d], df[df["date"] >= d]
    t = compare.table(compare.summary(a, .5), compare.summary(b, .5))
    assert len(t) == len(compare.MEASURES) and set(t["verdict"]) <= {"good", "bad", "neutral"}
    assert compare.display(t).shape[1] == 5 and compare.headline(t)
    same = compare.table(compare.summary(a, .5), compare.summary(a, .5))
    assert (same["Change"].fillna(0) == 0).all() and "within 1%" in compare.headline(same)[0]


def test_verdicts_follow_business_meaning():
    a = {k: 100.0 for k, *_ in compare.MEASURES}; b = dict(a, at_risk=150.0, revenue=150.0, avg_gb=150.0)
    v = compare.table(a, b).set_index("key")["verdict"]
    assert v["at_risk"] == "bad" and v["revenue"] == "good" and v["avg_gb"] == "neutral"


def test_empty_side_and_segments(df):
    t = compare.table(compare.summary(df, .5), compare.summary(df.iloc[0:0], .5))
    assert t["verdict"].eq("neutral").all() and compare.display(t)["B"].eq("n/a").all()
    s = compare.by_segment(df, df, "region")
    assert (s["Change %"].dropna().abs() < 1e-9).all()


def test_shap_in_monitoring_report(df, monkeypatch):
    import streamlit as st

    from src import explain, report_pages
    res = explain.shap_values(scoring.load_model(), df, n=15, background=8)
    monkeypatch.setattr(st, "session_state", {"version": 1, "model_name": "Original model", "shap_cache": {(1, "Original model"): res}})
    from src.reports import Report
    rep = Report("t", "m")
    report_pages._explanations(rep, st.session_state)
    assert [b[0] for b in rep.blocks] == ["bars", "text", "table"]
    st.session_state.clear()
    rep = Report("t", "m")
    report_pages._explanations(rep, st.session_state | {"version": 1, "model_name": "x"})
    assert "not calculated" in rep.blocks[0][2][0]
