# 📶 Telecom Consumption Intelligence

**Domain:** Mobile data consumption forecasting for South African telecom operators
**Type:** End-to-end data science portfolio project
**Status:** Complete — ready for review

> ⚠️ **Disclaimer:** This project uses synthetically generated data designed to simulate South African telecom subscriber behaviour (Vodacom / MTN / Telkom / Cell C / Rain plan tiers). No real customer, billing, or network data is included. Architecture and methodology are production-grade; specific metric values will differ on real operator data.

---

## 🎯 Problem

Telecom operators need to forecast how much data each subscriber will consume **tomorrow** to:

- Pre-provision network capacity
- Personalise data bundles and top-up offers
- Detect churn signals from declining consumption
- Forecast usage-based revenue

This project delivers a machine learning system that predicts next-day usage per subscriber, translates predictions into revenue implications, and produces actionable business recommendations.

---

## 📊 Headline Results

| Metric | Train | Validation | Test |
|---|---:|---:|---:|
| R² | 0.7748 | 0.7626 | **0.7698** |
| RMSE (GB) | 3.339 | 3.486 | 3.379 |
| MAE (GB) | 1.971 | 2.025 | **2.021** |

- **Overfit gap** (train − val R²): **0.0122** — healthy
- **Test R² = 0.77** — the model explains 77% of tomorrow's usage variance
- **Typical error = 2 GB per subscriber per day**

### Key finding — Network congestion

During congested network conditions, prediction error rises relative to usage. This has direct implications for capacity planning: forecasts used naively will over-provision during peak windows.

---

## 🏗️ Architecture
┌─────────────────────────────┐
│ Synthetic Data Generator │
│ 10K users × 90 days │
│ + 3% MCAR missing │
│ + 1% duplicate rows │
│ + congestion + drift │
└──────────────┬──────────────┘
│
▼
┌─────────────────────────────┐
│ Data Preparation │
│ - Fix typos (no impute) │
│ - Build lag features │
│ - Build D+1 target │
│ - Drop NaN rows (~3%) │
│ - Time-based split │
└──────────────┬──────────────┘
│
▼
┌─────────────────────────────┐
│ Preprocessing Pipeline │
│ - Drop leakage columns │
│ - Ordinal encode cats │
│ - Cyclical calendar │
└──────────────┬──────────────┘
│
▼
┌─────────────────────────────┐
│ HistGradientBoosting │
│ Regression Model │
│ R² = 0.77 │
└─────────────────────────────┘

---

## 🎯 Key Design Decisions

### Target definition
Predict `target_next_day_gb` — tomorrow's total usage — using only features known at end of today. No same-day features. No target leakage.

### Lag features
All lag features are past-only:
- `lag_1d_total_gb` — yesterday's usage
- `rolling_7d_avg_gb` — past 7 days average
- `rolling_30d_avg_gb` — past 30 days average

Early-day fallbacks use `lag_1d_total_gb` (available at prediction time) — **never backfilled from future values**.

### Time-based split
Train (70%) → Validation (15%) → Test (15%) ordered by date. No random shuffling. Test set is strictly after training — the realistic forecasting setup.

### Missing value policy
Missingness is ~3% MCAR. Below the 5% threshold, so rows are **dropped** rather than imputed. Eliminates any imputation-leakage questions.

### Model selection
Benchmarked 7 models. All tree models within 0.007 R² of each other. Chose **HistGradientBoostingRegressor** because:

- Same accuracy as the best
- 88× faster training than plain GradientBoosting
- 100× smaller artifact than RandomForest
- Sklearn-native (no extra dependencies)
- Native NaN handling

---

## 📁 Project Structure

```text
telecom-consumption-intelligence/
│
├── data/
│   ├── raw/                              # Generated data (not committed)
│   │   ├── users.csv
│   │   └── daily_usage.parquet
│   │
│   └── processed/                        # Splits (not committed)
│       ├── train.parquet
│       ├── val.parquet
│       ├── test.parquet
│       └── preparation_metadata.json
│
├── training/                             # ML training pipeline
│   ├── core/
│   │   ├── data_generator.py             # Synthetic data generation
│   │   ├── data_preparation.py           # Features + time split
│   │   └── custom_transformers.py        # DropColumns, CyclicalDayOfWeek
│   │
│   ├── pipelines/
│   │   ├── preprocessing_pipeline.py     # sklearn ColumnTransformer
│   │   └── training_pipeline.py          # Full pipeline (preproc + model)
│   │
│   ├── models/
│   │   ├── mobile_data_consumption_model.py  # Train script
│   │   ├── compare_models.py                 # Model comparison
│   │   └── model_insights.py                 # Permutation + congestion
│   │
│   └── evaluation/
│       └── evaluate_model.py             # Test-set evaluation
│
├── modular/                              # Streamlit application
│   ├── app.py
│   └── src/
│       ├── analytics/
│       ├── data/
│       ├── models/
│       ├── ui/
│       └── visualizations/
│
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 03_insights_and_recommendations.ipynb
│   └── 04_final_report.ipynb             # Auto-generated report
│
├── models/
│   ├── mobile_data_consumption_pipeline.pkl
│   └── model_info.json
│
├── reports/
│   ├── business_summary.txt              # Auto-generated narrative
│   ├── feature_importance.csv
│   ├── congestion_breakdown.csv
│   ├── evaluation_results.json
│   └── insights/                         # Auto-generated charts
│
├── requirements.txt
└── README.md