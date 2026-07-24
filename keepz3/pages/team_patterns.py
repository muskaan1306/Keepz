"""Location and team-wide patterns page."""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import horizontal_bars, location_bubble
from components.styles import page_header
from core.analytics import team_driver_summary
from core.insights import management_insight


def _location_summary(employees):
    base = employees.groupby("location").agg(
        employees=("employee_id", "count"),
        at_risk=("attention", "sum"),
        average_keep_score=("keep_score", "mean"),
    ).reset_index()
    drivers = (
        employees.groupby("location")["top_risk_driver"]
        .agg(lambda x: x.value_counts().index[0])
        .rename("top_driver").reset_index()
    )
    return base.merge(drivers, on="location")


def render(employees, history):
    page_header("ORGANISATIONAL SIGNALS", "Team Patterns", "See where risk clusters and which shared conditions managers can address together.")
    summary = _location_summary(employees)
    st.markdown("<div class='section-title'>Location risk landscape</div>", unsafe_allow_html=True)
    st.plotly_chart(location_bubble(summary), use_container_width=True)

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("<div class='section-title'>Employees and at-risk employees by location</div>", unsafe_allow_html=True)
        melted = summary.melt(
            id_vars="location", value_vars=["employees", "at_risk"],
            var_name="Measure", value_name="Count",
        )
        fig = px.bar(
            melted, x="location", y="Count", color="Measure", barmode="group",
            color_discrete_map={"employees": "#2563EB", "at_risk": "#E5484D"},
        )
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10), legend_title_text="", plot_bgcolor="white", paper_bgcolor="white")
        fig.update_yaxes(gridcolor="#EDF1F7")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Location scorecard</div>", unsafe_allow_html=True)
        display = summary.rename(columns={
            "location": "Location", "employees": "Employees", "at_risk": "At risk",
            "average_keep_score": "Avg Keep", "top_driver": "Top driver",
        })
        st.dataframe(
            display.style.format({"Avg Keep": "{:.1f}"})
            .background_gradient(subset=["Avg Keep"], cmap="RdYlGn", vmin=45, vmax=85),
            use_container_width=True, hide_index=True, height=340,
        )

    st.markdown("<div class='section-title'>Team-wide risk-driver comparison</div>", unsafe_allow_html=True)
    drivers = team_driver_summary(employees)
    st.plotly_chart(horizontal_bars(drivers, "weighted_contribution", "factor", height=360), use_container_width=True)
    st.markdown("<div class='section-title'>Automatically generated management insight</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='insight'>{management_insight(employees)}</div>", unsafe_allow_html=True)
