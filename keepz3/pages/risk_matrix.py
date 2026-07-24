"""Interactive team risk matrix page."""

import streamlit as st

from components.charts import risk_donut, risk_matrix
from components.styles import metric_card, page_header
from components.tables import priority_table


def render(employees, history):
    page_header("PORTFOLIO VIEW", "Team Risk Matrix", "Balance retention probability against the business impact of losing each employee.")
    st.plotly_chart(risk_matrix(employees), use_container_width=True)
    st.caption("Bubble size reflects priority score. Quadrants use a Keep Score and Business Impact threshold of 65.")

    left, middle, right = st.columns([1.3, 1, 1])
    with left:
        st.markdown("<div class='section-title'>Priority list</div>", unsafe_allow_html=True)
        st.dataframe(priority_table(employees, 5), use_container_width=True, hide_index=True, height=285)
    with middle:
        st.markdown("<div class='section-title'>Risk distribution</div>", unsafe_allow_html=True)
        st.plotly_chart(risk_donut(employees), use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Score decline</div>", unsafe_allow_html=True)
        for _, row in employees.nsmallest(5, "monthly_change").iterrows():
            tone = "risk" if row["monthly_change"] < 0 else "good"
            metric_card(row["employee_name"], f"{row['monthly_change']:+.1f}", f"Current Keep Score {row['keep_score']:.1f}", tone)
            st.write("")
