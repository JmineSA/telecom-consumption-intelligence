import json

import streamlit as st

from src import tour
from src.config import MODEL_INFO

info = json.loads(MODEL_INFO.read_text())
v = info["val_metrics"]

st.title("About this project")
st.write("A daily, per-customer forecast of mobile data use for a South African operator, with the business "
         "view a manager needs on top of it. The data is synthetic.")

st.subheader("The business problem")
st.markdown("""
Operators ask three questions every day, and most answer them with weekly reports that look backwards.
- **How much data will customers use tomorrow?** So capacity can be ready before it is needed.
- **Who is about to use more than expected?** So a top-up or bundle can be offered at the right moment.
- **Who is quietly using less?** So retention can step in before the customer leaves.
""")

st.subheader("How it works")
st.markdown("""
1. Daily usage and customer data go in, from the default file or an upload.
2. Lag and rolling-average features are built from each customer's past days only.
3. A gradient boosting model forecasts next-day usage per customer.
4. Every page is calculated from the loaded data, so uploading a new file refreshes everything.
""")

st.subheader("How to read this dashboard")
for n, (title, body) in enumerate(tour.STEPS, 1):
    with st.expander(f"{n}. {title}"):
        st.write(body)

st.subheader("The model")
c = st.columns(4)
c[0].metric("Average error", f"{v['mae']:.2f} GB")
c[1].metric("Typical large error", f"{v['rmse']:.2f} GB")
c[2].metric("Variance explained", f"{v['r2']:.2f}")
c[3].metric("Features", info["n_features"])
st.caption(f"Validation results. {info['model_type']}, trained on {info['n_train_samples']:,} rows and validated on "
           f"{info['n_val_samples']:,} rows, split by date. Target: {info['target']}.")

st.subheader("Limits to keep in mind")
st.markdown("""
- The data is synthetic, so real operator data will behave differently.
- The 90-day window cannot show yearly seasonality.
- Congestion is a yes or no flag. Real networks have degrees of congestion.
- Holidays, promotions, and device launches are not modelled.
- The model does not use the current day's usage, only the days before it. Adding it is a natural next experiment.
- Revenue figures that depend on a top-up price and take-up rate use assumptions you set in the sidebar.
""")

st.subheader("Built with")
st.write("Python, pandas, scikit-learn, Streamlit, Plotly, ReportLab, and openpyxl.")
