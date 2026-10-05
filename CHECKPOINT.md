## Model Comparison — 2026-10-05

Benchmarked 7 models on time-based split (582K train / 104K val / 103K test).

| Model | Test R² | Test MAE | Overfit Gap | Train Time |
|---|---|---|---|---|
| RandomForest | 0.7727 | 2.01 GB | 0.010 | 80s |
| GradientBoosting | 0.7722 | 2.01 GB | 0.006 | 928s |
| **HistGradientBoosting** | **0.7701** | **2.02 GB** | **0.010** | **10.5s** ← CHOSEN |
| LightGBM | 0.7681 | 2.03 GB | 0.020 | 10.1s |
| XGBoost | 0.7661 | 2.03 GB | 0.033 | 14.9s |
| Ridge / Linear | 0.7579 | 2.13 GB | 0.001 | ~1s |

**Decision:** HistGradientBoosting over RandomForest.
- R² difference (0.0026) is within noise
- 8× faster training → supports weekly retraining
- 100× smaller artifact → faster deployment
- Natively handles NaN → fewer production bugs

**Interview narrative:** "Model choice driven by engineering trade-offs, not just
metrics. Linear baseline at 0.758 shows lag features carry most of the signal."