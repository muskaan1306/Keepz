"""Styled dataframe helpers."""

from core.constants import AMBER, GREEN, RED


def priority_table(df, rows=7):
    view = df.sort_values("priority_rank").head(rows)[[
        "priority_rank", "employee_name", "role", "risk_level",
        "keep_score", "business_impact", "monthly_change", "top_risk_driver",
    ]].rename(columns={
        "priority_rank": "#", "employee_name": "Employee", "role": "Role",
        "risk_level": "Risk", "keep_score": "Keep", "business_impact": "Impact",
        "monthly_change": "Monthly Δ", "top_risk_driver": "Leading driver",
    })
    return view.style.format({"Keep": "{:.1f}", "Impact": "{:.1f}", "Monthly Δ": "{:+.1f}"}).map(
        lambda value: f"color: {RED if value == 'High' else AMBER if value == 'Medium' else GREEN}; font-weight: 700",
        subset=["Risk"],
    )
