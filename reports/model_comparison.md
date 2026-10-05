# Model Comparison Report

Generated: 2026-10-05T17:52:25.594181

Train rows: 581,971 | Val rows: 104,192 | Test rows: 103,310

| Rank | Model | Train R² | Val R² | Test R² | Test MAE | Test MAPE | Overfit Gap | Time (s) |
|---|---|---|---|---|---|---|---|---|
| 1 | RandomForest | 0.7744 | 0.7641 | 0.7727 | 2.0075 | 32.40% | 0.0103 | 80.2 |
| 2 | GradientBoosting | 0.7711 | 0.7647 | 0.7722 | 2.0130 | 33.53% | 0.0064 | 927.7 |
| 3 | HistGradientBoosting | 0.7733 | 0.7629 | 0.7701 | 2.0213 | 33.15% | 0.0104 | 10.5 |
| 4 | LightGBM | 0.7818 | 0.7619 | 0.7681 | 2.0276 | 32.93% | 0.0199 | 10.1 |
| 5 | XGBoost | 0.7938 | 0.7610 | 0.7661 | 2.0279 | 32.89% | 0.0328 | 14.9 |
| 6 | Ridge | 0.7497 | 0.7491 | 0.7579 | 2.1279 | 39.50% | 0.0006 | 1.0 |
| 7 | LinearRegression | 0.7497 | 0.7491 | 0.7579 | 2.1280 | 39.50% | 0.0006 | 1.4 |

## Winner: **RandomForest**

- Test R²: 0.7727
- Test MAE: 2.0075 GB
- Overfitting gap: 0.0103
