# SA Telecom Analytics: Telecom Consumption Intelligence

A manager-facing dashboard built on a next-day mobile data forecasting model
(HistGradientBoostingRegressor, scikit-learn 1.6.1). The data is synthetic.

It answers three daily questions: how much data will customers use tomorrow, who is about to use more than
expected (top-up offers), and who is quietly using less (retention).

<!--
Add screenshots to docs/screenshots/ and uncomment:
![Overview](docs/screenshots/overview.png)
![Forecast](docs/screenshots/forecast.png)
![Revenue](docs/screenshots/revenue.png)
-->

## Where this folder goes

Put this `modular/` folder inside your project, next to `training/` and `models/`. It uses them and does not copy them.

    telecom-consumption-intelligence/
    ├── training/            your ML pipeline (the saved model needs it to load)
    ├── models/              mobile_data_consumption_pipeline.pkl, model_info.json (the app reads them from here)
    ├── modular/             this app
    │   ├── app.py           start here
    │   ├── views/           one file per page
    │   ├── src/             data loading, checks, scoring, KPIs, charts, reports
    │   ├── assets/          default_sample.parquet, reference_profile.json (+ fallback copies of the model metadata)
    │   ├── scripts/         rebuild the default data, the reference profile, the test datasets
    │   ├── tests/           python -m pytest modular/tests
    │   └── .streamlit/      theme and upload limit
    └── requirements.txt     add the lines from modular/requirements.txt that are missing

Run it from the project folder or from `modular/`, both work:

    streamlit run modular/app.py          # from the project folder
    cd modular && streamlit run app.py    # from inside modular/

If a file is missing the app says which one and where it looked. If your project folder is elsewhere, set the
`TELECOM_PROJECT_ROOT` environment variable to it.

A sample of the exported report is in `docs/sample_full_report.pdf` and `docs/sample_full_report.xlsx`.

## Pages

| Page | What it shows |
|---|---|
| Overview | Customers, usage, bill, churn risk, next-day forecast, what needs attention, and Business Actions |
| Tomorrow's Forecast | Demand and capacity by region, plan, and network, plus top-up targets |
| Revenue Analysis | Revenue, top-up opportunity, revenue at risk, what each plan earns, and Business Actions |
| Geography | Regions compared on any metric |
| Customer Insights | Segments, customers to contact, and a single-customer lookup |
| Compare Data | Two periods of the loaded data, or the loaded data against another file: what changed, whether it is good or bad, by group |
| Model Monitoring | Accuracy, error over time, drivers, and a retrain button |
| Data Checks | Is this dataset valid and safe to use for scoring? Checks by group, what each problem means for the model, and a final READY / NOT READY status |
| About | The business problem, model facts, and limits |

**Business Actions** turn the numbers into suggested next steps: top-up opportunity, lower-than-expected usage,
capacity review, and forecast reliability. They use only measures the dashboard already calculates and the
sidebar's Business assumptions. A card appears only when the data supports it. They are decision support, not
automated decisions.

Every page can be downloaded as a PDF and Excel report. Uploading a new file in the sidebar recalculates
every number and chart. "Reset to default data" brings the original back.

## Data Checks

Every upload passes through the checks before anything is scored: file, columns, data types, missing values,
duplicates, impossible values and outliers, how the data compares with the model's training data, and scoring
readiness. Each check is **Passed**, **Warning** (scoring continues, review advised) or **Critical** (scoring is
blocked and the previous data stays on screen). Every warning or critical result says what it means for the
business and the model, and what to do. The page ends with **Dataset Status: READY FOR SCORING** or
**NOT READY FOR SCORING**. Thresholds are listed on the page and in `src/quality.py`.

The comparison with training data uses `models/reference_profile.json`. Rebuild it from the full training file:

    python modular/scripts/make_reference_profile.py --input data/processed/train.parquet

## KPI cards

All KPI cards come from one function, `theme.kpi(col, label, value, sub, tone, accent)`. Each has a 4px left accent:
teal (neutral), green (ok), amber (watch) or red (risk). Red is used only for real risk measures: customers at
churn risk, revenue at risk, a customer's churn probability at or above the threshold, critical data checks, and
model health "Action needed". Cards fade in and rise 12px, 70 ms apart, the first time they appear after entering
a page, and do not replay on filter, slider or upload changes. Reduced-motion settings turn this off.

## Data viewer

On the Data Checks page, **View data** opens a table of the loaded data: a sample (50 rows by default, random, earliest or
latest dates) or the full dataset. Sort by clicking a heading, edit cells, delete or add rows (tables up to 50,000 rows;
larger ones are read-only). Tabs let you add a calculated column (column ÷ column or number, and so on), keep only rows that
match a condition, summarise by group, and download CSV or Excel. **Check and use this data** sends the full edited table
through the same Data Checks as an upload, so a bad edit cannot reach the dashboard. Edits are per session and are not saved
on the server. Nothing typed in is run as code (`src/viewer.py`).

## Test datasets

`python modular/scripts/make_test_datasets.py` creates 28 synthetic files in `modular/test_data/` (clean, dirty, blocked, drift, noisy, compare,
large, edge cases) and a `README.md` saying what each file tests and what the dashboard should show. The expected results in
that README come from running every file through the app's own checks, so they stay honest. `tests/test_testdata.py` checks them.

## Compare Data, the tour, and reports

**Compare Data** compares two periods (presets or your own dates) or the loaded data against a second file. The second file goes
through the Data Checks first and never replaces the loaded data. Each measure gets a plain verdict: more revenue is good,
more customers at churn risk is not, usage and forecast changes are shown without one.
**How to read this dashboard** (sidebar button, and a section on About) is an eight-step guide for new managers.
The Model Monitoring report includes feature importance and SHAP when they were calculated before the report was prepared.

## Explaining the model

Model Monitoring has a switch: **Feature importance**, **SHAP values**, or **Both**. Importance shows which features the
model relies on (error grows when one is shuffled). SHAP shows, in GB, how much each feature pushes forecasts up or down.
It gives a plain-language summary, a table of how each feature pushes the forecast, and a "why this forecast" chart and
sentence for any record in a 300-row sample. SHAP runs only when you click, takes about 15 seconds, and uses the `shap`
package. It explains the model; it does not change any forecast.

## Navigation and hover effects

The sidebar groups pages under Business and Model and data; the active page has a tinted background and an accent
bar, and hovering tints the item and nudges it 2px. Cards share one hover language: KPI cards lift 4px with a
deeper shadow and an accent border, recommendation cards lift 2px, and panels, charts and tables only gain a
border and soft shadow. Effects apply only on devices that can hover, never move layout, and turn off when the
device asks for reduced motion. All styles live in `src/theme.py`; colours and shadows in `src/palette.py`.

## Appearance

System (default, follows the device), Light, or Dark. Open the three-dot menu at the top right and choose one.
Colours are set in `.streamlit/config.toml` and `src/palette.py`. Exported PDF reports are always light.

## Run it

    pip install -r modular/requirements.txt
    streamlit run modular/app.py

## Upload format

CSV or Parquet. Required columns: user_id, date, streaming_gb, social_gb, messaging_gb, gaming_gb,
background_gb, total_gb, arpu, congested, plan_type, device_type, network_type, age_group, region,
contract_duration_months, customer_tenure_months, monthly_bill_zar, support_calls_6months,
churn_probability, churn_status.

Lag and rolling columns are used if present and built from daily usage if not. Built features need consecutive
daily rows per customer. Uploads are limited to 1,000,000 rows (`MAX_UPLOAD_ROWS`).

## Deploy

See `docs/DEPLOY.md`.

## Limits

Synthetic data. A 90-day window. Congestion is a yes or no flag. No holidays or promotions. The model uses
the days before the current day, not the current day itself. Top-up price and take-up rate are assumptions.
