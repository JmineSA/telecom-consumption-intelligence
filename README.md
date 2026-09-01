# 📶 Mobile Data Consumption Intelligence System

**Client:** SA Telecom Analytics *(Simulated Engagement)*  
**Project Type:** Data Science & Business Analytics Portfolio Project  
**Focus:** Predictive Analytics, Revenue Optimisation & Network Intelligence  
**Status:** Completed  
**Date:** July 2026

---

## 🎯 Executive Summary

Telecom providers need better visibility into customer data consumption, network conditions and subscription behaviour to optimise network capacity, improve customer targeting and identify revenue opportunities.

This project delivers an end-to-end **Telecom Consumption Intelligence System** that analyses customer usage patterns and predicts mobile data consumption to support business decision-making.

The analysis covers **20,002 records across 20,001 users** over a 30-day period and combines customer behaviour, device type, network conditions and subscription plans to generate actionable insights.

### Key Outcomes

- Identified **595 peak-hour users**, representing **29.7% of analysed users**.
- Found that network congestion increased prediction error by approximately **255.7%**, highlighting an opportunity for congestion-aware forecasting and network capacity planning.
- Identified **Gaming** as the most revenue-efficient service among high-intensity users.
- Identified **Postpaid Unlimited** as the highest estimated-profitability plan.
- Segmented customers and identified **573 high-value Revenue Drivers** for targeted retention and personalised offers.
- Identified approximately **R32.8K in potential revenue opportunities** associated with under-predicted usage.
- Identified approximately **R44.9K in potential network over-allocation costs** associated with over-predicted usage.

The project translates predictive analytics into practical recommendations for **bundle optimisation, targeted upselling, customer retention, network capacity planning and revenue optimisation**.

---

## 📊 Business Overview

| Metric | Result |
|---|---:|
| Total Records | 20,002 |
| Unique Users | 20,001 |
| Analysis Period | 19 March 2026 – 17 April 2026 |
| Average Data Usage per Hour | 0.65 GB |
| Average ARPU per GB | R123.32 |
| Peak Hour Users | 595 |
| Peak Hour User Share | 29.7% |

---

## 💡 Key Business Insights

### 1. Network Congestion Impact

Network congestion had a significant impact on prediction accuracy.

| Network Condition | Average Data Usage | Average Prediction Error | Users |
|---|---:|---:|---:|
| Normal | 2.73 GB | 0.37 GB | 1,823 |
| Congested | 9.83 GB | 1.32 GB | 179 |

Prediction error during congestion was approximately **255.7% higher** than during normal network conditions.

**Business opportunity:**

- Improve congestion-aware forecasting.
- Optimise network capacity during high-demand periods.
- Include congestion indicators in predictive models.
- Improve network resource allocation using prediction confidence.

---

### 2. Service Revenue Efficiency

Revenue efficiency was analysed across high-intensity users.

| Service | Average ARPU | Average Data Usage | ARPU per GB |
|---|---:|---:|---:|
| Gaming | R358.50 | 4.68 GB | R76.57 |
| Messaging | R375.46 | 4.95 GB | R75.80 |
| Social | R396.35 | 5.23 GB | R75.74 |
| Streaming | R529.39 | 7.34 GB | R72.12 |

**Gaming** demonstrated the highest revenue efficiency, while **Streaming** showed the lowest.

**Business opportunity:**

- Develop gaming-focused data bundles.
- Create personalised offers based on service usage.
- Review streaming bundle pricing and margins.

---

### 3. Customer Segment Profitability

Customers were segmented based on their revenue and consumption behaviour.

| Customer Segment | Average ARPU | Average Data Usage | Users |
|---|---:|---:|---:|
| Regular User | R191.64 | 1.85 GB | 890 |
| Revenue Driver | R595.95 | 8.41 GB | 573 |
| Upsell Opportunity | R77.56 | 0.50 GB | 539 |

The analysis identified **573 high-value Revenue Drivers** with the highest average ARPU and data consumption.

**Business opportunity:**

- Target Revenue Drivers with retention and loyalty campaigns.
- Offer personalised premium bundles.
- Target Upsell Opportunities with tailored offers to increase engagement and ARPU.

---

### 4. Subscription Plan Performance

| Plan Type | Average ARPU | Average Data Usage | Estimated Profitability |
|---|---:|---:|---:|
| Postpaid Unlimited | R412.21 | 5.73 GB | R397.89 |
| Postpaid Premium | R381.09 | 5.25 GB | R367.95 |
| Postpaid Basic | R256.90 | 2.86 GB | R249.75 |
| Prepaid Daily | R202.99 | 1.73 GB | R198.66 |
| Prepaid Monthly | R183.92 | 2.07 GB | R178.74 |

Estimated profitability was calculated using an assumed network cost of **R2.50 per GB**.

**Key finding:** **Postpaid Unlimited** generated the highest estimated profitability, while **Prepaid Monthly** generated the lowest.

**Business opportunity:**

- Target high-usage customers for Postpaid Unlimited upgrades.
- Review the pricing and value proposition of Prepaid Monthly.
- Develop personalised migration campaigns between prepaid and postpaid plans.

---

### 5. Device and Network Impact

Device capability and network technology showed a relationship with customer consumption and revenue.

Examples:

- **5G devices on 5G networks** averaged **8.26 GB** of usage and **R583.65 ARPU**.
- **Premium smartphones on 5G networks** averaged **8.10 GB** of usage and **R554.74 ARPU**.
- Basic phone users generally demonstrated lower data consumption and ARPU.

**Business opportunity:**

- Target eligible customers with device upgrade campaigns.
- Support 4G-to-5G migration strategies.
- Personalise offers based on device and network capability.

---

## 📉 Prediction Error and Business Impact

### Under-Predicted Usage

**951 records (47.5%)** used more data than predicted.

This identified approximately:

> **R32,820.42 in potential revenue opportunities**

Potential actions include:

- Real-time usage alerts.
- Personalised top-up recommendations.
- Dynamic bundle offers.
- Usage-based upselling.

### Over-Predicted Usage

**1,051 records (52.5%)** used less data than predicted.

This identified approximately:

> **R44,853.97 in potential network over-allocation costs**

Potential actions include:

- Improve demand forecasting.
- Adjust network resource allocation.
- Monitor high-variance customer segments.

> **Note:** Revenue opportunity and cost estimates are based on assumptions within this simulated analysis and should be validated using real operational pricing and network cost data.

---

## 🧠 Methodology

### 1. Data Preparation

- Data cleaning and validation.
- Feature selection.
- Identification and removal of potential data leakage.
- Training and validation data splitting.
- Pipeline-based preprocessing.

### 2. Feature Engineering

Features included:

- Streaming activity.
- Social media usage.
- Messaging activity.
- Gaming activity.
- Subscription plan type.
- Device type.
- Network type.
- Age group.
- Date-based features.
- Peak usage indicators.
- Customer usage segments.

### 3. Predictive Modelling

The modelling workflow included:

- Train-validation splitting.
- Pipeline-based preprocessing.
- Categorical feature encoding.
- Feature engineering.
- Model comparison.
- Hyperparameter tuning.
- Final model selection.

### 4. Business Translation

Model outputs and analytical findings were translated into recommendations for:

- Revenue optimisation.
- Bundle design.
- Customer segmentation.
- Targeted upselling.
- Network capacity planning.
- Congestion management.

---

## 📈 Model Performance

The final model achieved the following results:

| Metric | Final Model |
|---|---:|
| MAE | **0.457 GB** |
| RMSE | **0.922 GB** |
| R² Score | **0.956** |
| MAPE | **16.3%** |

While the model demonstrated strong overall predictive performance, further analysis showed that prediction accuracy varied significantly across network conditions, particularly during congestion.

---

## 💼 Strategic Recommendations

### 🎮 Optimise Service Bundles

Develop targeted gaming and high-engagement service bundles while reviewing streaming pricing and margins.

### 🌐 Implement Congestion-Aware Forecasting

Use congestion indicators and prediction confidence to improve network planning and resource allocation during high-demand periods.

### 💰 Retain High-Value Revenue Drivers

Target the **573 identified Revenue Drivers** with personalised retention offers, loyalty benefits and premium bundles.

### 📱 Optimise Subscription Plans

Promote Postpaid Unlimited to high-usage customers and review the pricing and bundle structure of Prepaid Monthly.

### 📊 Improve Forecasting for High-Demand Conditions

Develop additional features related to network congestion and customer behaviour to improve forecasting during peak and congested periods.

---

## 📂 Project Deliverables

| Deliverable | Description |
|---|---|
| Business Analysis | Customer usage, ARPU, service and plan performance analysis |
| Predictive Model | Mobile data consumption forecasting model |
| Customer Segmentation | Identification of Revenue Drivers, Regular Users and Upsell Opportunities |
| Network Analysis | Peak-hour and congestion analysis |
| Business Recommendations | Revenue, pricing, bundling and network optimisation strategies |
| Dashboard | Interactive visualisation of telecom performance and insights |
| Data Pipeline | Reusable preprocessing and feature engineering workflow |
| Model Artifacts | Saved preprocessing pipeline and trained model |

---

## 🧰 Tech Stack

**Programming & Analysis**

Python · Pandas · NumPy · SQL

**Machine Learning**

Scikit-learn · Gradient Boosting · Random Forest

**Visualisation**

Matplotlib · Seaborn · Plotly

**Application**

Streamlit · Joblib

---

## 📁 Project Structure

```text
telecom-consumption-intelligence/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── models/
│   ├── preprocessing_pipeline.pkl
│   └── model artifacts
│
├── notebooks/
│
├── reports/
│   ├── telecom_user_segments.csv
│   ├── telecom_network_insights.csv
│   └── telecom_service_profitability.csv
│
├── src/
│   ├── data preparation
│   ├── feature engineering
│   ├── preprocessing
│   ├── model training
│   └── business analysis
│
├── visuals/
│
├── requirements.txt
└── README.md