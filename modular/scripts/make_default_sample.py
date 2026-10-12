"""Make a small default dataset for deployment: whole customers, every day they have.

Whole customers (not random rows) keep each customer's days together, so the
"days in a row" rules and per-customer charts work on the deployed app.

    python modular/scripts/make_default_sample.py --input data/processed/modelling_dataset.parquet

(Paths are relative to the project folder. The result goes to modular/assets/default_sample.parquet.)
"""
import argparse

import pandas as pd

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config  # noqa: E402


def where(p):
    """Paths may be given relative to the project folder (the one holding training/, models/ and modular/)."""
    p = Path(p)
    return p if p.is_absolute() or p.exists() else config.PROJECT_ROOT / p


ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, help="Full modelling_dataset.parquet")
ap.add_argument("--out", default=str(config.ASSETS / "default_sample.parquet"))
ap.add_argument("--customers", type=int, default=800)
ap.add_argument("--seed", type=int, default=42)
a = ap.parse_args()

df = pd.read_parquet(where(a.input)).drop_duplicates(["user_id", "date"])
ids = df["user_id"].drop_duplicates()
ids = ids.sample(min(a.customers, len(ids)), random_state=a.seed)
out = df[df["user_id"].isin(ids)].sort_values(["user_id", "date"]).reset_index(drop=True)
for col in out.select_dtypes("float64").columns:
    out[col] = out[col].astype("float32")
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
out.to_parquet(a.out, index=False, compression="zstd")
print(f"{len(out):,} rows, {out['user_id'].nunique():,} customers, {Path(a.out).stat().st_size / 1e6:.1f} MB -> {a.out}")
