"""Reading, checking and preparing data (default file or an upload)."""
from pathlib import Path

import pandas as pd

from . import quality
from .config import CRITICAL, ENGINEERED, KNOWN, MAX_ROWS, MODEL_REQUIRED, TARGET
from .features import add_calendar, add_target, build_features


class DataError(Exception):
    """A problem with the data that the user can fix. The message says how."""


def _shrink(df: pd.DataFrame) -> pd.DataFrame:
    """Halve the memory of numeric columns. Plenty of precision for GB and rand amounts."""
    for col in df.select_dtypes("float64").columns:
        df[col] = df[col].astype("float32")
    for col in df.select_dtypes("int64").columns:
        if col != "user_id" and df[col].abs().max() < 2**31 - 1:
            df[col] = df[col].astype("int32")
    return df


def read_file(file, name: str, enforce_limit: bool = True) -> pd.DataFrame:
    suffix = Path(name).suffix.lower()
    try:
        if suffix == ".parquet":
            df = pd.read_parquet(file)
        elif suffix == ".csv":
            df = pd.read_csv(file)
        else:
            raise DataError("Upload a CSV or Parquet file.")
    except DataError:
        raise
    except Exception as exc:
        raise DataError(f"{name} could not be read ({type(exc).__name__}). Check that the file is not damaged.") from exc
    if enforce_limit and len(df) > MAX_ROWS:
        raise DataError(f"The file has {len(df):,} rows and the limit is {MAX_ROWS:,}. "
                        "Upload fewer customers or days.")
    return _shrink(df)


def prepare(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean a dataset that passed the checks and return model-ready data plus a report of what was done."""
    if df.empty:
        raise DataError("The file has no rows.")
    missing = [c for c in MODEL_REQUIRED if c not in df.columns]
    if missing:
        raise DataError("Missing columns: " + ", ".join(missing) + ".")

    notes, df = [], df.copy()
    quality.coerce(df)  # right types, tidy text, known region spellings

    n0 = len(df)
    df = df[df["user_id"].notna() & df["date"].notna()]
    if n0 - len(df):
        notes.append(f"Removed {n0 - len(df):,} rows with no customer ID or date.")
    bad_rows, _ = quality.impossible(df)
    if bad_rows.any():
        notes.append(f"Removed {int(bad_rows.sum()):,} rows with impossible values.")
        df = df[~bad_rows]

    n0 = len(df)
    df = df.drop_duplicates(subset=["user_id", "date"], keep="first")
    if n0 - len(df):
        notes.append(f"Removed {n0 - len(df):,} duplicate customer-day rows.")

    built = not all(c in df.columns for c in ENGINEERED)
    if built:
        df = build_features(df)
        before = len(df)
        df = df.dropna(subset=["lag_1d_total_gb"])
        notes.append("Built lag and rolling features from daily usage "
                     f"({before - len(df):,} first-day rows have no history and were dropped).")
    else:
        if "day_of_week" not in df.columns or "day_index" not in df.columns:
            df = add_calendar(df)
        if TARGET not in df.columns:
            df = add_target(df)
            notes.append("Built next-day actuals from total_gb.")

    before = len(df)
    df = df.dropna(subset=CRITICAL)
    if before - len(df):
        notes.append(f"Dropped {before - len(df):,} rows with missing values in key columns.")
    if df.empty:
        raise DataError("No usable rows are left after checks.")

    for col, known in KNOWN.items():
        extra = sorted(set(df[col].dropna().unique()) - set(known))
        if extra:
            notes.append(f"{col} has values the model has not seen ({', '.join(map(str, extra[:4]))}). They are scored with a neutral code.")

    df = df.sort_values(["user_id", "date"]).reset_index(drop=True)
    report = {
        "rows": len(df),
        "customers": int(df["user_id"].nunique()),
        "date_min": df["date"].min(),
        "date_max": df["date"].max(),
        "has_actuals": bool(df[TARGET].notna().any()),
        "built_features": built,
        "notes": notes,
    }
    return df, report


def ingest(file, name: str, size: int | None = None):
    """The data-quality gate. Reads a file, runs every check, and cleans it if it is safe to score.

    Returns (clean_df, quality_report, prep_report). clean_df is None when the dataset is NOT READY FOR SCORING.
    """
    rep = quality.Report(source=name)
    df, err = None, ""
    try:
        df = read_file(file, name, enforce_limit=False)
    except DataError as exc:
        err = str(exc)
    quality.file_checks(rep, name, size, err, None if df is None else len(df))
    if df is None or not rep.ready:
        return None, rep, None
    rep.rows_in = len(df)
    if not quality.schema_checks(rep, df):
        return None, rep, None
    bad = quality.coerce(df)
    quality.assess(df, rep, bad)
    if not rep.ready:
        return None, rep, None
    try:
        clean, prep = prepare(df)
    except DataError as exc:
        rep.add("Scoring readiness", "Preparing the data", quality.CRIT, str(exc),
                "Nothing is left to score after cleaning.", "Fix the issues above and upload again.")
        return None, rep, None
    rep.rows_scored, rep.customers, rep.actions_taken = len(clean), prep["customers"], prep["notes"]
    share = len(clean) / rep.rows_in
    status = quality.PASS if share >= 0.90 else quality.WARN if share >= 0.50 else quality.CRIT
    rep.add("Scoring readiness", "Usable rows", status,
            f"{len(clean):,} of {rep.rows_in:,} rows ({share:.1%}) remain after cleaning.",
            "" if status == quality.PASS else "Cleaning removed a large part of the file, so every figure describes only the rows that remain."
            + (" With this little left, results would not represent the file." if status == quality.CRIT else ""),
            "" if status == quality.PASS else "Fix the issues listed above at the source.")
    if not rep.ready:
        return None, rep, None
    return clean, rep, prep
