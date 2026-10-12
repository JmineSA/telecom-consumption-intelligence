"""Data viewer helpers: sample, filter, calculate, summarise, export. Pure functions on DataFrames (no free-text code is run)."""
import io

import numpy as np
import pandas as pd

from .config import PRED

DERIVED = [PRED, "forecast_date", "residual"]     # added by scoring, never part of an upload
SAMPLE_MODES = ("Random", "Earliest dates", "Latest dates")
OPS = {"+": np.add, "-": np.subtract, "×": np.multiply, "÷": np.divide}
FILTERS = ("equals", "does not equal", "is greater than", "is less than", "is at least", "is at most", "contains")
AGGS = {"Sum": "sum", "Average": "mean", "Median": "median", "Smallest": "min", "Largest": "max", "Count": "count"}
EDITABLE_ROWS = 50_000          # above this the table is read-only, which keeps phones and the cloud responsive


def draw_sample(df, mode="Random", n=50, seed=0) -> pd.DataFrame:
    n = max(1, min(int(n), len(df)))
    if mode == "Earliest dates":
        return df.sort_values("date", kind="stable").head(n).copy()
    if mode == "Latest dates":
        return df.sort_values("date", kind="stable").tail(n).iloc[::-1].copy()
    return df.sample(n, random_state=seed).copy()


def numeric_columns(df):
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]


def add_column(df, name, a, op, b) -> pd.DataFrame:
    """New column = a (op) b. a is a column; b is a column name or a number. Division by zero gives a blank, not infinity."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Give the new column a name.")
    if name in df.columns:
        raise ValueError(f"There is already a column called {name}.")
    if a not in numeric_columns(df):
        raise ValueError(f"{a} is not a number column.")
    right = df[b] if isinstance(b, str) else b
    if isinstance(b, str) and b not in numeric_columns(df):
        raise ValueError(f"{b} is not a number column.")
    out = df.copy()
    with np.errstate(divide="ignore", invalid="ignore"):
        out[name] = OPS[op](df[a].astype("float64"), right if isinstance(b, str) else float(b))
    out[name] = out[name].replace([np.inf, -np.inf], np.nan)
    return out


def keep_rows(df, col, how, value) -> pd.DataFrame:
    """Keep only the rows that match. Everything else is removed from the working copy."""
    s = df[col]
    if how == "contains":
        m = s.astype(str).str.contains(str(value), case=False, regex=False, na=False)
    else:
        if pd.api.types.is_numeric_dtype(s):
            v = float(value)
        elif pd.api.types.is_datetime64_any_dtype(s):
            v = pd.Timestamp(value)
        else:
            v = str(value)
            s = s.astype(str)
        m = {"equals": s == v, "does not equal": s != v, "is greater than": s > v, "is less than": s < v,
             "is at least": s >= v, "is at most": s <= v}[how]
    return df[m.fillna(False)].copy()


def summarise(df, by, col, agg) -> pd.DataFrame:
    fn = AGGS[agg]
    if by is None:
        return pd.DataFrame({col: [getattr(df[col], fn)()]}, index=[agg])
    return df.groupby(by, observed=True)[col].agg(fn).sort_values(ascending=False).rename(f"{agg} of {col}").reset_index()


def for_upload(df, added) -> pd.DataFrame:
    """The edited data as an upload: drop scoring columns and anything the viewer calculated."""
    return df.drop(columns=[c for c in DERIVED + list(added) if c in df.columns]).reset_index(drop=True)


def to_csv(df) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_excel(df) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        d = df.copy()
        for c in d.select_dtypes(include=["datetimetz"]).columns:
            d[c] = d[c].dt.tz_localize(None)
        d.head(1_000_000).to_excel(w, index=False, sheet_name="Data")
    return buf.getvalue()


def to_parquet_buffer(df) -> io.BytesIO:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    return buf
