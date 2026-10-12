"""Retrain the model on the loaded data, with the same settings and date split as the original."""
import pandas as pd

from .config import TARGET
from .data_loader import DataError
from .kpis import metrics
from .scoring import load_model, score


def split_dates(dates):
    """70% / 15% / 15% by date, as in the original training. Returns (train_end, val_end)."""
    d = sorted(dates)
    n = len(d)
    return d[max(int(n * 0.70) - 1, 0)], d[max(int(n * 0.85) - 1, 0)]


def run(df):
    from training.pipelines.training_pipeline import build_model_pipeline  # needs the project root on sys.path

    d = df.dropna(subset=[TARGET])
    dates = d["date"].unique()
    if len(dates) < 10:
        raise DataError("Retraining needs at least 10 days of data with next-day actuals.")
    tr_end, va_end = split_dates(dates)
    train, val, test = d[d["date"] <= tr_end], d[(d["date"] > tr_end) & (d["date"] <= va_end)], d[d["date"] > va_end]
    if min(len(train), len(val), len(test)) == 0:
        raise DataError("The data does not have enough distinct days to split into train, validation and test.")

    stale = ["pred_next_day_gb", "forecast_date", "residual"]  # outputs of the previous scoring
    model = build_model_pipeline()
    model.fit(train.drop(columns=[TARGET] + stale, errors="ignore"), train[TARGET])

    rows = {}
    for name, m in (("Original model", load_model()), ("Retrained model", model)):
        rows[name] = metrics(score(test.drop(columns=stale, errors="ignore"), m))
    return model, rows, test["date"].min(), {"train": len(train), "val": len(val), "test": len(test)}
