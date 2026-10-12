"""The test-dataset pack must behave as its README says (small version, so the test stays quick)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import make_test_datasets as mt  # noqa: E402

BLOCKED = {"07_critical_missing_columns.csv", "08_critical_mostly_bad_values.csv", "09_unit_mismatch_megabytes.csv",
           "11_critical_empty_headers_only.csv"}


@pytest.fixture(scope="module")
def pack(tmp_path_factory):
    out = tmp_path_factory.mktemp("td")
    sc = mt.scenarios(small=True)
    for name, df, *_ in sc:
        df.to_csv(out / name, index=False) if name.endswith(".csv") else df.to_parquet(out / name, index=False)
    return out, sc


def test_every_file_is_distinct_and_documented(pack):
    out, sc = pack
    names = [n for n, *_ in sc]
    assert len(names) == len(set(names)) >= 25 and all(w for *_, w in sc)


def test_ready_and_blocked_files_match_readme(pack):
    out, sc = pack
    for name, *_ in sc:
        text = mt.outcome(out / name)
        assert text.startswith("NOT READY" if name in BLOCKED else "READY"), (name, text)


def test_baseline_is_clean_and_healthy(pack):
    out, _ = pack
    text = mt.outcome(out / "01_baseline_clean.parquet")
    assert "warning" not in text and "Healthy" in text


def test_drift_files_hurt_the_model(pack):
    out, _ = pack
    assert "Action needed" in mt.outcome(out / "24_model_noisy_behaviour.parquet")
    assert "No next-day actuals" in mt.outcome(out / "15_no_actuals_forecast_only.parquet")
