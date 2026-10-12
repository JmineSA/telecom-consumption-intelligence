"""Compare two datasets (two periods of the loaded data, or the loaded data against another file)."""
import pandas as pd

from . import kpis
from .config import PRED, TARGET

# (key, label, kind, higher_is_good). kind: int, gb, rand, pct. higher_is_good None means neither direction is good or bad.
MEASURES = [
    ("rows", "Records", "int", None),
    ("customers", "Customers", "int", None),
    ("avg_gb", "Data per customer per day", "gb", None),
    ("bill", "Average monthly bill", "rand", True),
    ("revenue", "Monthly revenue", "rand", True),
    ("at_risk", "Customers at churn risk", "int", False),
    ("at_risk_pct", "Share of customers at churn risk", "pct", False),
    ("revenue_at_risk", "Revenue at risk", "rand", False),
    ("fc_total", "Next-day forecast", "gb0", None),
    ("congested", "Records on congested networks", "pct", False),
    ("mae", "Average forecast error (MAE)", "gb", False),
]


def summary(df, threshold) -> dict:
    """The comparison measures for one dataset. Blank (None) when the data cannot support a measure."""
    if df is None or df.empty:
        return {k: None for k, *_ in MEASURES}
    cust = kpis.latest_per_customer(df)
    risk = cust[cust["churn_probability"] >= threshold]
    m = kpis.metrics(df) if df[TARGET].notna().any() else {}
    return {"rows": len(df), "customers": len(cust), "avg_gb": float(df["total_gb"].mean()),
            "bill": float(cust["monthly_bill_zar"].mean()), "revenue": float(cust["monthly_bill_zar"].sum()),
            "at_risk": len(risk), "at_risk_pct": len(risk) / len(cust), "revenue_at_risk": float(risk["monthly_bill_zar"].sum()),
            "fc_total": float(cust[PRED].sum()), "congested": float(df["congested"].mean()),
            "mae": m.get("mae")}


def fmt(kind, v) -> str:
    if v is None or pd.isna(v):
        return "n/a"
    return {"int": f"{v:,.0f}", "gb": f"{v:,.2f} GB", "gb0": f"{v:,.0f} GB", "rand": f"R {v:,.0f}", "pct": f"{v:.1%}"}[kind]


def table(a: dict, b: dict) -> pd.DataFrame:
    """One row per measure: A, B, change, change in %, and whether the change is good, bad or neutral for the business."""
    rows = []
    for key, name, kind, good in MEASURES:
        x, y = a[key], b[key]
        ok = x is not None and y is not None and not pd.isna(x) and not pd.isna(y)
        diff = (y - x) if ok else None
        pct = (diff / x) if ok and x else None
        if not ok or diff == 0 or good is None or (pct is not None and abs(pct) < 0.01):
            verdict = "neutral"
        else:
            verdict = "good" if (diff > 0) == good else "bad"
        rows.append({"key": key, "Measure": name, "kind": kind, "A": x, "B": y, "Change": diff, "Change %": pct, "verdict": verdict})
    return pd.DataFrame(rows)


def display(t: pd.DataFrame) -> pd.DataFrame:
    """The table as text for people: values with units, signed change."""
    out = pd.DataFrame({"Measure": t["Measure"]})
    out["A"] = [fmt(k, v) for k, v in zip(t["kind"], t["A"])]
    out["B"] = [fmt(k, v) for k, v in zip(t["kind"], t["B"])]
    out["Change"] = ["n/a" if pd.isna(d) or d is None else (f"{d:+.1%}".replace("%", " pts") if k == "pct" else ("+" if d > 0 else "") + fmt(k, d))
                     for k, d in zip(t["kind"], t["Change"])]
    out["Change %"] = ["n/a" if p is None or pd.isna(p) else f"{p:+.1%}" for p in t["Change %"]]
    return out


def headline(t: pd.DataFrame, name_a="A", name_b="B") -> list:
    """Plain-language sentences about what moved most. Only measures that changed by 1% or more."""
    out = []
    moved = t[t["Change %"].notna() & (t["Change %"].abs() >= 0.01) & ~t["key"].isin(["rows"])]
    for _, r in moved.reindex(moved["Change %"].abs().sort_values(ascending=False).index).head(4).iterrows():
        way = "up" if r["Change"] > 0 else "down"
        tone = {"good": " That is good for the business.", "bad": " That needs attention.", "neutral": ""}[r["verdict"]]
        out.append(f"{r['Measure']}: {way} {abs(r['Change %']):.1%} in {name_b} compared with {name_a} "
                   f"({fmt(r['kind'], r['A'])} to {fmt(r['kind'], r['B'])}).{tone}")
    return out or ["The two datasets are within 1% of each other on every measure."]


def by_segment(a, b, col, measure="avg_gb") -> pd.DataFrame:
    """A and B side by side for each value of a column (region, plan, network)."""
    def one(df):
        if df is None or df.empty:
            return pd.Series(dtype=float)
        if measure == "avg_gb":
            return df.groupby(col)["total_gb"].mean()
        if measure == "customers":
            return kpis.latest_per_customer(df).groupby(col)["user_id"].count()
        return kpis.latest_per_customer(df).groupby(col)["monthly_bill_zar"].sum()
    out = pd.concat({"A": one(a), "B": one(b)}, axis=1).fillna(0)
    out["Change %"] = (out["B"] / out["A"].where(out["A"] != 0) - 1)
    return out.sort_values("A", ascending=False)


def common_customers(a, b) -> int:
    return len(set(a["user_id"]) & set(b["user_id"])) if len(a) and len(b) else 0
