"""Central scoring rules and visual constants."""

RISK_WEIGHTS = {
    "overtime_hours": 0.16,
    "promotion_delay_months": 0.14,
    "engagement": 0.20,
    "workload": 0.14,
    "compensation_gap": 0.15,
    "manager_relationship": 0.16,
    "momentum": 0.05,
}

IMPACT_WEIGHTS = {
    "seniority": 0.18,
    "dependencies": 0.18,
    "client_criticality": 0.20,
    "specialised_skills": 0.18,
    "critical_project_owner": 0.12,
    "replacement_time_months": 0.14,
}

FACTOR_LABELS = {
    "overtime_hours": "Overtime",
    "promotion_delay_months": "Promotion delay",
    "engagement": "Low engagement",
    "workload": "Workload",
    "compensation_gap": "Compensation gap",
    "manager_relationship": "Manager relationship",
    "momentum": "Recent decline",
}

BLUE = "#2563EB"
NAVY = "#0B1739"
RED = "#E5484D"
GREEN = "#16A36A"
AMBER = "#E9A23B"
SLATE = "#667085"
LIGHT_BLUE = "#EAF2FF"

RISK_COLORS = {"High": RED, "Medium": AMBER, "Low": GREEN}
