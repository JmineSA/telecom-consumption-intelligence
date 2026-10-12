## Modular App Rebuild — 2026-10-07

### What Was Done
Complete rewrite of the Streamlit app for the new D+1 forecasting model.

Old app (deleted):
- 13-tab cross-sectional design
- Expected old data (train_data.parquet, total_data_gb)
- ~25 files, ~200 KB of code
- Never worked with new ZAR schema

New app (built):
- 3-page clean design: Overview / Predict / Insights
- Reads test.parquet + model_info.json (new schema)
- Sidebar radio nav (no clipping)
- Modern "Clean & Corporate" UI (Inter font, navy accents, subtle shadows)
- Predict page works end-to-end (34-feature input)
- Charts loaded from reports/insights/

### Architecture

modular/
├── app.py                      — entry point + router
├── requirements.txt
└── src/
    ├── config.py               — paths + Streamlit config
    ├── constants.py            — EXPECTED_FEATURES + chart list
    ├── data/
    │   └── loader.py           — reads parquet + json
    ├── models/
    │   └── manager.py          — loads pipeline, predicts
    ├── ui/
    │   ├── components.py       — metric_card, insight_card, result_card, etc.
    │   ├── pages.py            — 3 page renderers
    │   └── styling.py          — modern CSS (light + dark)
    └── utils/
        └── logger.py

### Verified Working
- Model loads: HistGradientBoostingRegressor, val R² = 0.7626
- Test data loads: 94,203 rows
- Prediction renders correctly with result card
- Sidebar nav switches pages
- Insights page shows charts

### Branch
feature/modular (up to date with main at time of build)

### Next Steps (When Resuming)
- [ ] Commit + push feature/modular
- [ ] Screenshot Overview + Predict pages for portfolio
- [ ] Update modular/README.md
- [ ] Optional: SHAP explanation on Predict page
- [ ] Merge feature/modular → main when ready
- [ ] Deploy to Streamlit Cloud

### Rollback
- Old modular code is in git history (before this commit)
- `git checkout main -- modular/` restores old version if needed