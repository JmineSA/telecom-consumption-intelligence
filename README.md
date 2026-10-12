# 📶 Telecom Consumption Intelligence

**Forecast tomorrow's mobile data demand. Identify commercial opportunities. Make better network and customer decisions.**

[**🚀 Live Dashboard **](https://telecom-consumption-intelligence-7u9fclgabrv8tttvf2jpsx.streamlit.app/)

Telecom Consumption Intelligence is a business analytics and forecasting solution designed around the daily decisions facing South African telecom operators: network capacity planning, data bundle opportunities, customer engagement, and revenue protection.

It predicts next-day mobile data consumption at subscriber level and translates forecasts into business insights through an interactive management dashboard.

The objective is not simply to predict data usage. It is to help teams understand **where demand is heading, which customers may need attention, and where commercial opportunities may exist.**

> **Important:** This portfolio project uses synthetic data simulating South African telecom subscriber behaviour. The findings and financial estimates demonstrate an analytical approach; they are not actual operator results or realised financial returns.

---

## 💼 The Business Challenge

Telecom operators must balance three competing priorities:

- **Network performance:** Make capacity available where demand is expected, without unnecessarily over-allocating resources.
- **Revenue growth:** Identify subscribers whose consumption patterns may create opportunities for relevant top-ups and data bundles.
- **Customer retention:** Detect sustained changes in usage that may warrant customer engagement before dissatisfaction or disengagement develops.

Historical reporting helps explain what has already happened. Forecasting adds another perspective: what may happen tomorrow, and what should the business investigate today?

This project brings these questions together in one decision-support dashboard.

## 📊 What the Solution Delivers

| Business Question | How the Solution Helps |
|---|---|
| Where might demand increase tomorrow? | Forecasts subscriber usage and aggregates demand by region, plan and network. |
| Where could additional data revenue exist? | Identifies subscribers whose actual usage exceeds predicted usage and estimates potential top-up opportunities. |
| Which customers may need attention? | Highlights sustained usage changes and existing churn-risk indicators for further investigation. |
| Which regions or customer segments differ? | Compares usage, revenue and other business measures across customer groups. |
| Can management trust the results? | Monitors forecast errors, examines model drivers and validates uploaded data before scoring. |

The dashboard includes Overview, Tomorrow's Forecast, Revenue Analysis, Geography, Customer Insights, Compare Data, Model Monitoring and Data Checks.

---

## 📈 Key Results

The forecasting model was evaluated on a held-out test dataset that was not used to train the model.

| Performance Metric | Test Result | Business Interpretation |
|---|---:|---|
| R² | 0.770 | Explains approximately 77% of the variation in next-day usage in the test data. |
| Mean Absolute Error (MAE) | 2.02 GB | Average absolute prediction error per subscriber per day. |
| Root Mean Squared Error (RMSE) | 3.38 GB | Measures prediction error while penalising larger errors more heavily. |
| Training-to-validation R² gap | 0.012 | Indicates a relatively small observed gap between training and validation performance. |

**What this means for the business**

The model captures a substantial portion of variation in next-day subscriber usage, with an average absolute prediction error of approximately 2 GB per subscriber per day.

This makes it a useful basis for exploring demand patterns and prioritising further analysis. It does not mean that 77% of individual predictions are correct, nor does it establish production readiness.

---

## 💰 Business Findings and Implications

### 1. Customer usage patterns are more informative than a single day's activity

The strongest predictive signal was the subscriber's 30-day average data consumption, followed by the 7-day average.

| Signal | Correlation with Next-Day Usage |
|---|---:|
| 30-day rolling average | 0.866 |
| 7-day rolling average | 0.854 |
| Previous day's usage | 0.758 |

*These are correlations with the target, not percentages of model importance or proof of causation.*

**Business implication:** Recent usage history provides a valuable baseline for understanding expected demand. Network and commercial teams can investigate persistent changes against that baseline rather than relying on an unusually high or low day.

### 2. Forecast reliability is slightly weaker during congestion

| Test Condition | Records | R² | Mean Absolute Error |
|---|---:|---:|---:|
| Normal conditions | 74,783 | 0.7711 | 2.016 GB |
| Congested conditions | 19,420 | 0.7646 | 2.039 GB |

Forecast performance is modestly weaker during congested conditions, with a slightly higher average error.

**Business implication:** Capacity planners should examine forecast performance alongside congestion indicators. Before adjusting capacity allocations, the operator would need to establish whether forecast errors systematically overestimate or underestimate demand and whether that pattern persists in real network data.

### 3. Forecast errors reveal potential commercial opportunities

On the synthetic test dataset, the analysis identified:

| Measure | Result |
|---|---:|
| Under-predicted records | 54,539 (57.9%) |
| Estimated top-up opportunity | R7,344,112 |
| Over-predicted records | 39,664 (42.1%) |
| Estimated over-allocation cost | R7,122,874 |

Under-prediction means actual usage exceeded the forecast; over-prediction means actual usage fell below it.

**Business implication:** Persistent under-prediction could help identify customers for relevant top-up offers. Persistent over-prediction could help identify declining consumption or allocations that merit review.

These figures are model-based estimates derived from synthetic records and financial assumptions. They are not verified incremental revenue, cash savings, or proof that every flagged customer represents an actionable opportunity. Commercial testing and cost validation would be necessary.

### 4. Customer segments may need different commercial strategies

The simulated dataset exhibits differences in consumption across plan, device and geographic segments.

**Business implication:** Segment-level analysis can help teams investigate whether different data bundles, pricing structures or engagement strategies are appropriate for different subscriber groups.

The relationships observed in synthetic data should be validated against actual customer behaviour before informing pricing or marketing decisions.

---

## 🎯 Recommended Business Actions

| Business Function | Proposed Action | Intended Outcome |
|---|---|---|
| Network operations | Review demand forecasts alongside congestion and capacity indicators. | Better-informed capacity planning. |
| Commercial and product | Test targeted top-up offers for subscribers with persistent under-prediction. | Measure incremental top-up conversion and revenue. |
| Customer retention | Investigate sustained consumption declines and relevant churn-risk indicators. | Identify customers who may benefit from engagement. |
| Product management | Compare usage by plan, device and region. | Inform segment-specific bundle design. |
| Data science | Monitor forecast error and data drift; retrain when justified by evidence. | Maintain reliable forecasting performance. |

The dashboard's Business Actions translate calculated measures into suggested next steps. These are recommendations for human review, not automated customer decisions.

Any operational thresholds, offer eligibility rules or retraining schedules should be validated against real business costs, customer outcomes and model performance.

---

## 🖥️ Explore the Dashboard

**[🚀 Open the Live Dashboard](https://telecom-consumption-intelligence-7u9fclgabrv8tttvf2jpsx.streamlit.app/)**

The dashboard is designed for managers and analysts who need to move from metrics to decisions.

| Dashboard Page | Business Purpose |
|---|---|
| Overview | Understand subscriber activity, usage, billing, churn indicators and forecast highlights. |
| Tomorrow's Forecast | Explore expected demand by region, plan and network. |
| Revenue Analysis | Examine revenue patterns and estimated commercial opportunities. |
| Geography | Compare regions across selected business measures. |
| Customer Insights | Explore customer segments and investigate individual subscriber records. |
| Compare Data | Compare periods or datasets to understand what has changed. |
| Model Monitoring | Assess forecast reliability, error patterns and model drivers. |
| Data Checks | Identify data-quality issues before forecasts are produced. |

Additional capabilities include PDF and Excel report exports, data uploads, configurable business assumptions and an interactive data viewer. Uploaded datasets are checked before they can replace the active dataset used by the dashboard.

---

## ⚙️ How It Works

The solution follows a straightforward forecasting workflow:

1. **Understand historical behaviour:** Analyse subscriber usage, customer profiles, plans and network conditions.
2. **Build a forecast:** Use past usage patterns and other available information to predict each subscriber's next-day consumption.
3. **Evaluate reliability:** Test the model on a separate, later time period and examine errors across different conditions.
4. **Translate forecasts into business measures:** Aggregate demand, compare actual usage against predictions and estimate opportunities using explicit assumptions.
5. **Support decisions:** Present the results through interactive charts, customer insights, data checks and management reports.

The dashboard also supports comparisons between datasets, explanations of model behaviour and validation of new data before scoring.

---

## 🧰 Technical Overview

The project combines a Python forecasting pipeline with a modular Streamlit business dashboard.

| Component | Implementation |
|---|---|
| Forecasting task | Next-day subscriber-level regression |
| Model | HistGradientBoostingRegressor |
| Machine learning | scikit-learn 1.6.1 |
| Data processing | Python, pandas and NumPy |
| Business dashboard | Streamlit |
| Explainability | Feature importance and optional SHAP analysis |
| Reporting | PDF and Excel exports |
| Quality assurance | Data validation and automated tests |

### Model Evaluation

| Dataset | Rows | R² | MAE |
|---|---:|---:|---:|
| Training | 531,140 | 0.7748 | 1.971 GB |
| Validation | 95,019 | 0.7626 | 2.025 GB |
| Test | 94,203 | 0.7698 | 2.021 GB |

The split is time-based to better reflect forecasting future usage from past observations. The small training-to-validation performance gap is encouraging, although broader testing is needed to establish reliability across different periods and operating conditions.

---

## ⚠️ Data, Assumptions and Limitations

This is a portfolio demonstration, not a production deployment for a real telecom operator.

- **Synthetic data:** Subscriber activity and business results are generated, not obtained from Vodacom, MTN, Telkom, Cell C, Rain or another operator.
- **Limited time horizon:** The simulated history covers approximately 90 days and does not establish annual seasonal patterns.
- **Simplified congestion:** Congestion is represented as a binary indicator rather than a detailed measure of network conditions.
- **Missing external factors:** Holidays, promotions, service disruptions, device launches and other external drivers are not fully represented.
- **Estimated financial value:** Revenue opportunities and allocation costs depend on assumptions and require validation using real operator economics.
- **Forecast uncertainty:** Individual predictions can differ materially from actual usage, and performance can vary by segment and network condition.
- **Retention interpretation:** Changes in usage may warrant investigation but do not, on their own, establish that a customer will churn.

These limitations define the next steps needed to evaluate the solution in a real operating environment.

---

## 🚀 Next Steps

If extended with an operator or research partner, the project could progress through:

1. **Real-world validation:** Evaluate forecast performance against historical operator data.
2. **Financial validation:** Calibrate top-up conversion, contribution margins and capacity costs using actual business assumptions.
3. **Network-aware forecasting:** Test whether more detailed congestion and capacity signals improve demand estimates.
4. **Customer outcome testing:** Measure whether forecast-led offers improve incremental revenue, retention or customer experience.
5. **Operational monitoring:** Establish data-quality gates, drift monitoring and evidence-based retraining triggers.
6. **Production integration:** Connect validated forecasts to existing planning and analytics workflows with appropriate human oversight.

---

## 📚 Technical Appendix

### Forecast Design and Leakage Prevention

The target is the subscriber's total data consumption on the following day. Features are designed to use information available before the forecast day.

Key controls include:

- Creating the next-day target using a per-subscriber shift.
- Constructing lag and rolling-window features from historical usage.
- Using a time-based evaluation split instead of randomly shuffling observations.
- Avoiding future-value backfilling in early-history fallbacks.
- Dropping records with missing required values where appropriate.

These controls reduce the risk of data leakage, but do not eliminate the need for further validation of feature availability and the full scoring pipeline.

### Feature Engineering

The model uses historical usage patterns, including daily lags and rolling averages, alongside available customer, plan, device, network, calendar and billing information.

Feature correlations help describe the data, while model importance and SHAP analysis can provide additional information about how the fitted model uses those features. Neither should automatically be interpreted as causal business drivers.

### Project Structure

```text
telecom-consumption-intelligence/
├── training/       # Data preparation and model training
├── models/         # Saved model and metadata
├── modular/        # Streamlit business dashboard
│   ├── app.py
│   ├── views/      # Dashboard pages
│   ├── src/        # Analytics, scoring, checks and reports
│   ├── assets/     # Default data and reference profiles
│   ├── scripts/    # Data and profile generation
│   └── tests/      # Dashboard and data-quality tests
├── notebooks/      # Exploratory analysis and business insights
├── reports/        # Analysis outputs
├── docs/           # Deployment and report documentation
├── requirements.txt
└── README.md
```

### Run Locally

From the repository root:

```bash
pip install -r modular/requirements.txt
streamlit run modular/app.py
```

Use the repository's root `requirements.txt` as well if your development or training workflow requires additional dependencies.

For deployment guidance, see [`docs/DEPLOY.md`](docs/DEPLOY.md).

---

**Project Focus:** Applied data science, demand forecasting, commercial analytics and decision support.

The central question behind this project is simple:

**How can a forecast become a useful business decision rather than just another model metric?**
