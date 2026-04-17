# 📶 Mobile Data Consumption Intelligence System

**Client:** SA Telecom Analytics (Simulated Engagement)  
**Role:** Data Science Consultant  
**Engagement Type:** Predictive Analytics & Business Intelligence  
**Status:** Ongoing  
**Date:** April 2026  

---

## 🎯 Executive Summary

SA Telecom lacked visibility into user-level data consumption patterns, limiting its ability to optimize pricing, manage network load, and design targeted bundles.

This project delivered an end-to-end predictive analytics system that:

- Predicts daily mobile data usage with **0.35 GB MAE**
- Identifies primary consumption drivers across user segments
- Quantifies a **15–20% revenue uplift opportunity (ARPU expansion)**
- Segments users for targeted pricing and bundle strategies

---

## 📊 Key Business Insights

| Insight | Business Impact |
|----------|----------------|
| Video streaming accounts for ~62% of total consumption | Prioritize video-centric bundle design |
| Students consume significantly higher data (+43%) | High-value acquisition segment |
| Township users show 2.3x higher night usage | Opportunity for off-peak monetization |
| 5G users consume ~38% more data than 4G users | Strong revenue link to network upgrades |

---

## 🧠 Methodology Overview

### 1. Data Engineering
- Synthetic dataset aligned with South African user behavior patterns
- 10,000 user profiles generated for modeling

### 2. Feature Engineering
- 20+ behavioral and usage-based features
- App-level consumption (YouTube, TikTok, etc.)
- Time-of-day and demographic segmentation

### 3. Model Development
- Multiple regression models evaluated
- Best-performing model selected based on MAE and R²

### 4. Business Translation
- Converted model outputs into pricing and segmentation strategies

---

## 📈 Model Performance

| Metric | Baseline | Final Model | Improvement |
|--------|----------|-------------|-------------|
| MAE (GB) | 0.82 | **0.35** | ↓ 57% |
| RMSE (GB) | 1.21 | **0.51** | ↓ 58% |
| R² Score | 0.71 | **0.94** | ↑ 32% |

**Target:** MAE ≤ 1.5 GB → ✅ Achieved

---

## 💡 Strategic Recommendations

### 1. Video-Optimized Bundles (High Priority)
- Target: High video-consumption users
- Offer: Dedicated video data packages
- Expected impact: **15–20% ARPU uplift**

---

### 2. Township Off-Peak Monetization
- Target: High nighttime usage segments
- Offer: Night-time unlimited/discount bundles
- Benefit: Better utilization of network capacity

---

### 3. Student Segment Strategy
- Target: High-usage student demographic
- Offer: High-data bundles with social/video incentives
- Impact: Increased penetration in growth segment

---

## 📂 Deliverables

| Deliverable | Description |
|-------------|-------------|
| Executive Summary | Business-focused findings and recommendations |
| Technical Report | Full methodology, modeling approach, evaluation |
| Model Artifacts | Trained model + reproducibility files |
| Notebooks | EDA → Modeling → Insights workflow |
| Data Pipeline | Scripts for preprocessing and feature engineering |

---

## 🧰 Tech Stack

Python · Pandas · NumPy · Scikit-learn · Matplotlib · Seaborn · Gradient Boosting · Random Forest · Streamlit · Joblib

---

## 🚀 Reproducibility

```bash
git clone https://github.com/yourusername/telecom-consumption-intelligence.git
cd telecom-consumption-intelligence

pip install -r requirements.txt

python src/data_generator.py
python src/model_pipeline.py

streamlit run src/dashboard.py