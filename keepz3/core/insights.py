"""Generate plain-language explanations and actions from the scoring rules."""

from core.scoring import factor_contributions


ACTION_LIBRARY = {
    "Overtime": "Rebalance near-term commitments and agree protected recovery time.",
    "Promotion delay": "Hold a career conversation and document a credible progression path.",
    "Low engagement": "Use a focused one-to-one to identify work that restores motivation.",
    "Workload": "Review priorities, remove low-value work, and reset delivery expectations.",
    "Compensation gap": "Review market positioning and available recognition options.",
    "Manager relationship": "Increase structured check-ins and agree clearer mutual expectations.",
    "Recent decline": "Discuss what changed this month and agree an early intervention.",
}


def employee_narrative(row):
    factors = factor_contributions(row, max(0, -row["monthly_change"])).head(3)
    names = factors["factor"].tolist()
    raw = ", ".join(names[:-1]) + f" and {names[-1]}" if len(names) > 1 else names[0]
    trend = (
        f"The Keep Score fell {abs(row['monthly_change']):.1f} points this month."
        if row["monthly_change"] < 0
        else f"The Keep Score improved {row['monthly_change']:.1f} points this month."
    )
    risk = f"{row['employee_name']} is rated {row['risk_level'].lower()} risk, led by {raw}. {trend}"
    impact = (
        f"Business Impact is {row['business_impact']:.0f}/100. The role has "
        f"{'critical project ownership, ' if row['critical_project_owner'] else ''}"
        f"a {row['replacement_time_months']}-month estimated replacement time, "
        f"and a dependency score of {row['dependencies']}/100."
    )
    actions = [ACTION_LIBRARY[name] for name in names]
    return risk, impact, actions


def management_insight(employees):
    risky = employees[employees["attention"]]
    if risky.empty:
        return "The team is broadly healthy. Maintain regular career and workload check-ins."
    location = (
        risky.groupby("location").size().sort_values(ascending=False).index[0]
    )
    driver = risky["top_risk_driver"].value_counts().index[0]
    high_impact = int(risky["high_impact_at_risk"].sum())
    return (
        f"{location} has the largest concentration of employees requiring attention. "
        f"{driver} is the most common leading driver among the at-risk group. "
        f"Prioritise the {high_impact} high-impact employee(s) at risk, then address "
        "the shared driver through a targeted team intervention."
    )
