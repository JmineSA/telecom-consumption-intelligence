"""Build a pack of synthetic test datasets for the dashboard. All data is made up.

    python modular/scripts/make_test_datasets.py    # writes modular/test_data/*.parquet, *.csv and test_data/README.md

Clean worlds are generated from a few parameters (usage level, plan mix, congestion, weekend behaviour, noise), then
lag features and next-day actuals are built with the app's own feature code. Dirty files are made by damaging a clean one.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config                      # noqa: E402
from src.features import build_features    # noqa: E402

PLANS = list(config.KNOWN["plan_type"])
PLAN_GB = {"Prepaid_Daily": 4.5, "Prepaid_Monthly": 5.9, "Postpaid_Basic": 6.5, "Postpaid_Premium": 8.6, "Postpaid_Unlimited": 10.8}
PLAN_BILL = {"Prepaid_Daily": 152, "Prepaid_Monthly": 274, "Postpaid_Basic": 449, "Postpaid_Premium": 849, "Postpaid_Unlimited": 1347}
PLAN_P = [.181, .24, .203, .216, .161]
REGIONS, REGION_P = ["Gauteng", "Western Cape", "KZN", "Eastern Cape"], [.407, .246, .196, .151]
NETS, NET_P = ["3G", "4G", "4G+", "5G"], [.15, .447, .154, .248]
NET_CONG = {"3G": .35, "4G": .21, "4G+": .15, "5G": .10}
DEVICES, DEVICE_P = ["Basic_Phone", "Mid_Range", "Premium_Smartphone", "Tablet", "5G_Device"], [.099, .347, .297, .049, .208]
AGES, AGE_P = ["18-24", "25-34", "35-44", "45-54", "55+"], [.246, .293, .204, .151, .105]


_POOL = []


def _churn_pool():
    """Churn probabilities of the default sample, so a clean file has the same shape as the training data."""
    if not _POOL:
        _POOL.append(pd.read_parquet(config.DEFAULT_DATA, columns=["user_id", "churn_probability"]).groupby("user_id")["churn_probability"].first().to_numpy())
    return _POOL[0]


def world(n=300, days=60, start="2026-01-05", seed=0, usage=1.0, plan_p=None, net_p=None, cong=1.0, weekend=1.12,
          noise=.27, spikes=.002, cust_sigma=.75, churn=1.0, bill=1.0, region_p=None, id_from=1_000_001, only_region=None, only_plan=None,
          cong_region=None, shift=None) -> pd.DataFrame:
    """Raw daily data for `n` customers over `days` consecutive days (no lag features yet)."""
    r = np.random.default_rng(seed)
    pp = np.array(plan_p or PLAN_P, float); pp /= pp.sum()
    npb = np.array(net_p or NET_P, float); npb /= npb.sum()
    rp = np.array(region_p or REGION_P, float); rp /= rp.sum()
    c = pd.DataFrame({
        "user_id": [f"SUB{id_from + i}" for i in range(n)],
        "plan_type": r.choice(PLANS, n, p=pp), "region": r.choice(REGIONS, n, p=rp),
        "network_type": r.choice(NETS, n, p=npb), "device_type": r.choice(DEVICES, n, p=np.array(DEVICE_P) / sum(DEVICE_P)),
        "age_group": r.choice(AGES, n, p=np.array(AGE_P) / sum(AGE_P))})
    if only_region:
        c["region"] = only_region
    if only_plan:
        c["plan_type"] = only_plan
    c["contract_duration_months"] = r.integers(1, 25, n)
    c["customer_tenure_months"] = r.integers(1, 61, n)
    c["support_calls_6months"] = np.clip(r.poisson(2, n), 0, 10)
    c["monthly_bill_zar"] = (c["plan_type"].map(PLAN_BILL) * r.lognormal(0, .25, n) * bill).clip(50, 1800).round(2)
    base = c["plan_type"].map(PLAN_GB) * r.lognormal(-.28, cust_sigma, n) * usage
    risk = r.choice(_churn_pool(), n) * r.uniform(.97, 1.03, n)
    c["churn_probability"] = np.clip(risk * churn, .015, .95).round(3)
    c["churn_status"] = (r.random(n) < c["churn_probability"] * .8).astype(int)
    d = c.loc[c.index.repeat(days)].reset_index(drop=True)
    d["date"] = np.tile(pd.date_range(start, periods=days), n)
    m = len(d)
    dow = d["date"].dt.dayofweek.to_numpy()
    mult = np.where(dow >= 5, weekend, 1.0) * r.lognormal(0, noise, m) * np.where(r.random(m) < spikes, r.uniform(2, 4, m), 1.0)
    pc = d["network_type"].map(NET_CONG).to_numpy() * cong
    if cong_region:
        pc = np.where(d["region"] == cong_region, .75, pc)
    d["congested"] = (r.random(m) < np.clip(pc, 0, .95)).astype(int)
    after = (d["date"] >= pd.Timestamp(shift["from"])).to_numpy() if shift else np.zeros(m, bool)
    if shift:   # behaviour changes part-way through: same customers, new level
        mult = mult * np.where(after, shift.get("usage", 1.0), 1.0)
        d["churn_probability"] = np.where(after, np.clip(d["churn_probability"] * shift.get("churn", 1.0), .015, .95), d["churn_probability"]).round(3)
        d["monthly_bill_zar"] = np.where(after, d["monthly_bill_zar"] * shift.get("bill", 1.0), d["monthly_bill_zar"]).round(2)
    total = np.repeat(base.to_numpy(), days) * mult * np.where(d["congested"] == 1, .88, 1.0)
    split = np.array([.617, .205, .139, .0136, .0245])       # streaming, social, gaming, messaging, background
    for col, share in zip(["streaming_gb", "social_gb", "gaming_gb", "messaging_gb", "background_gb"], split):
        d[col] = (total * share * r.lognormal(0, .12, m)).round(4)
    d["total_gb"] = d[["streaming_gb", "social_gb", "gaming_gb", "messaging_gb", "background_gb"]].sum(axis=1).round(4)
    d["arpu"] = (d["monthly_bill_zar"] * r.lognormal(-.1, .4, m)).round(2)
    return d


def finish(d) -> pd.DataFrame:
    """Add lag and rolling features, calendar columns and next-day actuals. Drops each customer's first day (no history)."""
    f = build_features(d)
    f = f.dropna(subset=["lag_1d_total_gb"])
    cols = [c for c in pd.read_parquet(config.DEFAULT_DATA).columns if c in f.columns]
    return f[cols].reset_index(drop=True)


def raw_only(f) -> pd.DataFrame:
    return f[[c for c in config.REQUIRED_RAW if c in f.columns]]


# ----------------------------------------------------------------- damage helpers
def _rng(seed): return np.random.default_rng(seed)


def blank(f, cols, share, seed):
    f = f.copy(); r = _rng(seed)
    for c in cols:
        f.loc[r.random(len(f)) < share, c] = np.nan
    return f


def dup(f, share, seed):
    r = _rng(seed)
    return pd.concat([f, f.sample(frac=share, random_state=seed)]).sample(frac=1, random_state=seed + 1).reset_index(drop=True)


def damage_values(f, share, seed):
    f = f.copy(); r = _rng(seed); n = len(f)
    pick = lambda: r.random(n) < share / 3
    f.loc[pick(), "streaming_gb"] = -5.0
    f.loc[pick(), "churn_probability"] = 1.7
    f.loc[pick(), "monthly_bill_zar"] = -100.0
    return f


def outliers(f, share, seed):
    f = f.copy(); r = _rng(seed); m = r.random(len(f)) < share
    for c in ["streaming_gb", "total_gb", "lag_1d_total_gb"]:
        f.loc[m, c] = f.loc[m, c] * 60
    return f


def text_numbers(f, share, seed):
    f = f.copy().astype({"total_gb": "object", "monthly_bill_zar": "object"}); r = _rng(seed)
    m = r.random(len(f)) < share
    f.loc[m, "total_gb"] = r.choice(["N/A", "unknown", "7,5GB", "--"], m.sum())
    m2 = r.random(len(f)) < share
    f.loc[m2, "monthly_bill_zar"] = "R" + f.loc[m2, "monthly_bill_zar"].astype(float).round(0).astype(int).astype(str)
    return f


def unseen(f, share, seed):
    f = f.copy(); r = _rng(seed); m = r.random(len(f)) < share
    f.loc[m, "plan_type"] = "Postpaid_Elite"
    f.loc[r.random(len(f)) < share, "network_type"] = "6G"
    f.loc[r.random(len(f)) < share, "region"] = "Limpopo"
    return f


def scenarios(small: bool = False) -> list:
    """(file name, DataFrame, group, what it tests). Order is the order in the README."""
    S = []
    add = lambda name, df, group, what: S.append((name, df, group, what))
    k = .45 if small else 1.0
    N = lambda n: max(40, int(n * k))

    base = finish(world(N(400), 70, seed=1))
    add("01_baseline_clean.parquet", base, "Baseline", "Healthy reference: should be ready, model health Healthy, little or no drift.")
    dirty = finish(world(N(150), 45, seed=2, id_from=2_000_001))
    add("02_dirty_missing_values.csv", blank(blank(dirty, ["total_gb", "plan_type", "monthly_bill_zar", "region"], .06, 3), ["user_id"], .01, 4),
        "Data Checks", "Missing values and a few missing IDs. Expect warnings, rows with gaps in key columns are dropped.")
    add("03_dirty_duplicates.csv", dup(dirty, .12, 5), "Data Checks", "12% duplicate customer-day rows. Expect a duplicates warning and cleaning.")
    add("04_dirty_impossible_values.csv", damage_values(dirty, .03, 6), "Data Checks",
        "Negative usage and bills, churn probability above 1 (3% of rows). Expect a warning and removal of those rows.")
    add("05_dirty_outliers.csv", outliers(dirty, .03, 7), "Data Checks", "A few usage values 60 times too large. Expect an outlier warning.")
    add("06_dirty_text_numbers.csv", text_numbers(dirty, .04, 8), "Data Checks", "Numbers stored as text ('N/A', '7,5GB', 'R450'). Tests type checks and cleaning.")
    add("07_critical_missing_columns.csv", dirty.drop(columns=["plan_type", "region", "total_gb"]), "Data Checks",
        "Required columns missing. Expect NOT READY FOR SCORING, previous data stays loaded.")
    add("08_critical_mostly_bad_values.csv", damage_values(dirty, .9, 9), "Data Checks", "About 90% of rows break a rule. Expect NOT READY.")
    mb = dirty.copy()
    for c in ["streaming_gb", "social_gb", "gaming_gb", "messaging_gb", "background_gb", "total_gb", "lag_1d_total_gb", "lag_7d_total_gb",
              "rolling_7d_avg_gb", "rolling_30d_avg_gb", "lag_1d_streaming_gb", "lag_1d_social_gb", "lag_1d_gaming_gb",
              "lag_1d_messaging_gb", "target_next_day_gb"]:
        mb[c] = mb[c] * 1024
    add("09_unit_mismatch_megabytes.csv", mb, "Data Checks", "Usage in MB instead of GB (x1024). Tests the unit-mismatch check and the effect on forecasts.")
    add("10_warning_too_few_rows.csv", dirty.head(300), "Data Checks", "Only 300 rows. Expect warnings (very small files give unstable averages); scoring continues.")
    add("11_critical_empty_headers_only.csv", dirty.head(0), "Data Checks", "Headers but no rows. Expect NOT READY.")
    add("12_warning_unseen_categories.csv", unseen(dirty, .15, 10), "Data Checks", "New plan, region and network values the model never saw. Expect warnings.")
    ex = dirty.sample(frac=1, random_state=11, axis=1).copy()
    ex["internal_notes"] = "ok"; ex["campaign_code"] = "SPRING26"
    ex["region"] = ex["region"].replace({"Gauteng": "gauteng"}); ex["plan_type"] = ex["plan_type"].astype(str) + " "
    add("13_extra_columns_shuffled.csv", ex, "Data Checks", "Extra columns, shuffled column order, 'gauteng' spelling, stray spaces. Should load; tests cleaning.")
    add("14_raw_only_no_lag_features.parquet", raw_only(dirty), "Data Checks", "Only raw daily columns. Tests that lag features and actuals are built from consecutive days.")
    noact = base.copy(); noact["target_next_day_gb"] = np.nan
    add("15_no_actuals_forecast_only.parquet", noact, "Data Checks", "No next-day actuals. Forecasts work, accuracy cannot be measured (Monitoring says so).")

    add("20_drift_usage_up_35pct.parquet", finish(world(N(400), 70, seed=20, usage=1.35)), "Drift and model", "Everyone uses 35% more data. Expect distribution warnings; error grows.")
    add("21_drift_plan_and_network_mix.parquet", finish(world(N(400), 70, seed=21, plan_p=[.45, .3, .1, .1, .05], net_p=[.4, .4, .1, .1])),
        "Drift and model", "More prepaid and 3G customers. Tests categorical drift and revenue changes.")
    add("22_drift_congestion_heavy.parquet", finish(world(N(400), 70, seed=22, cong=2.6)), "Drift and model", "Congestion on over half of records. Tests the congestion alerts and forecast error.")
    add("23_drift_weekend_behaviour.parquet", finish(world(N(400), 70, seed=23, weekend=1.9)), "Drift and model",
        "Weekend use nearly doubles. Inputs look similar but forecasts get worse (concept drift). Watch model health.")
    add("24_model_noisy_behaviour.parquet", finish(world(N(400), 70, seed=24, noise=.7, spikes=.05)), "Drift and model",
        "Very erratic daily use. Expect model health Watch or Action needed.")
    add("25_retrain_friendly_long_history.parquet", finish(world(N(200), 150, seed=25, start="2025-11-01")), "Drift and model",
        "150 days per customer. Use for the Retrain button, then compare original and retrained model.")

    two = finish(world(N(350), 61, seed=30, start="2026-08-01", id_from=3_000_001, shift=dict(**{"from": "2026-09-01"}, usage=1.10, churn=1.25, bill=1.05)))
    aug = two[two["date"] < "2026-09-01"]
    keep = sorted(two["user_id"].unique())[: int(two["user_id"].nunique() * .9)]          # 10% of customers left in September
    newc = finish(world(N(60), 30, seed=32, start="2026-09-01", id_from=3_900_001, usage=1.10, churn=1.25, bill=1.05))
    sep = pd.concat([two[(two["date"] >= "2026-09-01") & two["user_id"].isin(keep)], newc], ignore_index=True)
    add("30_compare_august.parquet", aug, "Compare", "Period A for Compare Data (load this one first).")
    add("31_compare_september.parquet", sep, "Compare",
        "Period B: same customers a month later with usage +10%, churn risk +25%, bills +5%, 10% of customers gone, 60 new. Use 'Loaded data against another file'.")
    add("32_compare_two_months_in_one_file.parquet", pd.concat([two, newc], ignore_index=True), "Compare",
        "August and September in one file. Use 'Two periods in the loaded data' (last 30 days against the 30 days before).")

    add("40_high_churn_risk.parquet", finish(world(N(400), 70, seed=40, churn=2.6)), "Whole dashboard", "Many customers at churn risk. Red risk cards, Business Actions, revenue at risk.")
    add("41_single_region_single_plan.csv", finish(world(N(150), 45, seed=41, only_region="Gauteng", only_plan="Postpaid_Premium", id_from=4_000_001)),
        "Whole dashboard", "One region and one plan. Tests charts and tables with a single group.")
    add("42_large_performance.parquet", finish(world(2200 if not small else 400, 70, seed=42, id_from=5_000_001)), "Whole dashboard", "About 150,000 rows. Tests speed and memory.")
    add("43_congestion_hotspot_eastern_cape.parquet", finish(world(N(400), 70, seed=43, cong_region="Eastern Cape")), "Whole dashboard",
        "Eastern Cape heavily congested. Tests Geography, network alerts and capacity story.")
    return S


def outcome(path) -> str:
    """Run the file through the app's own Data Checks and scoring and say what happened."""
    import json
    import warnings
    warnings.filterwarnings("ignore")
    from src import data_loader, kpis, scoring
    with open(path, "rb") as fh:
        df, q, _ = data_loader.ingest(fh, path.name, path.stat().st_size)
    bits = ["READY FOR SCORING" if q.ready else "NOT READY FOR SCORING"]
    if q.count("crit"):
        bits.append(f"{q.count('crit')} critical")
    if q.count("warn"):
        bits.append(f"{q.count('warn')} warning" + ("s" if q.count("warn") > 1 else ""))
    flagged = [c.name for c in q.checks if c.status != "pass"]
    out = ", ".join(bits) + (f" ({'; '.join(flagged[:4])})" if flagged else "")
    if df is not None:
        m = kpis.metrics(scoring.score(df))
        if m:
            ref = json.loads(config.MODEL_INFO.read_text())["val_metrics"]["mae"]
            r = m["mae"] / ref
            out += f". Model health: {'Healthy' if r <= 1.10 else 'Watch' if r <= 1.25 else 'Action needed'} (error {r:.2f} times training)"
        else:
            out += ". No next-day actuals, so accuracy is not measured"
    return out


def write_readme(out, sc):
    L = ["# Test datasets", "", "Made-up data for testing the dashboard. Upload one at a time with **Upload new data** in the sidebar "
         "(or the second-file box on Compare Data). The last column was produced by running each file through the app's own checks, "
         "so it is what you should see. Re-create the pack with `python scripts/make_test_datasets.py`.", "",
         "Start with `01_baseline_clean`: it should be ready with no warnings and a Healthy model. Then try the rest.", ""]
    group = None
    for name, df, g, what in sc:
        if g != group:
            L += ["", f"## {g}", "", "| File | Rows | What it tests | What you should see |", "|---|---|---|---|"]
            group = g
        L.append(f"| `{name}` | {len(df):,} | {what} | {outcome(out / name)} |")
    L += ["", "## Suggested order", "",
          "1. **Data Checks:** upload 01, then 02 to 06 (warnings, scoring continues), then 07, 08, 09 and 11 (blocked: the dashboard keeps the previous data and shows why).",
          "2. **Data viewer:** on the Data Checks page, open View data on 01, add a calculated column, delete a few rows, and press Check and use this data.",
          "3. **Drift and model:** load 01, then 20 to 24 in turn and watch Model Monitoring health and the distribution checks. Calculate SHAP on 01 and on 23.",
          "4. **Retrain:** load 25 and press Retrain model.",
          "5. **Compare Data:** load 30, choose Loaded data against another file, and upload 31. Or load 32 and compare two periods.",
          "6. **Whole dashboard:** 40 (risk cards and Business Actions), 41 (single group), 43 (regional congestion), 42 (speed on 150,000 rows).",
          "", "Notes: every file is synthetic and generated from a random seed. The usual warnings about the history per customer do not appear here "
          "because these files have consecutive days for every customer.", ""]
    (out / "README.md").write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "test_data"))
    ap.add_argument("--small", action="store_true", help="smaller files, for tests")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(exist_ok=True)
    sc = scenarios(a.small)
    for name, df, *_ in sc:
        p = out / name
        df.to_csv(p, index=False) if name.endswith(".csv") else df.to_parquet(p, index=False)
        print(f"{name}: {len(df):,} rows")
    write_readme(out, sc)
    print("README.md written")


if __name__ == "__main__":
    main()
