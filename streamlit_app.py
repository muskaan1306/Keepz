
import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Keepz,
    page_icon="📊",
    layout="wide"
)

# Dashboard Title
st.title("📊 Keepz Dashboard")
st.markdown("A dashboard to view attrition")

# Sidebar
# st.sidebar.header("Filters")

# num_days = st.sidebar.slider(
#     "Select Number of Days",
#     min_value=7,
#     max_value=30,
#     value=14
# )

df=pd.read_csv("employee_attrition_dataset.csv")

# # Sample Data
# dates = pd.date_range(end=pd.Timestamp.today(), periods=num_days)
# sales = np.random.randint(100, 1000, size=num_days)

# df = pd.DataFrame({
#     "Date": dates,
#     "Sales": sales
# })

# KPI Section
col1, col2, col3, col4, col5 = st.columns(5)

# with col1:
#     st.metric(f"df2['emp_id']", df"${df['Sales'].sum():,.0f}")

with col2:
    st.metric(" Attrition Risk", f"{df['attrition_risk_score']}")

with col3:
    st.metric("business impact if exits", f"${df['business_impact_score']}")


# with col1:
#     st.metric("Total Sales", f"${df['Sales'].sum():,.0f}")

# with col2:
#     st.metric("Average Sales", f"${df['Sales'].mean():,.0f}")

# with col3:
#     st.metric("Max Sales", f"${df['Sales'].max():,.0f}")

# Chart Section
# st.subheader("Sales Trend")
# st.line_chart(df.set_index("Date"))

# # Data Table
# st.subheader("Sales Data")
# st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Built with Streamlit")
st.markdown("---")
st.caption("Built with Streamlit")
