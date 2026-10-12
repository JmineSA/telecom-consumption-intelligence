"""The data-quality gate: every scenario says whether the dataset is safe to score, and why."""
import io

import numpy as np
import pandas as pd
import pytest

from src import quality
from src.config import DEFAULT_DATA, ENGINEERED, TARGET
from src.data_loader import ingest


@pytest.fixture(scope="module")
def base():
    return pd.read_parquet(DEFAULT_DATA).drop_duplicates(["user_id", "date"]).reset_index(drop=True)


def run(df, name="f.parquet", raw=None):
    buf = io.BytesIO(raw) if raw is not None else io.BytesIO()
    if raw is None:
        df.to_csv(buf, index=False) if name.endswith(".csv") else df.to_parquet(buf, index=False)
    buf.seek(0)
    return ingest(buf, name, len(buf.getvalue()))


def status(rep, name):
    return next(c.status for c in rep.checks if c.name == name)


def test_default_dataset_is_ready_and_duplicates_are_flagged():
    clean, rep, _ = ingest(DEFAULT_DATA, DEFAULT_DATA.name, DEFAULT_DATA.stat().st_size)
    assert rep.ready and clean is not None
    assert status(rep, "Duplicate records") == "warn"


def test_missing_required_columns_block_scoring_and_name_the_columns(base):
    clean, rep, _ = run(base.drop(columns=["region", "monthly_bill_zar"]))
    assert clean is None and not rep.ready
    c = next(c for c in rep.checks if c.name == "Required columns")
    assert c.status == "crit" and "region" in c.finding and "monthly_bill_zar" in c.finding
    assert "revenue" in c.impact and c.action


def test_optional_columns_may_be_missing(base):
    clean, rep, _ = run(base.drop(columns=["arpu", "churn_status", "background_gb"]))
    assert rep.ready and clean is not None


def test_unsupported_empty_and_damaged_files_are_critical(base):
    assert status(run(base, "d.xlsx", raw=b"PK junk")[1], "File type") == "crit"
    assert status(run(base, "e.csv", raw=b"")[1], "File is not empty") == "crit"
    assert status(run(base.head(0), "h.csv")[1], "File is not empty") == "crit"
    assert status(run(base, "x.parquet", raw=b"not parquet")[1], "File can be read") == "crit"


def test_wrong_unit_is_critical(base):
    d = base.copy()
    for c in ["streaming_gb", "social_gb", "messaging_gb", "gaming_gb", "background_gb", "total_gb", TARGET] + ENGINEERED:
        d[c] = d[c] * 1000
    clean, rep, _ = run(d)
    assert clean is None and status(rep, "Usage level") == "crit"


def test_a_few_impossible_values_warn_and_are_removed_but_many_block(base):
    few = base.copy()
    few.loc[few.sample(frac=0.01, random_state=1).index, "monthly_bill_zar"] = -10
    clean, rep, _ = run(few)
    assert rep.ready and status(rep, "Impossible values") == "warn" and rep.rows_scored < len(few)
    many = base.copy()
    many.loc[many.sample(frac=0.10, random_state=1).index, "monthly_bill_zar"] = -10
    assert not run(many)[1].ready


def test_heavy_duplication_blocks(base):
    assert status(run(pd.concat([base, base.sample(frac=0.4, random_state=2)]))[1], "Duplicate records") == "crit"


def test_unseen_categories_warn_then_block(base):
    rng = np.random.RandomState(0)
    for share, expected in ((0.05, "warn"), (0.40, "crit")):
        d = base.copy()
        d["plan_type"] = np.where(rng.rand(len(d)) < share, "Gold_Plan", d["plan_type"])
        assert status(run(d)[1], "Unseen categories") == expected


def test_unreadable_text_in_a_number_column_is_reported(base):
    d = base.copy()
    d["total_gb"] = d["total_gb"].astype(object)
    d.loc[d.sample(frac=0.02, random_state=3).index, "total_gb"] = "abc"
    clean, rep, _ = run(d, "t.csv")
    assert status(rep, "Numbers and dates are readable") == "warn"


def test_a_shifted_customer_base_warns_but_does_not_block(base):
    clean, rep, _ = run(base[base.plan_type == "Postpaid_Unlimited"])
    assert rep.ready and status(rep, "Customer mix") == "warn"


def test_raw_usage_without_lag_columns_is_scored(base):
    raw = base.drop(columns=ENGINEERED + [TARGET, "day_of_week", "is_weekend", "day_of_month", "is_month_start",
                                          "is_month_end", "day_index"])
    clean, rep, prep = run(raw)
    assert rep.ready and prep["built_features"] and "lag_1d_total_gb" in clean.columns


def test_every_warning_and_critical_explains_its_impact(base):
    d = base.copy()
    d.loc[d.sample(frac=0.01, random_state=1).index, "total_gb"] = -5
    d["Unnamed: 0"] = range(len(d))
    cases = [run(d)[1], run(base.drop(columns=["region"]))[1], run(base, "e.csv", raw=b"")[1],
             run(pd.concat([base, base.sample(frac=0.4, random_state=2)]))[1]]
    flagged = [c for rep in cases for c in rep.checks if c.status != "pass"]
    assert len(flagged) >= 6
    assert all(c.impact and c.action for c in flagged), [c.name for c in flagged if not (c.impact and c.action)]


def test_psi_is_zero_for_the_same_data_and_large_for_a_shift():
    ref = quality.reference()["numeric"]["total_gb"]
    rng = np.random.RandomState(0)
    same = rng.lognormal(1.6, 0.8, 20000)
    edges = np.quantile(same, np.linspace(0.1, 0.9, 9)).tolist()
    share = (np.bincount(np.searchsorted(edges, same, side="right"), minlength=10) / len(same)).tolist()
    assert quality.psi_numeric(same, edges, share) < 0.01
    assert quality.psi_numeric(same * 3, edges, share) > 0.25
    assert ref["edges"]


def test_blocked_upload_keeps_the_previous_data(monkeypatch, base):
    import streamlit as st
    from src import state
    ss = {"version": 3, "data": "previous", "source": "default sample"}
    monkeypatch.setattr(st, "session_state", ss)
    f = io.BytesIO()
    base.drop(columns=["region"]).to_parquet(f)
    f.name, f.size = "bad.parquet", len(f.getvalue())
    f.seek(0)
    assert state.load_upload(f) is False
    assert ss["data"] == "previous" and ss["quality_blocked"] and not ss["quality"].ready


def test_ready_upload_replaces_the_data(monkeypatch, base):
    import streamlit as st
    from src import state
    ss = {"version": 3, "data": "previous", "source": "default sample"}
    monkeypatch.setattr(st, "session_state", ss)
    f = io.BytesIO()
    base.to_parquet(f)
    f.name, f.size = "good.parquet", len(f.getvalue())
    f.seek(0)
    assert state.load_upload(f) is True
    assert ss["source"] == "good.parquet" and ss["version"] == 4 and not ss["quality_blocked"]
    assert "pred_next_day_gb" in ss["data"].columns and ss["quality"].ready
