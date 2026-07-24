"""Executive overview page."""

import streamlit as st

from components.charts import horizontal_bars, risk_donut, team_trend
from components.styles import metric_card, page_header
from components.tables import priority_table
from core.analytics import team_driver_summary, team_monthly_trend


def render(employees, history):
    page_header("TEAM COMMAND CENTER", "Overview", "A clear view of retention health, emerging risk, and where manager attention matters most.")
    health = round(employees["keep_score"].mean() * .7 + (100 - employees["attention"].mean() * 100) * .3)
    attention = int(employees["attention"].sum())
    impact_risk = int(employees["high_impact_at_risk"].sum())
    average = employees["keep_score"].mean()
    cols = st.columns(4)
    with cols[0]:
        metric_card("Team Health Score", f"{health}/100", "Retention health + risk mix", "good" if health >= 72 else "watch")
    with cols[1]:
        metric_card("Requiring Attention", attention, f"{attention / len(employees):.0%} of the team", "risk" if attention >= 5 else "watch")
    with cols[2]:
        metric_card("High-Impact at Risk", impact_risk, "Impact ≥70 and not low risk", "risk")
    with cols[3]:
        metric_card("Average Keep Score", f"{average:.1f}", "Current team average", "good" if average >= 72 else "watch")

    left, right = st.columns([1.7, 1])
    with left:
        st.markdown("<div class='section-title'>Six-month team health trend</div>", unsafe_allow_html=True)
        st.plotly_chart(team_trend(team_monthly_trend(history)), use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Risk distribution</div>", unsafe_allow_html=True)
        st.plotly_chart(risk_donut(employees), use_container_width=True)

    drivers = team_driver_summary(employees).tail(6)
    declines = employees.nsmallest(5, "monthly_change").sort_values("monthly_change")
    left, right = st.columns([1, 1])
    with left:
        st.markdown("<div class='section-title'>Top team risk drivers</div>", unsafe_allow_html=True)
        st.plotly_chart(horizontal_bars(drivers, "weighted_contribution", "factor"), use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Largest monthly declines</div>", unsafe_allow_html=True)
        decline_view = declines[["employee_name", "role", "keep_score", "monthly_change"]].rename(
            columns={"employee_name": "Employee", "role": "Role", "keep_score": "Keep", "monthly_change": "Monthly Δ"}
        )
        st.dataframe(
            decline_view.style.format({"Keep": "{:.1f}", "Monthly Δ": "{:+.1f}"})
            .background_gradient(subset=["Monthly Δ"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True, height=300,
        )

    st.markdown("<div class='section-title'>Priority employees</div>", unsafe_allow_html=True)
    st.dataframe(priority_table(employees), use_container_width=True, hide_index=True, height=320)
