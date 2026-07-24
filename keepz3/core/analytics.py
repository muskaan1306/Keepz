"""Derive dashboard-ready metrics from fictional raw inputs."""

from __future__ import annotations

import pandas as pd

from core.scoring import (
    calculate_business_impact,
    calculate_keep_score,
    factor_contributions,
    risk_category,
)


def build_dashboard_data(employees: pd.DataFrame, history: pd.DataFrame):
    history = history.copy()
    history["keep_score"] = history.apply(calculate_keep_score, axis=1)
    history = history.sort_values(["employee_id", "month"])

    scored = employees.copy()
    changes = history.groupby("employee_id")["keep_score"].agg(
        previous_score=lambda x: x.iloc[-2], current_score="last"
    )
    changes["monthly_change"] = changes["current_score"] - changes["previous_score"]
    scored = scored.merge(changes, on="employee_id")
    scored["keep_score"] = scored["current_score"]
    scored["business_impact"] = scored.apply(calculate_business_impact, axis=1)
    scored["risk_level"] = scored["keep_score"].apply(risk_category)
    scored["attention"] = scored["risk_level"].isin(["High", "Medium"])
    scored["high_impact_at_risk"] = (
        (scored["business_impact"] >= 70) & scored["attention"]
    )
    scored["priority_score"] = (
        (100 - scored["keep_score"]) * 0.55
        + scored["business_impact"] * 0.35
        + (-scored["monthly_change"]).clip(lower=0) * 2 * 0.10
    ).round(1)
    scored["priority_rank"] = scored["priority_score"].rank(
        ascending=False, method="first"
    ).astype(int)

    top_drivers = []
    for _, row in scored.iterrows():
        momentum = max(0, -row["monthly_change"])
        contributions = factor_contributions(row, momentum)
        top_drivers.append(contributions.iloc[0]["factor"])
    scored["top_risk_driver"] = top_drivers
    return scored.sort_values("priority_rank"), history


def team_monthly_trend(history: pd.DataFrame) -> pd.DataFrame:
    return history.groupby("month", as_index=False)["keep_score"].mean()


def team_driver_summary(employees: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, row in employees.iterrows():
        frame = factor_contributions(row, max(0, -row["monthly_change"]))
        frame["employee_id"] = row["employee_id"]
        frames.append(frame)
    return (
        pd.concat(frames)
        .groupby("factor", as_index=False)["weighted_contribution"]
        .mean()
        .sort_values("weighted_contribution", ascending=True)
    )
