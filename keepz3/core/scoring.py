"""Transparent scoring functions. Every transformation is explicit and bounded."""

from __future__ import annotations

import pandas as pd

from core.constants import FACTOR_LABELS, IMPACT_WEIGHTS, RISK_WEIGHTS


def _bounded(value, lower, upper):
    return max(0.0, min(100.0, (float(value) - lower) / (upper - lower) * 100))


def risk_factor_scores(row, momentum=0.0) -> dict[str, float]:
    """Convert differently-scaled raw inputs into comparable 0–100 risks."""
    return {
        "overtime_hours": _bounded(row["overtime_hours"], 0, 20),
        "promotion_delay_months": _bounded(row["promotion_delay_months"], 0, 24),
        "engagement": 100 - _bounded(row["engagement"], 0, 100),
        "workload": _bounded(row["workload"], 40, 95),
        "compensation_gap": _bounded(row["compensation_gap"], 0, 15),
        "manager_relationship": 100 - _bounded(row["manager_relationship"], 0, 100),
        "momentum": _bounded(momentum, 0, 12),
    }


def calculate_keep_score(row, momentum=0.0) -> float:
    factors = risk_factor_scores(row, momentum)
    risk = sum(factors[key] * weight for key, weight in RISK_WEIGHTS.items())
    return round(max(0, min(100, 100 - risk)), 1)


def calculate_business_impact(row) -> float:
    values = {
        "seniority": row["seniority"],
        "dependencies": row["dependencies"],
        "client_criticality": row["client_criticality"],
        "specialised_skills": row["specialised_skills"],
        "critical_project_owner": 100 if row["critical_project_owner"] else 0,
        "replacement_time_months": _bounded(row["replacement_time_months"], 1, 9),
    }
    return round(sum(values[k] * w for k, w in IMPACT_WEIGHTS.items()), 1)


def risk_category(keep_score: float) -> str:
    if keep_score < 55:
        return "High"
    if keep_score < 72:
        return "Medium"
    return "Low"


def factor_contributions(row, momentum=0.0) -> pd.DataFrame:
    factors = risk_factor_scores(row, momentum)
    result = pd.DataFrame([
        {
            "factor": FACTOR_LABELS[key],
            "risk_score": round(value, 1),
            "weighted_contribution": round(value * RISK_WEIGHTS[key], 1),
        }
        for key, value in factors.items()
    ])
    return result.sort_values("weighted_contribution", ascending=False)
