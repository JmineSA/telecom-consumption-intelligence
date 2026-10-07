# 📶 Telecom Consumption Intelligence

**Forecasting tomorrow's mobile data demand for South African operators**

An end-to-end machine learning system that predicts how much data each
subscriber will consume tomorrow, quantifies the revenue implications, and
produces actionable recommendations for network, retention, and product teams.

> ⚠️ **Note:** Built on synthetically generated data simulating South African
> telecom subscriber behaviour (Vodacom / MTN / Telkom / Cell C / Rain plan
> tiers). Architecture and methodology are production-grade; specific values
> will differ on real operator data.

---

## 💼 The Business Problem

Every telecom operator faces the same three questions every day:

1. **How much data will subscribers consume tomorrow?** — so they can
   pre-provision network capacity and avoid congestion.
2. **Who is about to use more than expected?** — so they can offer top-ups
   and bundles at the right moment.
3. **Who is quietly disengaging?** — so retention teams can intervene before
   they churn.

Currently, most operators answer these questions with weekly historical
reports — reacting to yesterday rather than preparing for tomorrow.

This project answers them with a daily forecast per subscriber.

---

## 📊 What the Model Delivers

| Question | Answer |
|---|---|
| **How accurate is the forecast?** | 77% of tomorrow's usage variance explained (R² = 0.77) |
| **How close is a typical prediction?** | Within **2 GB** of actual usage per subscriber per day |
| **When does the model struggle?** | During network congestion — prediction error rises |
| **How fast can it retrain?** | ~10 seconds — supports weekly retraining |
| **How big is the model?** | ~10 MB — deployable in-app |

**Headline numbers (test set):**

| Metric | Value |
|---|---:|
| R² | 0.77 |
| MAE | 2.02 GB |
| RMSE | 3.38 GB |
| Overfit gap | 0.012 |

---

## 🎯 Business Value

### 1. Network capacity planning
Forecast tomorrow's aggregate demand by region, plan, and network tier.
Pre-provision capacity where the model expects peaks — instead of reacting
to yesterday's report.

### 2. Personalised top-up offers
When the model persistently under-predicts a subscriber's usage, they're
using more than expected — a natural moment to offer a data top-up. Value
captured without hard-selling.

### 3. Churn early-warning signals
When the model persistently over-predicts — meaning usage is falling —
the subscriber may be disengaging. This is a leading indicator of churn,
captured before it happens.

### 4. Segment-specific bundles
Usage varies 3–4× between plan types and 2× between device tiers. Offers
priced per segment outperform one-size-fits-all bundles.

---

## 🔍 What We Found

### Rolling averages predict better than yesterday's single value

The single strongest signal for tomorrow's usage is not yesterday's usage —
it's the subscriber's recent **rolling average** (7-day and 30-day). Daily
usage is noisy; longer windows smooth that noise and better predict the
habit underneath.

**Implication:** for network planning, forecast from smoothed baselines,
not from yesterday's raw numbers.

### Congestion hurts forecasting accuracy

During congested network conditions, the model over-predicts — because
congestion suppresses actual usage (subscribers give up or defer), but the
model doesn't fully learn that effect.

**Implication:** capacity plans based on these forecasts will over-provision
during peak congestion. A congestion-aware variant of the model is the
recommended follow-up.

### Usage segments differ sharply

- **Postpaid Unlimited** users consume 3–4× more than **Prepaid Daily** users
- **5G device** users consume ~2× more than mid-range smartphone users
- **Gauteng** users consume more than other provinces

**Implication:** targeting and pricing should be segment-specific.

---

## 💡 Recommendations

| # | Recommendation | Owner |
|---|---|---|
| 1 | Deploy congestion-aware forecasting for capacity planning | Network Ops |
| 2 | Retrain the model every 4–6 weeks or on drift detection | Data Science |
| 3 | Trigger top-up offers on 3-day persistent under-prediction (>2 GB) | Product |
| 4 | Route 5-day persistent over-prediction (>2 GB) to retention campaigns | Customer Retention |
| 5 | Design bundles by segment (plan, device, region) | Commercial |

---

## 🧠 How It Works (Non-Technical)

---

## 📈 Model at a Glance

| Aspect | Detail |
|---|---|
| **Type** | Supervised regression (forecasting) |
| **Algorithm** | HistGradientBoostingRegressor (scikit-learn) |
| **Target** | `target_next_day_gb` — tomorrow's usage per subscriber |
| **Features** | 25 (lags, rolling averages, calendar, congestion, profile) |
| **Training data** | 10,000 synthetic users × 90 days = ~817K rows |
| **Train / Val / Test** | 70% / 15% / 15% (time-based, not random) |
| **Test R²** | 0.77 |
| **Test MAE** | 2.02 GB |
| **Training time** | ~10 seconds |
| **Model size** | ~10 MB |

---

## ⚠️ Key Limitations

- **Synthetic data** — behaviour is generated. Real production behaviour
  will differ.
- **90-day window** — insufficient to model annual seasonality.
- **Binary congestion** — real network states are graded.
- **No external signals** — holidays, promotions, and device launches are
  not modelled.

These are deliberate boundaries for a portfolio project, and each one
defines a natural next step.

---

## 🚀 Next Steps

If this project were extended toward production:

1. **Validate on real operator data** — same methodology, real subscriber base
2. **Add external signals** — public holidays, marketing campaigns, new device launches
3. **Congestion-aware model variant** — separate model for congested windows
4. **Automated retraining** — weekly pipeline with validation gates
5. **Monitoring layer** — drift detection, reject thresholds for low-quality inputs
6. **Integration** — feed forecasts into the operator's planning dashboards

---

## 📚 Technical Appendix

### Leakage prevention
The single most important design decision in forecasting is preventing the
model from accidentally seeing tomorrow's data. Every feature is past-only:

- Target built via `shift(-1)` per user
- Lags use `shift(1)` and rolling windows over shifted values
- Early-day fallbacks use `lag_1d_total_gb` (the latest known value) — no
  backfilling from future values
- Time-based split, no random shuffle
- Missing values (~3% MCAR) dropped rather than imputed

### Feature engineering
- **Lag features** — yesterday, 7 days ago, rolling 7-day and 30-day averages
- **Service lags** — per-service yesterday's usage (streaming, social, gaming)
- **Calendar** — day of week, weekend flag, cyclical sine/cosine encodings
- **Network** — congestion indicator
- **Profile** — plan type, device type, network tier, monthly bill (ZAR),
  tenure, churn probability

### Model selection
Benchmarked 7 models. All tree-based models within 0.007 R² of each other.
Chose **HistGradientBoostingRegressor** for:
- Same accuracy as the best candidate
- 88× faster training than plain GradientBoosting
- 100× smaller artifact than RandomForest
- Sklearn-native (no extra dependencies)
- Native NaN handling

### Project structure
```text
telecom-consumption-intelligence/
├── training/                        # ML training pipeline
│   ├── core/                        # Data generation, features, transformers
│   ├── pipelines/                   # sklearn pipelines
│   ├── models/                      # Training scripts + insights
│   └── evaluation/                  # Test-set evaluation
│
├── modular/                         # Streamlit application (demo)
│   ├── app.py
│   └── src/                         # UI, analytics, model loading
│
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 03_insights_and_recommendations.ipynb
│   └── 04_final_report.ipynb        # Auto-generates business_summary.txt
│
├── models/                          # Trained artifacts
├── reports/
│   ├── business_summary.txt         # Auto-generated narrative
│   └── insights/                    # Six charts (PNG)
│
├── requirements.txt
└── README.md