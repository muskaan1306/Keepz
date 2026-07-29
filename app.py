from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from utils.charts import (
    attrition_criticality_scatter,
    feature_importance_chart,
    geography_map,
    location_comparison,
    probability_gauge,
    risk_distribution,
)

st.set_page_config(page_title="Keepz | Manager Retention Brief", page_icon="◆", layout="wide")

FEATURE_RULES = {
    "overtime_hours_month": ("Monthly overtime", "low"),
    "work_life_balance": ("Work-life balance", "high"),
    "workload_score": ("Workload", "low"),
    "engagement_score": ("Engagement", "high"),
    "promotion_wait_months": ("Promotion wait", "low"),
    "manager_rating": ("Manager rating", "high"),
    "flexible_work_score": ("Work flexibility", "high"),
}


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    employees = pd.read_csv("data/employee_scores.csv")
    employees["attrition_probability"] = employees["attrition_probability"].clip(.05, .80)
    employees["criticality_probability"] = employees["criticality_probability"].clip(.05, .80)
    employees["Keepz"] = (
        100
        * (
            0.7 * employees["criticality_probability"] * employees["attrition_probability"]
            + 0.3 * employees["criticality_probability"]
        )
    ).round(2)
    # Backward-compatible derivation prevents stale Streamlit caches or an
    # older generated CSV from breaking the Individual view.
    employees["attrition_prediction"] = employees["attrition_probability"].map(
        lambda value: "Likely to leave" if value >= .50 else "Likely to stay"
    )
    employees["criticality_prediction"] = employees["criticality_probability"].map(
        lambda value: "Critical" if value >= .50 else "Non-critical"
    )
    return employees, pd.read_csv("data/feature_importance.csv")


def inject_css() -> None:
    with open("assets/styles.css", encoding="utf-8") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)


def metric(label: str, value: str, tone: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card {tone}-border"><div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value {tone}">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


def heading(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="section-heading"><h3>{html.escape(title)}</h3>'
        f'<span>{html.escape(subtitle)}</span></div>',
        unsafe_allow_html=True,
    )


def navigate(page: str, employee_id: str | None = None) -> None:
    st.session_state.nav_page = page
    if employee_id:
        st.session_state.employee_id = employee_id


def probability_band(value: float, high_is_bad: bool = True) -> tuple[str, str]:
    if high_is_bad:
        return ("High", "bad") if value >= .50 else ("Medium", "warn") if value >= .25 else ("Low", "good")
    return ("High", "good") if value >= .55 else ("Medium", "warn") if value >= .30 else ("Low", "bad")


def keepz_band(value: float, full_population: pd.DataFrame) -> tuple[str, str]:
    if value >= 55:
        return "High", "bad"
    if value >= 40:
        return "Elevated", "orange"
    if value >= 20:
        return "Medium", "warn"
    return "Low", "good"


def keepz_thresholds(full_population: pd.DataFrame) -> tuple[float, float, float]:
    return (20.0, 40.0, 55.0)


def replacement_band(months: float) -> tuple[str, str]:
    return ("High", "bad") if months >= 3 else ("Medium", "warn") if months >= 2 else ("Low", "good")


def feature_tone(feature: str, value: float) -> tuple[str, str]:
    if feature == "overtime_hours_month":
        tone = "good" if value <= 8 else "warn" if value <= 20 else "bad"
    elif feature == "promotion_wait_months":
        tone = "good" if value <= 12 else "warn" if value <= 24 else "bad"
    elif feature == "workload_score":
        tone = "good" if value <= 2 else "warn" if value <= 3 else "bad"
    else:
        tone = "good" if value >= 4 else "warn" if value >= 3 else "bad"
    category = {"good": "Good", "warn": "Medium", "bad": "Concern"}[tone]
    return category, tone


def driver_rows(row: pd.Series, importance: pd.DataFrame) -> list[tuple[str, str, str]]:
    ranked = (
        importance[importance["model"] == "attrition_probability"]
        .sort_values("importance", ascending=False)["feature"]
    )
    rows = []
    for feature in [value for value in ranked if value in FEATURE_RULES][:6]:
        label, _ = FEATURE_RULES[feature]
        category, tone = feature_tone(feature, row[feature])
        value = row[feature]
        display = f"{value:g}"
        rows.append((label, f"{display} · {category}", tone))
    return rows


def team_view(df: pd.DataFrame, importance: pd.DataFrame) -> None:
    action_case = (
        (df["attrition_probability"] >= .50)
        & (df["criticality_probability"] >= .50)
    )
    ranked = df.sort_values("Keepz", ascending=False).head(6)
    _, average_keepz_tone = keepz_band(df["Keepz"].mean(), employees)

    st.markdown('<div class="eyebrow">MANAGER BRIEF</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Where does your team need attention?</h1>', unsafe_allow_html=True)
    st.caption(
        "Keepz = 100 x (0.7 x criticality x attrition + 0.3 x criticality). "
        "It combines role importance with attrition urgency."
    )
    cols = st.columns(4)
    cards = [
        ("Team size", str(len(df)), "neutral", "Employees in current filter"),
        ("Average Keepz", f"{df['Keepz'].mean():.2f}", average_keepz_tone,
         "Importance to retain"),
        ("Average attrition probability", f"{df['attrition_probability'].mean():.1%}",
         "bad" if df["attrition_probability"].mean() >= .5 else "warn",
         "Random Forest probability"),
        ("Retention-action cases", str(int(action_case.sum())),
         "bad" if action_case.any() else "good",
         "Predicted leave and critical"),
    ]
    for col, card in zip(cols, cards):
        with col:
            metric(*card)

    left, right = st.columns([1.7, 1])
    with left:
        heading("Attrition probability vs criticality", "Color = Keepz")
        st.plotly_chart(
            attrition_criticality_scatter(df, keepz_thresholds(employees)),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with right:
        heading("Priority attention", "Highest Keepz employees")
        for _, row in ranked.iterrows():
            c1, c2 = st.columns([3.1, 1])
            with c1:
                st.button(
                    f"{row['employee_name']} · {row['role']}",
                    key=f"open_{row['employee_id']}",
                    use_container_width=True,
                    on_click=navigate,
                    args=("Individual", row["employee_id"]),
                )
            with c2:
                label, tone = keepz_band(row["Keepz"], employees)
                st.markdown(
                    f'<div class="risk-pill {tone}">{label}<br>Keepz {row["Keepz"]:.2f}</div>',
                    unsafe_allow_html=True,
                )

    # left, right = st.columns([1, 1.55])
    # with left:
    #     heading("Attrition risk mix", "Counts by bounded probability")
    #     st.plotly_chart(
    #         risk_distribution(df),
    #         use_container_width=True,
    #         config={"displayModeBar": False},
    #     )
    # with right:
    #     heading("What drives attrition predictions?", "Random Forest feature importance")
    #     st.plotly_chart(
    #         feature_importance_chart(importance, "attrition_probability"),
    #         use_container_width=True,
    #         config={"displayModeBar": False},
    #     )


def individual_view(
    population: pd.DataFrame,
    full_population: pd.DataFrame,
    importance: pd.DataFrame,
) -> None:
    ids = population["employee_id"].tolist()
    current = st.session_state.get("employee_id", ids[0])
    current = current if current in ids else ids[0]
    selected_name = st.selectbox(
        "Select employee",
        population["employee_name"].tolist(),
        index=ids.index(current),
    )
    row = population.loc[population["employee_name"] == selected_name].iloc[0]
    st.session_state.employee_id = row["employee_id"]

    st.markdown('<div class="eyebrow">EMPLOYEE REVIEW</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="page-title">{html.escape(row["employee_name"])}</h1>', unsafe_allow_html=True)
    st.caption(
        f"{row['role']} · {row['department']} · {row['location']} · "
        f"{row['tenure_years']:.1f} years"
    )

    attrition_category, attrition_tone = probability_band(row["attrition_probability"])
    criticality_category, _ = probability_band(row["criticality_probability"], False)
    keepz_category, keepz_tone = keepz_band(row["Keepz"], full_population)
    prediction = row["attrition_prediction"]
    prediction_tone = "bad" if prediction == "Likely to leave" else "good"

    cols = st.columns(4)
    with cols[0]:
        metric("Prediction", prediction, prediction_tone, "Random Forest at 50% threshold")
    with cols[1]:
        st.plotly_chart(
            probability_gauge(
                row["attrition_probability"], "Attrition",
                attrition_category, True,
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with cols[2]:
        st.plotly_chart(
            probability_gauge(
                row["criticality_probability"], "Criticality",
                criticality_category, False,
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with cols[3]:
        metric(
            "Keepz",
            f"{row['Keepz']:.2f}",
            keepz_tone,
            f"{keepz_category} retention importance",
        )

    drivers = driver_rows(row, importance)
    concerns = [label.lower() for label, _, tone in drivers if tone == "bad"][:3]
    reason = ", ".join(concerns) if concerns else "no major adverse signal among the leading features"
    replacement_category, replacement_tone = replacement_band(row["replacement_time_months"])
    summary = (
        f"{row['employee_name']} has {row['attrition_probability']:.1%} attrition probability "
        f"and {row['criticality_probability']:.1%} criticality probability. "
        f"Signals to validate with the employee are {reason}. "
        f"The Keepz score is {row['Keepz']:.2f}."
    )
    left, right = st.columns([1, 2])
    # with left:
    #     st.markdown(
    #         f'<div class="detail-card"><h3>Replacement difficulty</h3>'
    #         f'<div class="detail-value {replacement_tone}">{replacement_category}</div>'
    #         f'<p>Estimated replacement time: {row["replacement_time_months"]} months</p></div>',
    #         unsafe_allow_html=True,
    #     )
    # with right:
    st.markdown(
            f'<div class="detail-card"><h3>Why this employee may need attention</h3>'
            f'<p>{html.escape(summary)}</p></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1.35, 1])
    with left:
        heading("Signals to discuss", "Green = good · amber = medium · red = concern")
        for label, value, tone in drivers:
            st.markdown(
                f'<div class="driver-row {tone}"><span>{html.escape(label)}</span>'
                f'<strong>{html.escape(value)}</strong></div>',
                unsafe_allow_html=True,
            )
    with right:
        heading("Manager context", "Reproducible staffing and performance facts")
        context = [
            ("Performance", f"{row['performance_rating']}/5",
             "good" if row["performance_rating"] >= 4 else "warn"),
            ("Active projects", str(row["active_projects"]),
             "bad" if row["active_projects"] >= 5 else "warn"),
            ("Direct reports", str(row["direct_reports"]), "neutral"),
            ("Client facing", "Yes" if row["client_facing"] else "No",
             "warn" if row["client_facing"] else "good"),
            ("Successor ready", "Yes" if row["succession_ready"] else "No",
             "good" if row["succession_ready"] else "bad"),
        ]
        for label, value, tone in context:
            st.markdown(
                f'<div class="context-row {tone}"><span>{html.escape(label)}</span>'
                f'<strong>{html.escape(value)}</strong></div>',
                unsafe_allow_html=True,
            )


def geography_view(df: pd.DataFrame) -> None:
    source = df.assign(
        action_case=(
            (df["attrition_probability"] >= .50)
            & (df["criticality_probability"] >= .50)
        )
    )
    geo = source.groupby(
        ["location", "latitude", "longitude"], as_index=False
    ).agg(
        employees=("employee_id", "size"),
        avg_attrition=("attrition_probability", "mean"),
        avg_criticality=("criticality_probability", "mean"),
        avg_keepz=("Keepz", "mean"),
        action_cases=("action_case", "sum"),
    )
    highest = geo.nlargest(1, "avg_keepz").iloc[0]
    _, average_keepz_tone = keepz_band(df["Keepz"].mean(), employees)
    st.markdown('<div class="eyebrow">GEOGRAPHIC EXPOSURE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Where is retention exposure concentrated?</h1>', unsafe_allow_html=True)
    st.caption("Low Keepz is green, medium is amber, and high Keepz is red.")

    cols = st.columns(3)
    cards = [
        ("Locations", str(len(geo)), "neutral", "Offices represented"),
        ("Average Keepz", f"{df['Keepz'].mean():.2f}", average_keepz_tone,
         "Importance to retain"),
        ("Highest average Keepz", highest["location"], "bad",
         f"Office score: {highest['avg_keepz']:.2f}"),
    ]
    for col, card in zip(cols, cards):
        with col:
            metric(*card)

    left, right = st.columns([1.35, 1])
    with left:
        heading("Keepz by office", "Size = headcount · color = average Keepz")
        st.plotly_chart(
            geography_map(geo, keepz_thresholds(employees)),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with right:
        heading("Office comparison", "Average Keepz")
        st.plotly_chart(
            location_comparison(geo, keepz_thresholds(employees)),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    heading("Location values", "Figures represented on the map")
    table = geo[[
        "location", "employees", "avg_attrition", "avg_criticality",
        "avg_keepz", "action_cases",
    ]].copy()
    table["avg_attrition"] = table["avg_attrition"].map(lambda value: f"{value:.1%}")
    table["avg_criticality"] = table["avg_criticality"].map(lambda value: f"{value:.1%}")
    table["avg_keepz"] = table["avg_keepz"].round(2)
    table.columns = [
        "Location", "Employees", "Average attrition probability",
        "Average criticality probability", "Average Keepz", "Action cases",
    ]
    st.dataframe(
        table.sort_values("Average Keepz", ascending=False),
        hide_index=True,
        use_container_width=True,
    )

st.markdown(
    """
    <style>
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem;
    }
    [data-testid="stSidebar"] div:first-child {
        padding-top: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
inject_css()
employees, feature_importance = load_data()
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Team"

with st.sidebar:
    st.markdown('<div class="brand"><span>◆</span> Keepz</div>', unsafe_allow_html=True)
    st.caption("Manager retention brief")
    page = st.radio(
        "Navigation", ["Individual", "Team", "Geography"],
        key="nav_page", label_visibility="collapsed",
    )
    st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
    department = st.selectbox(
        "Department",
        ["All departments"] + sorted(employees["department"].unique()),
        index=(["All departments"] + sorted(employees["department"].unique())).index("Marketing"),
    )
    location = st.selectbox(
        "Location",
        ["All locations"] + sorted(employees["location"].unique()),
        index=(["All locations"] + sorted(employees["location"].unique())).index("Bangalore"),
    )
    st.caption("Random Forest probabilities are bounded between 5% and 80%.")

filtered = employees.copy()
if department != "All departments":
    filtered = filtered[filtered["department"] == department]
if location != "All locations":
    filtered = filtered[filtered["location"] == location]

if filtered.empty:
    st.warning("No employees match these filters.")
elif page == "Individual":
    individual_view(filtered, employees, feature_importance)
elif page == "Geography":
    geography_view(filtered)
else:
    team_view(filtered, feature_importance)


