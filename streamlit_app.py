
import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Sample Dashboard",
    page_icon="📊",
    layout="wide"
)

# Dashboard Title
st.title("📊 Sales Dashboard")
st.markdown("A basic Streamlit dashboard example")

# Sidebar
st.sidebar.header("Filters")

num_days = st.sidebar.slider(
    "Select Number of Days",
    min_value=7,
    max_value=30,
    value=14
)

# Sample Data
dates = pd.date_range(end=pd.Timestamp.today(), periods=num_days)
sales = np.random.randint(100, 1000, size=num_days)

df = pd.DataFrame({
    "Date": dates,
    "Sales": sales
})

# KPI Section
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"${df['Sales'].sum():,.0f}")

with col2:
    st.metric("Average Sales", f"${df['Sales'].mean():,.0f}")

with col3:
    st.metric("Max Sales", f"${df['Sales'].max():,.0f}")

# Chart Section
st.subheader("Sales Trend")
st.line_chart(df.set_index("Date"))

# Data Table
st.subheader("Sales Data")
st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Built with Streamlit")
