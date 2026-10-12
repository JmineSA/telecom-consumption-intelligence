"""Build the reference profile that the Data Checks page compares uploads against.

The profile records what the model's training data looked like: usage and bill ranges, churn probability, and
the mix of plans, devices, networks, ages and regions. Run it on your full modelling dataset for the best result:

    python modular/scripts/make_reference_profile.py --input data/processed/train.parquet

(Paths are relative to the project folder. The result goes to modular/assets/reference_profile.json.)
"""
import argparse
import json
from datetime import date

import numpy as np
import pandas as pd

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config  # noqa: E402


def where(p):
    """Paths may be given relative to the project folder (the one holding training/, models/ and modular/)."""
    p = Path(p)
    return p if p.is_absolute() or p.exists() else config.PROJECT_ROOT / p

NUMERIC = ["total_gb", "rolling_30d_avg_gb", "monthly_bill_zar", "churn_probability"]
CATEGORICAL = ["plan_type", "device_type", "network_type", "age_group", "region"]

ap = argparse.ArgumentParser()
ap.add_argument("--input", default=str(config.DEFAULT_DATA))
ap.add_argument("--metadata", default=str(config.PREP_META), help="Training metadata (for the largest value seen)")
ap.add_argument("--out", default=str(config.ASSETS / "reference_profile.json"))
a = ap.parse_args()

df = pd.read_parquet(where(a.input)).drop_duplicates(["user_id", "date"])
profile = {"source": Path(a.input).name, "rows": int(len(df)), "built": date.today().isoformat(), "numeric": {}, "categorical": {}}

for col in NUMERIC:
    x = df[col].dropna().astype(float).to_numpy()
    edges = sorted(set(np.round(np.quantile(x, np.linspace(0.1, 0.9, 9)), 6).tolist()))
    share = np.bincount(np.searchsorted(edges, x, side="right"), minlength=len(edges) + 1) / len(x)
    profile["numeric"][col] = {"median": float(np.median(x)), "p01": float(np.quantile(x, 0.01)),
                               "p99": float(np.quantile(x, 0.99)), "max": float(x.max()),
                               "edges": edges, "share": share.round(6).tolist()}
for col in CATEGORICAL:
    profile["categorical"][col] = df[col].value_counts(normalize=True).round(6).to_dict()
profile["congested_rate"] = float(df["congested"].mean())

meta = Path(a.metadata)
profile["training_max_gb"] = (json.loads(meta.read_text())["target_stats"]["max"] if meta.exists()
                              else float(df["total_gb"].max()))
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
Path(a.out).write_text(json.dumps(profile, indent=2))
print(f"Wrote {a.out}: {profile['rows']:,} rows from {profile['source']}, training max {profile['training_max_gb']:.1f} GB/day")
