"""A short guide for new managers: shown as a step-by-step dialog from the sidebar, and listed on the About page."""
import streamlit as st

STEPS = [
    ("Start with the Overview",
     "The cards at the top answer: how many customers, how much data they use, what they pay, who might leave, and how much "
     "data they will use tomorrow. The coloured edge on a card tells you how to read it: **teal** is neutral, **green** is "
     "healthy, **amber** is worth watching, **red** is a real risk such as customers likely to leave. Below the cards, "
     "Business Actions suggest what to look at next. They are decision support, not decisions."),
    ("Plan capacity with Tomorrow's Forecast",
     "This is the model's forecast of next-day data use by region, plan and network. Capacity to provision is the forecast "
     "plus a safety buffer, which you can change under Business assumptions in the sidebar. Customers using more than "
     "expected are the ones to consider for a top-up offer."),
    ("Follow the money in Revenue Analysis",
     "Monthly revenue and what each plan earns come from customers' bills. Potential top-up revenue and revenue at risk are "
     "estimates built from assumptions you set (take-up rate, price per GB, churn-risk threshold), so treat them as "
     "scenarios, not forecasts of income."),
    ("Look across Geography and Customer Insights",
     "Geography compares regions on any measure. Customer Insights shows segments, lists customers using more or less than "
     "expected, and lets you look up a single customer."),
    ("Compare two periods or two files",
     "Compare Data puts two periods, or the loaded data and another file, side by side. It says what moved most and whether "
     "that is good or bad for the business. The other file is checked first and does not replace your data."),
    ("Check that the model can be trusted",
     "Model Monitoring compares today's forecast error with the error when the model was trained. Healthy, Watch and Action "
     "needed tell you when to look closer. Feature importance shows what the model relies on. SHAP values show how much, "
     "and in which direction, each feature moves a forecast, including for a single customer."),
    ("Check the data, and work with it",
     "Data Checks answers one question: is this dataset safe to score? It ends with READY or NOT READY FOR SCORING and "
     "explains every problem in business terms. Its Data viewer lets you sort, edit, calculate and summarise the rows "
     "yourself, and download the result."),
    ("Controls and reports",
     "The sidebar holds upload, filters and assumptions. Everything recalculates when they change. Every page has a "
     "download for a PDF or Excel report. Appearance (System, Light or Dark) is in the three-dot menu at the top right. "
     "The data is synthetic, so use the dashboard to learn how it works, not to make real decisions."),
]


@st.dialog("How to read this dashboard", width="large")
def show():
    ss = st.session_state
    i = ss.setdefault("tour_i", 0)
    title, body = STEPS[i]
    st.caption(f"Step {i + 1} of {len(STEPS)}")
    st.progress((i + 1) / len(STEPS))
    st.subheader(title)
    st.write(body)
    back, nxt, _ = st.columns([1, 1, 3])
    back.button("Back", disabled=i == 0, key="tour_back", on_click=lambda: ss.update(tour_i=ss["tour_i"] - 1))
    if i < len(STEPS) - 1:
        nxt.button("Next", type="primary", key="tour_next", on_click=lambda: ss.update(tour_i=ss["tour_i"] + 1))
    elif nxt.button("Done", type="primary", key="tour_done"):
        ss["tour_i"] = 0
        st.rerun()
