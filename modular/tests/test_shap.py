import numpy as np
import pandas as pd

from src import config, explain, scoring


def _res():
    df = scoring.score(pd.read_parquet(config.DEFAULT_DATA).head(3000))
    return explain.shap_values(scoring.load_model(), df, n=15, background=8)


def test_shap_adds_up_to_forecast():
    r = _res()
    total = r["values"].sum(axis=1) + r["base"]
    assert np.allclose(total, r["forecast"], atol=1e-6)
    assert list(r["values"].columns) == explain.features()


def test_shap_text_explains():
    r = _res()
    s = explain.shap_summary(r)
    assert s["size"].is_monotonic_decreasing and s["note"].str.len().gt(10).all()
    assert "GB" in explain.shap_sentence(s, r["base"])
    assert "average of" in explain.shap_row_text(r, r["values"].index[0])
