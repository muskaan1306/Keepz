"""Keep — transparent, rule-based employee retention dashboard."""

import streamlit as st

from components.styles import apply_theme, render_sidebar_brand
from core.analytics import build_dashboard_data
from data.generator import generate_employee_data, generate_monthly_history
from pages.individual_insights import render as render_individual
from pages.overview import render as render_overview
from pages.risk_matrix import render as render_risk_matrix
from pages.team_patterns import render as render_team_patterns


st.set_page_config(
    page_title="Keep | Team Retention Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


@st.cache_data
def load_data():
    employees = generate_employee_data()
    history = generate_monthly_history(employees)
    return build_dashboard_data(employees, history)


employees, history = load_data()

with st.sidebar:
    render_sidebar_brand()
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Team Risk Matrix", "Individual Insights", "Team Patterns"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.caption("RULE-BASED PEOPLE INTELLIGENCE")
    st.markdown(
        "<div class='sidebar-note'>Scores use explainable weighted factors. "
        "No machine-learning model is used.</div>",
        unsafe_allow_html=True,
    )

if page == "Overview":
    render_overview(employees, history)
elif page == "Team Risk Matrix":
    render_risk_matrix(employees, history)
elif page == "Individual Insights":
    render_individual(employees, history)
else:
    render_team_patterns(employees, history)
