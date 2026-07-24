from core.analytics import build_dashboard_data
from data.generator import generate_employee_data, generate_monthly_history


def test_dashboard_derivations():
    raw = generate_employee_data()
    employees, history = build_dashboard_data(raw, generate_monthly_history(raw))
    assert len(employees) == 15
    assert len(history) == 90
    assert employees["priority_rank"].nunique() == 15
    assert employees["top_risk_driver"].notna().all()
