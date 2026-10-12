import pandas as pd
import pytest

from src import config, viewer


@pytest.fixture(scope="module")
def df():
    return pd.read_parquet(config.DEFAULT_DATA).head(2000)


def test_samples(df):
    assert len(viewer.draw_sample(df, "Random", 50, 1)) == 50
    assert not viewer.draw_sample(df, "Random", 50, 1).equals(viewer.draw_sample(df, "Random", 50, 2))
    e, l = viewer.draw_sample(df, "Earliest dates", 20), viewer.draw_sample(df, "Latest dates", 20)
    assert e["date"].max() <= l["date"].min() and len(viewer.draw_sample(df, "Random", 10**9)) == len(df)


def test_calculated_column(df):
    out = viewer.add_column(df, "ratio", "total_gb", "÷", "monthly_bill_zar")
    assert "ratio" in out and "ratio" not in df
    z = viewer.add_column(df.assign(zero=0.0), "r", "total_gb", "÷", 0)
    assert z["r"].isna().all()
    for bad in [("", "total_gb", "+", 1), ("total_gb", "total_gb", "+", 1), ("x", "plan_type", "+", 1), ("x", "total_gb", "+", "region")]:
        with pytest.raises(ValueError):
            viewer.add_column(df, *bad)


def test_keep_rows_and_summary(df):
    assert set(viewer.keep_rows(df, "region", "equals", df["region"].iloc[0])["region"]) == {df["region"].iloc[0]}
    assert (viewer.keep_rows(df, "total_gb", "is at least", 5)["total_gb"] >= 5).all()
    assert len(viewer.keep_rows(df, "date", "is less than", df["date"].min())) == 0
    s = viewer.summarise(df, "region", "total_gb", "Average")
    assert len(s) == df["region"].nunique() and s.iloc[:, 1].is_monotonic_decreasing
    assert viewer.summarise(df, None, "total_gb", "Sum").iloc[0, 0] == pytest.approx(df["total_gb"].sum())


def test_export_and_upload_round_trip(df):
    scored = df.assign(pred_next_day_gb=1.0, forecast_date=df["date"], residual=0.0, mine=1.0)
    up = viewer.for_upload(scored, ["mine"])
    assert list(up.columns) == list(df.columns)
    assert len(viewer.to_csv(df)) > 100 and viewer.to_excel(df.head(50))[:2] == b"PK"
    assert len(pd.read_parquet(viewer.to_parquet_buffer(up))) == len(df)
