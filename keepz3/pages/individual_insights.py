"""Employee-level explanation and action page."""

import streamlit as st

from components.charts import employee_trend, keep_gauge
from components.styles import metric_card, page_header
from core.constants import RISK_COLORS
from core.insights import employee_narrative
from core.scoring import factor_contributions


def render(employees, history):
    page_header("EMPLOYEE VIEW", "Individual Insights", "Understand the signals behind each score and choose a practical next action.")
    selected = st.selectbox(
        "Search or select an employee",
        employees["employee_name"].tolist(),
        index=0,
    )
    row = employees.loc[employees["employee_name"] == selected].iloc[0]
    employee_history = history[history["employee_id"] == row["employee_id"]]
    risk_text, impact_text, actions = employee_narrative(row)

    gauge, details = st.columns([1.1, 2])
    with gauge:
        st.markdown("<div class='section-title'>Keep Score</div>", unsafe_allow_html=True)
        st.plotly_chart(keep_gauge(row["keep_score"]), use_container_width=True)
    with details:
        st.markdown(f"### {row['employee_name']}")
        st.caption(f"{row['role']} · {row['location']} · {row['tenure_years']:.1f} years")
        cols = st.columns(3)
        with cols[0]:
            tone = "risk" if row["risk_level"] == "High" else "watch" if row["risk_level"] == "Medium" else "good"
            metric_card("Risk Level", row["risk_level"], "Rule-based category", tone)
        with cols[1]:
            metric_card("Business Impact", f"{row['business_impact']:.0f}/100", "Operational importance", "risk" if row["business_impact"] >= 70 else "")
        with cols[2]:
            metric_card("Replacement Difficulty", f"{row['replacement_time_months']} months", "Estimated time to replace", "risk" if row["replacement_time_months"] >= 7 else "")
        st.markdown("<div class='section-title'>Why this employee is at risk</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight'>{risk_text}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("<div class='section-title'>Six-month Keep Score trend</div>", unsafe_allow_html=True)
        st.plotly_chart(employee_trend(employee_history), use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Risk factor contribution</div>", unsafe_allow_html=True)
        factors = factor_contributions(row, max(0, -row["monthly_change"]))
        factor_view = factors.rename(columns={
            "factor": "Factor", "risk_score": "Risk signal", "weighted_contribution": "Score impact"
        })
        st.dataframe(
            factor_view.style.format({"Risk signal": "{:.1f}", "Score impact": "{:.1f}"})
            .background_gradient(subset=["Risk signal"], cmap="RdYlGn_r", vmin=0, vmax=100),
            use_container_width=True, hide_index=True, height=290,
        )

    left, right = st.columns(2)
    with left:
        st.markdown("<div class='section-title'>Business impact explanation</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-card'>{impact_text}</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='section-title'>Recommended manager actions</div>", unsafe_allow_html=True)
        st.markdown("<div class='info-card'>" + "".join(
            f"<div style='margin-bottom:.65rem'><b style='color:#2563EB'>{i}.</b> {action}</div>"
            for i, action in enumerate(actions, 1)
        ) + "</div>", unsafe_allow_html=True)

    with st.expander("View transparent score inputs"):
        raw_fields = [
            "overtime_hours", "promotion_delay_months", "engagement", "workload",
            "compensation_gap", "manager_relationship", "seniority", "dependencies",
            "client_criticality", "specialised_skills", "critical_project_owner",
            "replacement_time_months",
        ]
        st.json({key: row[key].item() if hasattr(row[key], "item") else row[key] for key in raw_fields})
