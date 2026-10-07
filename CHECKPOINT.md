# CHECKPOINT — Telecom Consumption Intelligence

## Latest — 2026-10-07 (feature/data-v2 merged to main)

### Where We Are
- **Branch:** `main` — has the new time-series D+1 model
- **Status:** Merge complete, README rewritten, ready for app migration
- **Model:** HistGradientBoostingRegressor, test R² ≈ 0.77

### Working State (main branch, post-merge)
- **Data generator:** 10,000 users × 90 days = 817,568 rows
  - ZAR pricing: `monthly_bill_zar` R50 – R1,800
  - 3% MCAR missing, 1% duplicates injected for realism
- **Data preparation:** time-based split, drop-not-impute policy
  - Train: ~531,140 | Val: ~95,019 | Test: ~94,203
  - Train dates: 2026-01-02 → 2026-03-03
  - Val dates:   2026-03-04 → 2026-03-16
  - Test dates:  2026-03-17 → 2026-03-30
- **Model:**
  - Target: `target_next_day_gb` (D+1 forecast)
  - Train R² = 0.7748
  - Val R²   = 0.7626
  - Test R²  = 0.7698
  - Test MAE = 2.021 GB
  - Overfit gap = 0.0122 (healthy)

### Leakage Prevention (verified)
- Target built via `shift(-1)` per user
- All lag features past-only (`shift(1)` + rolling windows)
- Early-day fallbacks use `lag_1d_total_gb` (no bfill from future)
- Missing values dropped (~3% MCAR), not imputed
- Time-based split, no shuffle

### Completed Yesterday's Plan ✅
- [x] Confirmed `monthly_bill_zar` in `model_info.json` feature_names
- [x] Ran `training.evaluation.evaluate_model`
- [x] Regenerated `model_insights.py` outputs on ZAR model
- [x] Committed + pushed feature/data-v2
- [x] Merged feature/data-v2 into main (11 conflicts resolved)
- [x] Deleted `modular/logs/app.log` from tracking

### Merge Notes
Resolved conflicts in favor of `feature/data-v2` for:
- `models/mobile_data_consumption_pipeline.pkl` (new ZAR model)
- `models/model_info.json` (new metadata)
- All 8 `training/*` files (ZAR pricing, drop-NA, past-only lags)
Deleted `modular/logs/app.log` — should never have been tracked.

### Known Follow-Ups
- [ ] `.gitignore` — add `*.log`, `modular/logs/`, `data/processed/*.parquet`,
      `data/raw/*.parquet`, `*.pkl`
- [ ] Remove large tracked files (e.g. `modelling_dataset.parquet`, 53 MB —
      GitHub warned about size)
- [ ] Rewrite README (in progress — business-first structure)
- [ ] Update LinkedIn post with new numbers

---

## NEXT: App Migration

The Streamlit app on `main` currently loads the **legacy model** (the old
cross-sectional one). It needs to be migrated to the new D+1 forecasting model.

### App Files That Need Updating
- `modular/src/constants.py` — `EXPECTED_FEATURES` (13 → ~25 features)
- `modular/src/data/loader.py` — read `train.parquet` (not `train_data.parquet`)
- `modular/src/data/processor.py` — new feature preparation
- `modular/src/ui/sidebar.py` — new input form (with `measurement_date`,
  string categoricals, lag features)
- `modular/src/models/manager.py` — verify prediction schema
- `modular/src/ui/tabs.py` — display updates (new target, new metrics)
- `modular/src/analytics/*` — update if referencing old columns

### Migration Order
1. **Data layer** — `constants.py`, `loader.py`, `processor.py`
2. **Prediction** — `manager.py`, `sidebar.py`
3. **Display** — `tabs.py`, `analytics/*`
4. **Verify locally** — run app, check prediction renders
5. **Deploy** — reboot Streamlit Cloud

### Migration Risks
- App currently built for cross-sectional input (13 features)
- New model needs lag features that can't be entered via a form
- **Decision needed:** how does the app handle lag features for a
  hypothetical user? Options:
  - A) Use recent real data from `train.parquet` (pick a user, load their last 30 days)
  - B) Simulate lags from simple inputs (e.g., user enters "recent usage")
  - C) Restrict the app to segment-level forecasts (aggregate)

**Recommendation:** Option A — user picks a real subscriber from the test
set, the app pulls their actual lag features and forecasts tomorrow.

---

## Rollback Points

- **Pre-merge main:** `git checkout main && git reset --hard 527a603`
- **feature/data-v2 preserved:** still exists, pushable
- **Working model:** `models/mobile_data_consumption_pipeline.pkl` (current
  commit) — the ZAR model, safe to reload

---

## Session Log

### 2026-10-06
- Rebuilt `data_generator.py` with ZAR pricing
- Renamed `monthly_bill_usd` → `monthly_bill_zar`
- Fixed `data_preparation.py`: drop NaN, no imputation, past-only lags
- Retrained model (HistGradientBoosting)
- Added permutation importance to `model_insights.py`

### 2026-10-07
- Merged `feature/data-v2` → `main` (11 conflicts resolved)
- Rewrote README (business-first structure)
- Ready to start app migration