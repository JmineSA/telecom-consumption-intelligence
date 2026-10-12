"""Data quality gate: is this dataset valid and safe to use for scoring?

Every check returns a status and says what it means for the business and for the model:

    pass  acceptable
    warn  scoring can continue, attention recommended
    crit  scoring is blocked

A dataset is READY FOR SCORING when it has no critical check. This module only reads pandas data, so it can be
tested without Streamlit.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from .config import (CALENDAR, ENGINEERED, KNOWN, MAX_ROWS, MODEL_REQUIRED, OPTIONAL_RAW, REFERENCE_PROFILE,
                     REQUIRED_RAW, TARGET)

PASS, WARN, CRIT = "pass", "warn", "crit"
LABEL = {PASS: "Passed", WARN: "Warning", CRIT: "Critical"}

# ---- thresholds (shown on the Data Checks page, so they live in one place)
MIN_ROWS, MIN_CUSTOMERS, MIN_DAYS, MIN_ROWS_COMPARE = 1_000, 100, 30, 500
BAD_VALUE_CRIT = 0.05          # unreadable or impossible values
MISSING_CRIT = 0.20            # missing values in a model column
ID_MISSING_CRIT = 0.05         # missing customer IDs or dates
DUPLICATE_CRIT = 0.25
OUTLIER_CRIT = 0.10
OUTLIER_MULTIPLE = 1.25        # times the largest daily usage seen in training
UNSEEN_CRIT = 0.30
PSI_WARN = 0.10                # 0.10 to 0.25 is a moderate shift, above 0.25 a large one
UNIT_RATIO = 5.0               # median usage this many times higher or lower than training
CONGESTION_SHIFT = 0.15
GAP_WARN = 0.20                # share of day-to-day steps that skip a day

THRESHOLDS = [
    ("Rows in the file", f"Fewer than {MIN_ROWS:,}", f"More than {MAX_ROWS:,} (memory limit)"),
    ("Required columns", "None", "Any missing"),
    ("Unexpected columns", "Any", "None"),
    ("Numbers and dates readable", "Up to 5% unreadable", "More than 5% unreadable"),
    ("Missing customer IDs or dates", "Any", "More than 5% of rows"),
    ("Missing values in model columns", "Any", "More than 20% in a column"),
    ("Duplicate records", "Any", "More than 25% of rows"),
    ("Impossible values", "Up to 5% of rows", "More than 5% of rows"),
    ("Extreme daily usage", f"Any above {OUTLIER_MULTIPLE}x the training maximum", "More than 10% of rows"),
    ("Usage level and shape vs training", "PSI above 0.10", f"Median usage {UNIT_RATIO:g}x higher or lower (likely wrong unit)"),
    ("Unseen plan, device, network or age values", "Any", "More than 30% of rows"),
    ("History per customer", f"Under {MIN_DAYS} days, or many missing days", "None"),
]

# What a missing column costs.
COLUMN_IMPACT = {
    "user_id": "customers cannot be followed from day to day, so lag features and customer counts fail",
    "date": "the order of days is unknown, so lags, rolling averages and forecast dates cannot be built",
    "total_gb": "usage KPIs, the usage trend and every lag feature depend on it",
    "streaming_gb": "the model's streaming lag feature", "social_gb": "the model's social lag feature",
    "messaging_gb": "the model's messaging lag feature", "gaming_gb": "the model's gaming lag feature",
    "congested": "the model's congestion feature and the congestion analysis",
    "plan_type": "the model's plan feature and every plan breakdown",
    "device_type": "the model's device feature and device insights",
    "network_type": "the model's network feature and network breakdowns",
    "age_group": "the model's age feature and age-group insights",
    "region": "the Geography page and regional capacity view",
    "contract_duration_months": "a model feature", "customer_tenure_months": "a model feature",
    "support_calls_6months": "a model feature",
    "monthly_bill_zar": "a model feature and every revenue figure",
    "churn_probability": "a model feature, churn-risk counts and revenue at risk",
}

USAGE_COLS = ["streaming_gb", "social_gb", "messaging_gb", "gaming_gb", "background_gb", "total_gb"]
CATEGORICAL = ["plan_type", "device_type", "network_type", "age_group", "region"]
MODEL_CATEGORICAL = ["plan_type", "device_type", "network_type", "age_group"]
NUMERIC = [c for c in REQUIRED_RAW + OPTIONAL_RAW if c not in CATEGORICAL + ["user_id", "date"]]
NUMERIC = list(dict.fromkeys(NUMERIC + ENGINEERED + CALENDAR + [TARGET]))
KNOWN_COLUMNS = set(REQUIRED_RAW + OPTIONAL_RAW + ENGINEERED + CALENDAR + [TARGET])


@dataclass
class Check:
    group: str
    name: str
    status: str
    finding: str
    impact: str = ""
    action: str = ""


@dataclass
class Report:
    source: str
    checks: list = field(default_factory=list)
    rows_in: int | None = None
    rows_scored: int | None = None
    customers: int | None = None
    actions_taken: list = field(default_factory=list)
    stopped_early: str = ""

    def add(self, group, name, status, finding, impact="", action=""):
        self.checks.append(Check(group, name, status, finding, impact, action))

    def count(self, status) -> int:
        return sum(c.status == status for c in self.checks)

    @property
    def ready(self) -> bool:
        return bool(self.checks) and self.count(CRIT) == 0

    @property
    def groups(self) -> list:
        return list(dict.fromkeys(c.group for c in self.checks))


def _pct(x: float) -> str:
    return f"{x:.1%}" if x >= 0.001 or x == 0 else "under 0.1%"


def _grade(share: float, crit_at: float) -> str:
    return PASS if share <= 0 else (CRIT if share > crit_at else WARN)


# ------------------------------------------------------------------ reading and coercion
def coerce(df: pd.DataFrame) -> dict:
    """Make columns the right type, in place. Returns how many values could not be read, per column."""
    bad = {}
    if "date" in df.columns:
        raw = df["date"]
        parsed = pd.to_datetime(raw, errors="coerce")
        if parsed.isna().mean() > 0.5:  # mixed formats
            try:
                alt = pd.to_datetime(raw, errors="coerce", format="mixed")
                parsed = alt if alt.isna().sum() < parsed.isna().sum() else parsed
            except Exception:
                pass
        bad["date"] = int((parsed.isna() & raw.notna()).sum())
        df["date"] = parsed
    for col in NUMERIC:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            raw = df[col]
            num = pd.to_numeric(raw, errors="coerce")
            bad[col] = int((num.isna() & raw.notna()).sum())
            df[col] = num
        elif col in df.columns and pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(int)
    for col in CATEGORICAL:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype("string").str.strip().astype("object")
    if "region" in df.columns:
        df["region"] = df["region"].replace({"gauteng": "Gauteng", "GP": "Gauteng"})
    return bad


def impossible(df: pd.DataFrame):
    """Rows that break a rule of the real world. Returns (mask, {rule: rows})."""
    rules = {}
    def add(label, mask):
        n = int(mask.sum())
        if n:
            rules[label] = (mask, n)
    usage = [c for c in USAGE_COLS if c in df.columns]
    if usage:
        add("negative data usage", (df[usage] < 0).any(axis=1))
    money = [c for c in ("monthly_bill_zar", "arpu") if c in df.columns]
    if money:
        add("negative bill or revenue", (df[money] < 0).any(axis=1))
    counts = [c for c in ("contract_duration_months", "customer_tenure_months", "support_calls_6months") if c in df.columns]
    if counts:
        add("negative tenure, contract or support calls", (df[counts] < 0).any(axis=1))
    if "churn_probability" in df.columns:
        add("churn probability outside 0 to 1", (df["churn_probability"] < 0) | (df["churn_probability"] > 1))
    for col, label in (("congested", "congested flag not 0 or 1"), ("churn_status", "churn status not 0 or 1")):
        if col in df.columns:
            add(label, df[col].notna() & ~df[col].isin([0, 1]))
    mask = pd.Series(False, index=df.index)
    for m, _ in rules.values():
        mask |= m
    return mask, {k: n for k, (_, n) in rules.items()}


@lru_cache(maxsize=1)
def reference() -> dict | None:
    try:
        return json.loads(Path(REFERENCE_PROFILE).read_text())
    except Exception:
        return None


def psi_numeric(values: np.ndarray, edges: list, ref_share: list) -> float:
    x = values[~np.isnan(values)]
    if len(x) == 0:
        return float("nan")
    act = np.bincount(np.searchsorted(edges, x, side="right"), minlength=len(edges) + 1) / len(x)
    a, e = np.clip(act, 1e-4, None), np.clip(np.asarray(ref_share), 1e-4, None)
    return float(((a - e) * np.log(a / e)).sum())


def psi_categorical(values: pd.Series, ref_share: dict) -> float:
    act = values.dropna().value_counts(normalize=True).to_dict()
    cats = set(act) | set(ref_share)
    a = np.clip(np.array([act.get(c, 0.0) for c in cats]), 1e-4, None)
    e = np.clip(np.array([ref_share.get(c, 0.0) for c in cats]), 1e-4, None)
    return float(((a - e) * np.log(a / e)).sum())


# ------------------------------------------------------------------ the checks
def file_checks(rep: Report, name: str, size: int | None, error: str = "", rows: int | None = None):
    suffix = Path(name).suffix.lower()
    G = "File"
    if suffix not in (".csv", ".parquet"):
        rep.add(G, "File type", CRIT, f"{suffix or 'No extension'} is not supported.",
                "The app can only read CSV or Parquet files, so nothing can be scored.", "Save the data as CSV or Parquet and upload again.")
        return
    rep.add(G, "File type", PASS, f"{suffix[1:].upper()} file.")
    if size == 0:
        rep.add(G, "File is not empty", CRIT, "The file has no content.", "There is nothing to score.", "Export the data again and check the file.")
        return
    if error:
        rep.add(G, "File can be read", CRIT, error, "The file is damaged or not in the expected format, so nothing can be scored.",
                "Re-export the file and upload it again.")
        return
    rep.add(G, "File can be read", PASS, "Opened without errors." if size is None else f"Opened without errors ({size / 1e6:,.1f} MB).")
    if rows == 0:
        rep.add(G, "File is not empty", CRIT, "The file has a header but no rows.", "There is nothing to score.", "Check the export filters.")
    elif rows is not None and rows > MAX_ROWS:
        rep.add(G, "Rows in the file", CRIT, f"{rows:,} rows. The limit is {MAX_ROWS:,}.",
                "A file this large can run the app out of memory, so scoring is blocked to protect it.",
                f"Upload fewer customers or fewer days. The limit can be raised with MAX_UPLOAD_ROWS on a machine with more memory.")
        rep.stopped_early = "The remaining checks were not run because the file is too large."
    elif rows is not None and rows < MIN_ROWS:
        rep.add(G, "Rows in the file", WARN, f"{rows:,} rows.", "Very small files give unstable averages and weak segment comparisons.",
                "Use a larger extract if you can.")
    elif rows is not None:
        rep.add(G, "Rows in the file", PASS, f"{rows:,} rows.")


def schema_checks(rep: Report, df: pd.DataFrame) -> bool:
    """Returns False when required columns are missing, because the other checks cannot run."""
    G = "Schema"
    cols = set(df.columns)
    missing = [c for c in MODEL_REQUIRED if c not in cols]
    if missing:
        detail = "; ".join(f"{c} ({COLUMN_IMPACT.get(c, 'needed by the model')})" for c in missing[:6])
        more = f" and {len(missing) - 6} more" if len(missing) > 6 else ""
        rep.add(G, "Required columns", CRIT, f"Missing: {', '.join(missing[:12])}.",
                f"Without these columns the dashboard cannot score reliably. Affected: {detail}{more}.",
                "Add the missing columns to the file. The Upload format section of the README lists them all.")
        rep.stopped_early = "The remaining checks were not run because required columns are missing."
        return False
    rep.add(G, "Required columns", PASS, f"All {len(MODEL_REQUIRED)} required columns are present.")
    absent = [c for c in OPTIONAL_RAW if c not in cols]
    rep.add(G, "Optional columns", PASS,
            "All present." if not absent else f"Not present: {', '.join(absent)}.",
            "" if not absent else "These columns are not used by the model or any dashboard page, so nothing is lost.")
    extra = [c for c in df.columns if c not in KNOWN_COLUMNS]
    if extra:
        rep.add(G, "Unexpected columns", WARN, f"{len(extra)} column(s) not used: {', '.join(map(str, extra[:8]))}{'...' if len(extra) > 8 else ''}.",
                "They are ignored, so forecasts are not affected. Columns like 'Unnamed: 0' usually mean an index was exported by mistake.",
                "Check that this is the intended export.")
    else:
        rep.add(G, "Unexpected columns", PASS, "None.")
    have = [c for c in ENGINEERED if c in cols]
    if len(have) == len(ENGINEERED):
        rep.add(G, "Lag and rolling features", PASS, "Provided in the file and used as they are.")
    elif have:
        rep.add(G, "Lag and rolling features", WARN, f"Only {len(have)} of {len(ENGINEERED)} are present.",
                "The provided ones are replaced: all lag and rolling features are rebuilt from daily usage.",
                "Provide all of them, or none.")
    else:
        rep.add(G, "Lag and rolling features", PASS, "Not in the file. They will be built from daily usage.")
    return True


def type_checks(rep: Report, bad: dict, n: int):
    G = "Schema"
    worst = sorted(((v / n, c, v) for c, v in bad.items() if v), reverse=True)
    if not worst:
        rep.add(G, "Numbers and dates are readable", PASS, "Every value could be read.")
        return
    share = worst[0][0]
    status = CRIT if share > BAD_VALUE_CRIT else WARN
    listing = ", ".join(f"{c} ({v:,} values, {_pct(s)})" for s, c, v in worst[:5])
    rep.add(G, "Numbers and dates are readable", status, f"Unreadable values in: {listing}.",
            "Text where a number or date should be is treated as missing. "
            + ("Too many are affected, so KPIs and forecasts would be unreliable." if status == CRIT
               else "Affected rows are handled as missing values."),
            "Check for text such as 'N/A', units like 'GB', or a different date format in those columns.")


def completeness_checks(rep: Report, df: pd.DataFrame):
    G = "Completeness"
    n = len(df)
    ids = int(df["user_id"].isna().sum() + (df["date"].isna() & df["user_id"].notna()).sum())
    share = ids / n
    rep.add(G, "Customer IDs and dates", _grade(share, ID_MISSING_CRIT),
            "No missing IDs or dates." if not ids else f"{ids:,} rows ({_pct(share)}) have no customer ID or date.",
            "" if not ids else "These rows cannot be followed from day to day, so they are removed. Too many would leave customer counts and trends unreliable.",
            "" if not ids else "Fill in the IDs and dates at the source.")
    cols = [c for c in MODEL_REQUIRED if c not in ("user_id", "date")]
    miss = df[cols].isna().mean()
    worst = miss[miss > 0].sort_values(ascending=False)
    key = [c for c in ["age_group", "plan_type", "device_type", "network_type", "region"] if c in df.columns]
    drop_n = int(df[key].isna().any(axis=1).sum())
    status = PASS if worst.empty else (CRIT if worst.iloc[0] > MISSING_CRIT else WARN)
    if worst.empty:
        rep.add(G, "Missing values in model columns", PASS, "No missing values.")
    else:
        listing = ", ".join(f"{c} ({_pct(v)})" for c, v in worst.head(5).items())
        rep.add(G, "Missing values in model columns", status, f"Missing in: {listing}.",
                f"{drop_n:,} rows missing a plan, device, network, age group or region are removed, so KPIs cover fewer customers. "
                "Other gaps are scored as unknown, which makes those forecasts less accurate."
                + (" At this level the forecasts would not be dependable." if status == CRIT else ""),
                "Fill the gaps at the source, or accept the rows being dropped.")


def duplicate_checks(rep: Report, df: pd.DataFrame):
    G = "Duplicates"
    keys = ["user_id", "date"]
    ok = df[keys].notna().all(axis=1)
    d = df.loc[ok]
    n_key = int(d.duplicated(keys).sum())
    share = n_key / len(df)
    if n_key == 0:
        rep.add(G, "Duplicate records", PASS, "No customer has two records on the same day.")
        return
    group = d[d.duplicated(keys, keep=False)]
    exact = int(group.duplicated(keep="first").sum())
    conflict = n_key - exact
    rep.add(G, "Duplicate records", _grade(share, DUPLICATE_CRIT),
            f"{n_key:,} extra records ({_pct(share)}): {exact:,} exact copies and {conflict:,} with different values.",
            "The first record per customer and day is kept. Left in, usage and revenue would be counted twice and "
            "yesterday's usage for the next day would be wrong."
            + (" Records with different values mean the source disagrees with itself, so check it." if conflict else ""),
            "Remove duplicates at the source." if not conflict else "Find out which record is correct.")


def value_checks(rep: Report, df: pd.DataFrame, ref: dict | None):
    G = "Values"
    mask, rules = impossible(df)
    n = len(df)
    if not rules:
        rep.add(G, "Impossible values", PASS, "No negative usage, bills or counts, and no probabilities outside 0 to 1.")
    else:
        share = int(mask.sum()) / n
        listing = "; ".join(f"{k} ({v:,} rows)" for k, v in rules.items())
        rep.add(G, "Impossible values", CRIT if share > BAD_VALUE_CRIT else WARN,
                f"{int(mask.sum()):,} rows ({_pct(share)}): {listing}.",
                "These values cannot happen in real life, so the rows are removed. "
                + ("So many rows are affected that the file is probably wrongly exported or mixed with another source." if share > BAD_VALUE_CRIT
                   else "A few bad rows are removed without affecting the results."),
                "Correct the values at the source.")
    comps = [c for c in ("streaming_gb", "social_gb", "messaging_gb", "gaming_gb", "background_gb") if c in df.columns]
    if len(comps) == 5 and "total_gb" in df.columns:
        diff = (df["total_gb"] - df[comps].sum(axis=1)).abs()
        off = int((diff > np.maximum(0.05, 0.01 * df["total_gb"].abs())).sum())
        if off:
            rep.add(G, "Usage adds up", WARN, f"{off:,} rows ({_pct(off / n)}) where total usage differs from the sum of its parts.",
                    "The model uses the parts for its service features and the total for everything else. A mismatch means they describe different things.",
                    "Check how total_gb was calculated.")
        else:
            rep.add(G, "Usage adds up", PASS, "Total usage equals the sum of its parts.")
    if ref and "total_gb" in df.columns:
        limit = OUTLIER_MULTIPLE * ref["training_max_gb"]
        n_out = int((df["total_gb"] > limit).sum())
        share = n_out / n
        if n_out == 0:
            rep.add(G, "Extreme daily usage", PASS, f"Nothing above {limit:,.0f} GB a day.")
        else:
            rep.add(G, "Extreme daily usage", CRIT if share > OUTLIER_CRIT else WARN,
                    f"{n_out:,} rows ({_pct(share)}) above {limit:,.0f} GB a day, the largest in training was {ref['training_max_gb']:,.0f} GB.",
                    "The model cannot predict beyond what it saw in training, so these customers' forecasts will be too low and capacity totals understated. "
                    + ("So many extreme values usually mean the wrong unit, such as MB instead of GB." if share > OUTLIER_CRIT else ""),
                    "Check the unit, and review these customers separately.")


def distribution_checks(rep: Report, df: pd.DataFrame, ref: dict | None):
    G = "Distribution vs training"
    if ref is None:
        rep.add(G, "Comparison with training data", WARN, "The reference profile (models/reference_profile.json) was not found.",
                "Without it the file cannot be compared with the data the model learned from.", "Run scripts/make_reference_profile.py.")
        return
    if len(df) < MIN_ROWS_COMPARE:
        rep.add(G, "Comparison with training data", WARN, f"Skipped: fewer than {MIN_ROWS_COMPARE} rows.",
                "Too few rows to compare shapes reliably.", "Use a larger extract.")
        return
    spec = [("total_gb", "Daily usage", "Usage per customer per day differs from what the model learned, so its forecasts may be off."),
            ("monthly_bill_zar", "Monthly bill", "Customers are priced differently from training, so revenue figures and the model's bill feature may be off."),
            ("churn_probability", "Churn probability", "Churn scores follow a different pattern than in training, so the model's churn feature and churn-risk counts may be off.")]
    med = ref["numeric"]["total_gb"]["median"]
    cur = float(df["total_gb"].median())
    ratio = cur / med if med else float("nan")
    if ratio > UNIT_RATIO or ratio < 1 / UNIT_RATIO:
        rep.add(G, "Usage level", CRIT, f"Median daily usage is {cur:,.2f} GB against {med:,.2f} GB in training ({ratio:,.1f} times).",
                "This is almost always a unit problem, such as MB instead of GB. Forecasts would be meaningless, so scoring is blocked.",
                "Check the unit of the usage columns.")
    else:
        rep.add(G, "Usage level", PASS, f"Median daily usage is {cur:,.2f} GB against {med:,.2f} GB in training.")
    for col, label, why in spec:
        if col not in df.columns:
            continue
        r = ref["numeric"][col]
        v = psi_numeric(df[col].to_numpy(dtype=float), r["edges"], r["share"])
        if np.isnan(v):
            continue
        strength = "large" if v > 0.25 else "moderate"
        rep.add(G, f"{label} shape", WARN if v > PSI_WARN else PASS,
                f"PSI {v:.2f}" + (f", a {strength} shift from training." if v > PSI_WARN else ", close to training."),
                why if v > PSI_WARN else "", "Compare with the data the model was trained on." if v > PSI_WARN else "")
    shifts = []
    for col in CATEGORICAL:
        if col in df.columns:
            shifts.append((psi_categorical(df[col], ref["categorical"][col]), col))
    if shifts:
        top = max(shifts)
        rep.add(G, "Customer mix", WARN if top[0] > PSI_WARN else PASS,
                f"Largest shift: {top[1].replace('_', ' ')} (PSI {top[0]:.2f})." if top[0] > PSI_WARN else "Plans, devices, networks, ages and regions look like training.",
                "The customer base is different from the one the model learned from, so accuracy for the over-represented groups may be lower." if top[0] > PSI_WARN else "",
                "Review the segment mix before relying on forecasts." if top[0] > PSI_WARN else "")
    if "congested" in df.columns:
        rate = float(df["congested"].mean())
        gap = abs(rate - ref["congested_rate"])
        rep.add(G, "Congestion rate", WARN if gap > CONGESTION_SHIFT else PASS,
                f"{_pct(rate)} of records on congested networks, against {_pct(ref['congested_rate'])} in training.",
                "Congestion changes how much customers use and how well the model forecasts, so capacity advice may be off." if gap > CONGESTION_SHIFT else "",
                "Check the congestion flag." if gap > CONGESTION_SHIFT else "")
    unseen = {}
    for col in MODEL_CATEGORICAL:
        if col in df.columns:
            s = df[col].dropna()
            share = float((~s.isin(KNOWN[col])).mean()) if len(s) else 0.0
            if share:
                unseen[col] = share
    if unseen:
        worst = max(unseen.items(), key=lambda kv: kv[1])
        rep.add(G, "Unseen categories", CRIT if worst[1] > UNSEEN_CRIT else WARN,
                "; ".join(f"{k.replace('_', ' ')}: {_pct(v)} of rows" for k, v in unseen.items()) + " have values the model never saw.",
                "These rows are scored with a neutral code, so their forecasts are less reliable."
                + (" With this many, the model is effectively guessing." if worst[1] > UNSEEN_CRIT else ""),
                "Map the new values to existing plans, devices, networks or age groups, or retrain the model.")
    else:
        rep.add(G, "Unseen categories", PASS, "Every plan, device, network and age group is known to the model.")


def readiness_checks(rep: Report, df: pd.DataFrame):
    G = "Scoring readiness"
    cust = df["user_id"].nunique()
    days = (df["date"].max() - df["date"].min()).days + 1 if df["date"].notna().any() else 0
    d = df[["user_id", "date"]].dropna().drop_duplicates().sort_values(["user_id", "date"])
    same = d["user_id"].eq(d["user_id"].shift())
    step = d["date"].diff().dt.days
    pairs = int(same.sum())
    gaps = float(((step > 1) & same).sum() / pairs) if pairs else 0.0
    consecutive = bool(((step == 1) & same).any())
    per = d.groupby("user_id").size().median() if len(d) else 0
    if cust < MIN_CUSTOMERS:
        rep.add(G, "Customers", WARN, f"{cust:,} customers.", "Too few customers for stable segment and regional comparisons.", "Use a larger extract.")
    else:
        rep.add(G, "Customers", PASS, f"{cust:,} customers.")
    if days < MIN_DAYS:
        rep.add(G, "Time coverage", WARN, f"{days} days ({df['date'].min():%d %b %Y} to {df['date'].max():%d %b %Y}).",
                f"The model's 30-day average needs about {MIN_DAYS} days of history, so early forecasts lean on yesterday's usage and are less accurate.",
                "Provide at least 30 days.")
    else:
        rep.add(G, "Time coverage", PASS, f"{days} days ({df['date'].min():%d %b %Y} to {df['date'].max():%d %b %Y}).")
    if gaps > GAP_WARN:
        rep.add(G, "History per customer", WARN, f"{_pct(gaps)} of day-to-day steps skip a day. The median customer has {per:.0f} days.",
                ("The lag features in the file are used as they are, but the top-up and retention rules need days in a row, so they will find few customers."
                 if all(c in df.columns for c in ENGINEERED) else
                 "Lag features are built from the rows provided, so where days are missing yesterday's usage is really older data and forecasts are less accurate."),
                "Provide consecutive daily rows for each customer.")
    else:
        rep.add(G, "History per customer", PASS, f"The median customer has {per:.0f} days with few gaps.")
    has_target = TARGET in df.columns and df[TARGET].notna().any()
    if has_target or consecutive:
        rep.add(G, "Next-day actuals", PASS, "Available, so forecast accuracy can be measured.")
    else:
        rep.add(G, "Next-day actuals", WARN, "No customer has two consecutive days.",
                "Forecasts and KPIs will work, but accuracy cannot be measured, so the Model Monitoring page will be empty.",
                "Include consecutive days if you want accuracy figures.")


def assess(df: pd.DataFrame, rep: Report, coerce_bad: dict) -> Report:
    """Run every check on a coerced dataframe. Adds to `rep`."""
    ref = reference()
    n = len(df)
    type_checks(rep, coerce_bad, n)
    completeness_checks(rep, df)
    duplicate_checks(rep, df)
    value_checks(rep, df, ref)
    distribution_checks(rep, df, ref)
    readiness_checks(rep, df)
    return rep
