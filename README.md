# 📶 Mobile Data Consumption Intelligence System

**Client:** SA Telecom Analytics (Simulated Engagement)  
**Role:** Data Science Consultant  
**Status:** ✅ Delivered  
**Date:** April 2026

---

## 🎯 Executive Summary

SA Telecom faces unpredictable network load and suboptimal bundle pricing due to limited visibility into consumption drivers. This engagement delivered a predictive intelligence system that:

- **Predicts** daily data usage within **0.35 GB** (MAE)
- **Identifies** key consumption drivers (YouTube, TikTok, Student segment)
- **Quantifies** a **15-20% ARPU opportunity** through targeted bundling
- **Segments** 10,000+ users for personalized offerings

---

## 📊 Key Business Findings

| Insight | Business Implication |
|---------|---------------------|
| Video drives 62% of all data consumption | Video-optimized bundles = highest ROI |
| Students consume 43% more than employed users | Student acquisition is strategic priority |
| Township night usage 2.3x higher than Urban | "Night Owl" bundles for Township areas |
| 5G users consume 38% more than 4G users | 5G upgrades directly increase revenue |

---

## 🧠 Methodology

1. **Data Engineering:** 10,000 user profiles reflecting SA demographics
2. **Feature Engineering:** 20+ behavioral features from app usage patterns
3. **Model Development:** 4 regression approaches evaluated
4. **Insights Delivery:** Actionable recommendations from model outputs

---

## 📈 Model Performance

| Metric | Baseline | Final Model | Improvement |
|--------|----------|-------------|-------------|
| MAE (GB) | 0.82 | **0.35** | 57% |
| RMSE (GB) | 1.21 | **0.51** | 58% |
| R² Score | 0.71 | **0.94** | 32% |

✅ **Target Achieved:** MAE ≤ 1.5 GB

---

## 🎯 Strategic Recommendations

### Priority 1: Video-First Bundle
- **Target:** Heavy video consumers (YouTube/TikTok/Netflix)
- **Offer:** 10GB optimized video pass
- **Impact:** +15-20% segment ARPU

### Priority 2: Township Night Owl Expansion
- **Target:** High night-usage Township users
- **Offer:** 20GB (12AM-6AM)
- **Impact:** Monetize off-peak network capacity

### Priority 3: Student Acquisition
- **Target:** Student segment (25% of heavy users)
- **Offer:** 25GB + zero-rated social/video
- **Impact:** +25% segment penetration

---

## 📂 Deliverables

| Deliverable | Link |
|-------------|------|
| Executive Summary | [reports/executive_summary.md](reports/executive_summary.md) |
| Technical Appendix | [reports/technical_appendix.md](reports/technical_appendix.md) |
| Presentation Deck | [reports/presentation_deck.md](reports/presentation_deck.md) |
| Notebook 1: Data Prep | [notebooks/01_data_preparation.ipynb](notebooks/01_data_preparation.ipynb) |
| Notebook 2: Modeling | [notebooks/02_model_development.ipynb](notebooks/02_model_development.ipynb) |
| Notebook 3: Insights | [notebooks/03_insights_delivery.ipynb](notebooks/03_insights_delivery.ipynb) |

---

## 🔧 Technical Stack

`Python 3.9+` · `scikit-learn` · `pandas` · `numpy` · `Random Forest` · `Gradient Boosting` · `Matplotlib` · `Seaborn` · `Streamlit` · `joblib`

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/telecom-consumption-intelligence.git
cd telecom-consumption-intelligence

# Install dependencies
pip install -r requirements.txt

# Run data generation
python src/data_generator.py

# Train model
python src/model_pipeline.py

# Launch dashboard (optional)
streamlit run src/dashboard.py