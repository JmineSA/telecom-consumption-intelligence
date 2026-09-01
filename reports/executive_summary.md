# 📊 Final Report: Mobile Data Consumption Intelligence System

**Client:** SA Telecom Analytics *(Simulated Engagement)*  
**Project Type:** Data Science & Business Analytics Portfolio Project  
**Focus:** Predictive Analytics, Revenue Optimisation & Network Intelligence  
**Date:** July 2026  
**Report Type:** Combined Business + Technical Report  

---

## 1. Executive Overview

This project developed an end-to-end **Telecom Consumption Intelligence System** to analyse customer mobile data consumption, identify behavioural and revenue patterns, predict data usage, and translate analytical findings into actionable business recommendations.

The solution combines:

- Data preparation and feature engineering
- Exploratory data analysis
- Predictive modelling
- Customer segmentation
- Network and congestion analysis
- Revenue and plan profitability analysis
- Business intelligence and dashboard reporting

The analysis covers **20,002 records across 20,001 users** over the period **19 March 2026 to 17 April 2026**.

The resulting insights support business decisions across **revenue optimisation, customer targeting, bundle design, subscription strategy and network capacity planning**.

---

## 2. Business Problem

Telecom providers need visibility into how customers consume mobile data across different services, devices, network conditions and subscription plans.

Without this visibility, organisations may face:

- Inefficient network resource allocation
- Poorly targeted bundles
- Missed upselling opportunities
- Limited visibility into high-value customers
- Difficulty forecasting demand during congested periods
- Inefficient subscription plan strategies

The objective of this project was to use data and predictive analytics to provide a clearer view of **customer consumption, network demand and revenue opportunities**.

---

## 3. Data Overview

### Dataset Summary

| Metric | Result |
|---|---:|
| Total Records | 20,002 |
| Unique Users | 20,001 |
| Analysis Period | 19 March 2026 – 17 April 2026 |
| Data Type | Synthetic telecom data |
| Average Data per Hour | 0.65 GB |
| Average ARPU per GB | R123.32 |
| Peak-Hour Users | 595 |
| Peak-Hour User Share | 29.7% |

### Key Feature Groups

The analysis incorporated features covering:

- Customer behaviour
- Streaming activity
- Social media usage
- Messaging activity
- Gaming activity
- Subscription plan
- Device type
- Network type
- Age group
- Date and time patterns
- Peak-hour indicators
- Customer revenue segments

---

## 4. Methodology

### 4.1 Data Preparation

The data preparation process included:

- Data quality validation
- Handling of missing values where applicable
- Identification and removal of potential target leakage
- Train-validation splitting
- Pipeline-based preprocessing
- Categorical feature encoding

### 4.2 Feature Engineering

Features were engineered to capture:

- Application-level usage behaviour
- Subscription characteristics
- Device and network relationships
- Date-based usage patterns
- Peak-hour activity
- Customer usage segments
- Revenue-related indicators

### 4.3 Modelling Approach

Multiple machine learning approaches were evaluated for mobile data consumption forecasting.

The final workflow included:

1. Training and validation split
2. Preprocessing pipeline
3. Feature encoding
4. Model comparison
5. Hyperparameter tuning
6. Final model evaluation
7. Business-level error analysis

The final model was selected based on predictive performance and its suitability for the telecom consumption forecasting problem.

### 4.4 Business Translation

Model predictions were combined with customer, network and revenue analysis to identify:

- Revenue opportunities
- Network allocation risks
- High-value customer segments
- Bundle optimisation opportunities
- Subscription plan opportunities
- Congestion-related forecasting challenges

---

## 5. Exploratory Data Analysis

### 📊 Usage Distribution

The analysis examined the distribution of customer data consumption to identify normal and high-intensity usage patterns.

**Key observation:** High-consumption customers represent an important revenue segment and require accurate forecasting to support bundle and capacity decisions.

---

### 📊 Service Usage and Revenue

Service-level analysis compared customer consumption and ARPU across gaming, messaging, social and streaming.

**Key observation:** Gaming demonstrated the highest revenue efficiency among high-intensity service users, while streaming generated the highest average ARPU and data consumption.

---

### 📊 Customer Segmentation

Customers were grouped according to their revenue and consumption behaviour.

**Key observation:** The analysis identified **573 Revenue Drivers**, representing customers with high ARPU and high data consumption.

---

### 📊 Network and Peak-Hour Patterns

The analysis evaluated usage and prediction error across network conditions and peak periods.

**Key observation:** **595 users (29.7%)** were identified as peak-hour users, while congestion significantly increased prediction error.

---

## 6. Model Performance

The final model achieved:

| Metric | Final Model |
|---|---:|
| MAE | **0.457 GB** |
| RMSE | **0.922 GB** |
| R² | **0.956** |
| MAPE | **16.3%** |

### Interpretation

**Model accuracy:**  
The model achieved an average absolute prediction error of approximately **0.457 GB**, providing strong overall predictive performance for customer data consumption.

**Generalisation:**  
The evaluation results indicate that the model performs effectively on unseen evaluation data. However, performance varies across customer and network segments.

**Key limitation:**  
Prediction accuracy deteriorates significantly during network congestion, indicating that additional network-condition features could improve operational forecasting.

---

## 7. Key Findings

### Finding 1 — Network Congestion

Prediction error increased from **0.37 GB during normal conditions to 1.32 GB during congestion**.

This represents approximately a **255.7% increase in prediction error**.

**Business implication:** Forecasting should incorporate network congestion and demand indicators to improve network capacity planning.

---

### Finding 2 — High-Value Customers

The analysis identified **573 Revenue Drivers** with:

- Average ARPU of **R595.95**
- Average data consumption of **8.41 GB**

**Business implication:** These customers represent an important target for retention, loyalty programmes and personalised premium bundles.

---

### Finding 3 — Service Profitability

Gaming recorded the highest ARPU efficiency among high-intensity services at approximately **R76.57 per GB**.

Streaming recorded the lowest at approximately **R72.12 per GB**, despite having the highest average ARPU and data consumption.

**Business implication:** Service-level consumption patterns can be used to design more targeted and profitable bundles.

---

### Finding 4 — Subscription Plan Performance

**Postpaid Unlimited** recorded the highest estimated profitability at **R397.89**, while **Prepaid Monthly** recorded the lowest at **R178.74**.

**Business implication:** High-usage customers may represent opportunities for targeted upgrades to higher-value subscription plans.

---

### Finding 5 — Device and Network Value

Customers using advanced devices and faster networks demonstrated substantially higher data consumption and ARPU.

For example, 5G device users on 5G networks averaged:

- **8.26 GB** data usage
- **R583.65 ARPU**

**Business implication:** Device and network characteristics can support targeted 5G migration, upgrade and premium bundle strategies.

---

## 8. Business Impact

### 💰 Revenue Opportunity

Under-predicted usage occurred in **951 records (47.5%)**.

The analysis estimated approximately:

**R32,820.42 in potential revenue opportunities**

Potential actions include:

- Usage alerts
- Personalised top-up recommendations
- Targeted bundle offers
- Usage-based upselling

---

### 💸 Cost Optimisation

Over-predicted usage occurred in **1,051 records (52.5%)**.

The analysis estimated approximately:

**R44,853.97 in potential network over-allocation costs**

Potential actions include:

- Improving demand forecasting
- Adjusting network resource allocation
- Monitoring high-variance segments
- Incorporating network conditions into forecasting

---

### 👥 Customer Segmentation

The segmentation identified:

| Segment | Users | Average ARPU | Average Data |
|---|---:|---:|---:|
| Regular User | 890 | R191.64 | 1.85 GB |
| Revenue Driver | 573 | R595.95 | 8.41 GB |
| Upsell Opportunity | 539 | R77.56 | 0.50 GB |

This provides a framework for differentiated customer strategies rather than treating the customer base uniformly.

---

### 🌐 Network Efficiency

The significant increase in prediction error during congestion highlights an opportunity to improve resource allocation during high-demand periods.

The analysis supports a move toward **congestion-aware demand forecasting**.

---

## 9. Visual Summary Dashboard

The Streamlit dashboard provides an interactive view of:

- Customer consumption
- ARPU performance
- Network conditions
- Peak-hour behaviour
- Customer segments
- Service profitability
- Subscription plan performance
- Prediction error
- Revenue opportunities

> **Dashboard:** Add Streamlit deployment link here.

---

## 10. Strategic Recommendations

### 1. 🎮 Optimise Service Bundles

Develop targeted gaming and high-engagement bundles while reviewing streaming pricing and margins.

### 2. 🌐 Implement Congestion-Aware Forecasting

Incorporate network congestion indicators into forecasting models and capacity planning processes.

### 3. 💰 Retain High-Value Customers

Target the **573 Revenue Drivers** with personalised retention offers, loyalty benefits and premium data bundles.

### 4. 📱 Optimise Subscription Plans

Target high-usage customers for Postpaid Unlimited upgrades and review the pricing and value proposition of Prepaid Monthly.

### 5. 📊 Improve Forecasting During High-Demand Periods

Prioritise model improvements for congested networks and high-consumption customer segments.

Potential improvements include:

- Network performance indicators
- Congestion features
- Device performance metrics
- Segment-specific forecasting
- Real-time usage signals

---

## 11. Conclusion

The Telecom Consumption Intelligence System demonstrates how customer behaviour, predictive analytics and business intelligence can be combined to support telecom decision-making.

The analysis identified measurable opportunities across:

- **Revenue optimisation**
- **Customer retention**
- **Targeted upselling**
- **Bundle optimisation**
- **Subscription strategy**
- **Network capacity planning**

The strongest finding was the relationship between network congestion and forecasting performance, where prediction error increased by approximately **255.7%**.

Overall, the project demonstrates a complete workflow from **raw telecom data to predictive modelling, business analysis and actionable recommendations**.

---

## 12. Next Steps

### Technical

- Add additional network performance and congestion features.
- Improve forecasting for high-demand customer segments.
- Explore real-time prediction capabilities.
- Monitor model performance over time.
- Implement automated model retraining.

### Business

- Validate revenue opportunity calculations against real pricing data.
- Integrate usage predictions with bundle recommendation systems.
- Connect customer segmentation with CRM systems.
- Develop automated alerts for high-value customers and unusual consumption.
- Evaluate recommendations using controlled A/B testing.

---

## 📌 Disclaimer

This is a **portfolio project based on simulated telecom data**.

Revenue opportunities, cost estimates and profitability calculations are based on assumptions within the analysis and should be validated using real operational pricing, customer and network cost data before being used for actual business decisions.