"""Create a small, reproducible fictional workforce and six-month history."""

from __future__ import annotations

import pandas as pd


def generate_employee_data() -> pd.DataFrame:
    """Return intentionally varied employee inputs for meaningful demos."""
    columns = [
        "employee_id", "employee_name", "role", "location", "tenure_years",
        "overtime_hours", "promotion_delay_months", "engagement",
        "workload", "compensation_gap", "manager_relationship", "seniority",
        "dependencies", "client_criticality", "specialised_skills",
        "critical_project_owner", "replacement_time_months",
    ]
    rows = [
        ("E001", "Aarav Mehta", "Principal Architect", "Bengaluru", 8.2, 19, 24, 49, 88, 14, 52, 92, 90, 96, 94, True, 8),
        ("E002", "Isha Nair", "Product Manager", "Mumbai", 5.4, 12, 10, 67, 72, 8, 70, 76, 82, 88, 72, True, 6),
        ("E003", "Rohan Kapoor", "Data Engineer", "Pune", 3.1, 8, 4, 82, 61, 3, 84, 58, 62, 79, 86, False, 5),
        ("E004", "Meera Iyer", "Delivery Lead", "Chennai", 7.6, 16, 20, 55, 84, 11, 61, 88, 92, 91, 74, True, 7),
        ("E005", "Kabir Shah", "UX Designer", "Mumbai", 2.8, 5, 1, 89, 48, 1, 90, 44, 38, 50, 69, False, 3),
        ("E006", "Ananya Rao", "Cloud Engineer", "Bengaluru", 4.7, 14, 14, 62, 79, 9, 58, 68, 76, 78, 92, True, 7),
        ("E007", "Vikram Singh", "Business Analyst", "Delhi", 1.9, 7, 2, 78, 60, 5, 81, 40, 54, 68, 51, False, 3),
        ("E008", "Diya Patel", "Engineering Manager", "Pune", 6.9, 10, 8, 76, 69, 4, 78, 86, 91, 84, 77, True, 6),
        ("E009", "Arjun Reddy", "DevOps Specialist", "Hyderabad", 5.8, 18, 18, 51, 91, 13, 49, 73, 86, 89, 96, True, 9),
        ("E010", "Sanya Gupta", "QA Lead", "Delhi", 4.2, 6, 5, 84, 56, 2, 86, 66, 63, 71, 64, False, 4),
        ("E011", "Neel Joshi", "Solution Consultant", "Mumbai", 3.8, 13, 15, 59, 81, 10, 64, 62, 79, 93, 70, True, 6),
        ("E012", "Tara Menon", "People Partner", "Chennai", 5.1, 4, 7, 86, 52, 4, 91, 71, 70, 57, 61, False, 4),
        ("E013", "Rahul Verma", "Backend Developer", "Hyderabad", 2.3, 15, 9, 64, 83, 7, 67, 49, 72, 75, 89, False, 6),
        ("E014", "Zoya Khan", "Account Director", "Delhi", 9.0, 9, 16, 70, 68, 6, 73, 95, 88, 98, 66, True, 7),
        ("E015", "Aditya Bose", "Data Scientist", "Bengaluru", 3.6, 6, 3, 88, 58, 2, 89, 61, 67, 74, 95, False, 7),
    ]
    return pd.DataFrame(rows, columns=columns)


def generate_monthly_history(employees: pd.DataFrame) -> pd.DataFrame:
    """Generate raw monthly inputs with deterministic employee-specific trends."""
    months = pd.date_range(end=pd.Timestamp("2026-07-01"), periods=6, freq="MS")
    # Positive values worsen each month; negative values indicate improvement.
    slopes = {
        "E001": 2.5, "E002": 0.6, "E003": -0.5, "E004": 1.8, "E005": -0.7,
        "E006": 1.4, "E007": 0.1, "E008": -0.2, "E009": 2.7, "E010": -0.4,
        "E011": 1.9, "E012": -0.3, "E013": 1.3, "E014": 0.7, "E015": -0.8,
    }
    records = []
    for _, employee in employees.iterrows():
        slope = slopes[employee.employee_id]
        for i, month in enumerate(months):
            offset = i - 5
            records.append({
                "employee_id": employee.employee_id,
                "month": month,
                "overtime_hours": max(0, employee.overtime_hours + slope * offset * 0.55),
                "promotion_delay_months": max(0, employee.promotion_delay_months + offset),
                "engagement": min(100, max(0, employee.engagement - slope * offset * 1.3)),
                "workload": min(100, max(0, employee.workload + slope * offset)),
                "compensation_gap": max(0, employee.compensation_gap + slope * offset * 0.35),
                "manager_relationship": min(100, max(0, employee.manager_relationship - slope * offset)),
            })
    return pd.DataFrame(records)
