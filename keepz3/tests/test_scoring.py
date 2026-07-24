from data.generator import generate_employee_data
from core.scoring import calculate_business_impact, calculate_keep_score, risk_category


def test_scores_are_bounded():
    employees = generate_employee_data()
    assert employees.apply(calculate_keep_score, axis=1).between(0, 100).all()
    assert employees.apply(calculate_business_impact, axis=1).between(0, 100).all()


def test_risk_thresholds():
    assert risk_category(54.9) == "High"
    assert risk_category(55) == "Medium"
    assert risk_category(72) == "Low"
