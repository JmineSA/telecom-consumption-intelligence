## feature/data-v2 Migration — 2026-10-06 (End of Day)

### Where We Are
Branch: feature/data-v2
Status: Model retrained on new ZAR dataset — NEEDS VERIFICATION TOMORROW

### Working State
- Data generator rebuilt with ZAR pricing
  - 10,000 users × 90 days = 817,568 rows
  - monthly_bill_zar: R50 – R1,800 (realistic SA telecom)
- Data preparation: 789,473 rows across time-based splits
  - Train: 581,971 | Val: 104,192 | Test: 103,310
  - Train dates: 2026-01-02 → 2026-03-03
  - Val dates:   2026-03-04 → 2026-03-16
  - Test dates:  2026-03-17 → 2026-03-30
- Model retrained: 
  - Train R² = 0.7736
  - Val R²   = 0.7628
  - Overfit gap = 0.0108 (small — good)
  - Target: target_next_day_gb (D+1 forecast)

### Unverified (Do First Tomorrow)
- [ ] Confirm 'monthly_bill_zar' in model_info.json feature_names
- [ ] Run python -m training.evaluation.evaluate_model
      (expect test R² ≈ 0.76, congestion breakdown)
- [ ] Regenerate model_insights.py outputs on the new ZAR model
- [ ] Commit + push

### Files Changed Today
- training/core/data_generator.py       (NEW — ZAR version)
- training/core/data_preparation.py     (renamed monthly_bill_usd → monthly_bill_zar)
- training/pipelines/preprocessing_pipeline.py (same)
- models/mobile_data_consumption_pipeline.pkl (retrained)
- models/model_info.json                (new schema)
- training/models/model_insights.py     (permutation importance added)

### Next Session Plan
1. Run the two verification commands from last message
2. If monthly_bill_zar in features → good, commit
3. If not → fix preprocessing_pipeline.py, retrain
4. Run evaluate_model.py
5. Run model_insights.py
6. Commit + push feature/data-v2
7. Plan merge into main + app migration

### Rollback
- Branch: `git checkout feature/data-v2 && git reset --hard HEAD~1`
- To main: `git checkout main` (still working with legacy model)