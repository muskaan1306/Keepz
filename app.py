from __future__ import annotations

import html
import pandas as pd
import streamlit as st

from utils.charts import (
    feature_evidence_chart, geography_map, location_exposure,
    risk_distribution, risk_impact_scatter, score_gauge,
)

st.set_page_config(page_title="Keepz | Manager Retention Brief", page_icon="◆", layout="wide")

RISK_FEATURES = {
    "overtime_hours": ("Overtime hours", "low"),
    "work_life_balance": ("Work-life balance", "high"),
    "workload": ("Workload", "low"),
    "engagement": ("Engagement", "high"),
    "client_escalation_count": ("Client escalations", "low"),
    "work_flexibility_score": ("Work flexibility", "high"),
    "manager_relationship": ("Manager relationship", "high"),
    "peer_recognition_count": ("Peer recognition", "high"),
}


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv("data/employee_scores.csv"),
        pd.read_csv("data/feature_correlations.csv", index_col=0),
    )


def inject_css() -> None:
    with open("assets/styles.css", encoding="utf-8") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)


def metric(label: str, value: str, tone: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card {tone}-border"><div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value {tone}">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div></div>', unsafe_allow_html=True,
    )


def heading(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="section-heading"><h3>{html.escape(title)}</h3>'
        f'<span>{html.escape(subtitle)}</span></div>', unsafe_allow_html=True,
    )


def navigate(page: str, employee_id: str | None = None) -> None:
    st.session_state.nav_page = page
    if employee_id:
        st.session_state.employee_id = employee_id


def risk_band(value: float) -> tuple[str, str]:
    return ("High", "bad") if value >= 50 else ("Medium", "warn") if value >= 20 else ("Low", "good")


def impact_band(value: float) -> tuple[str, str]:
    return ("High", "bad") if value >= 70 else ("Medium", "warn") if value >= 40 else ("Low", "good")


def keepz_band(value: float, population: pd.DataFrame) -> tuple[str, str]:
    median, upper = population["Keepz"].quantile([.5, .75])
    return ("High", "bad") if value >= upper else ("Medium", "warn") if value >= median else ("Low", "good")


def replacement_band(months: float) -> tuple[str, str]:
    return ("High", "bad") if months >= 7 else ("Medium", "warn") if months >= 4 else ("Low", "good")


def driver_rows(row: pd.Series, population: pd.DataFrame,
                correlations: pd.DataFrame) -> list[tuple[str, str, str]]:
    ranked = sorted(RISK_FEATURES, key=lambda f: abs(float(
        correlations.loc[f, "attrition_risk_score"])), reverse=True)
    result = []
    for feature in ranked[:6]:
        label, _ = RISK_FEATURES[feature]
        value = row[feature]
        if feature == "overtime_hours":
            tone = "good" if value <= 10 else "warn" if value <= 20 else "bad"
        elif feature in {"work_life_balance", "engagement", "work_flexibility_score",
                         "manager_relationship"}:
            tone = "good" if value >= 4 else "warn" if value >= 3 else "bad"
        elif feature == "workload":
            tone = "good" if value <= 2 else "warn" if value <= 3 else "bad"
        elif feature == "client_escalation_count":
            tone = "good" if value == 0 else "warn" if value <= 2 else "bad"
        else:  # peer recognition count
            tone = "good" if value >= 5 else "warn" if value >= 2 else "bad"
        category = {"good": "Good", "warn": "Medium", "bad": "Concern"}[tone]
        display = f"{value:.1f}" if isinstance(value, float) else str(value)
        result.append((label, f"{display} · {category}", tone))
    return result


def team_view(df: pd.DataFrame) -> None:
    high_risk = df["attrition_risk_score"] >= 50
    high_keepz_cutoff = employees["Keepz"].quantile(.75)
    top = df.sort_values(["Keepz", "attrition_risk_score"], ascending=False).head(6)
    st.markdown('<div class="eyebrow">MANAGER BRIEF</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Where does your team need attention?</h1>', unsafe_allow_html=True)
    st.caption("Keepz combines the urgency to retain an employee with their likelihood of leaving.")

    cols = st.columns(4)
    cards = [
        ("Team size", str(len(df)), "neutral", "Employees in current filter"),
        ("Average Keepz", f"{df['Keepz'].mean():.2f}", "bad", "Higher means greater retention priority"),
        ("Average leave probability", f"{df['attrition_risk_score'].mean():.2f}", "warn", "Model probability out of 100"),
        ("High-Keepz employees", str(int((df["Keepz"] >= high_keepz_cutoff).sum())), "bad",
         f"Portfolio top quartile (≥ {high_keepz_cutoff:.2f})"),
    ]
    for col, card in zip(cols, cards):
        with col:
            metric(*card)

    left, right = st.columns([1.7, 1])
    with left:
        heading("Leave probability vs company impact", "Point color shows the Keepz gradient")
        st.plotly_chart(risk_impact_scatter(df), use_container_width=True,
                        config={"displayModeBar": False})
    with right:
        heading("Priority attention", "Highest Keepz employees")
        for _, row in top.iterrows():
            category, tone = keepz_band(row["Keepz"], employees)
            c1, c2 = st.columns([3.1, 1])
            with c1:
                st.button(f"{row['employee_name']} · {row['role']}",
                          key=f"open_{row['employee_id']}", use_container_width=True,
                          on_click=navigate, args=("Individual", row["employee_id"]))
            with c2:
                st.markdown(f'<div class="risk-pill {tone}">{category} {row["Keepz"]:.2f}</div>',
                            unsafe_allow_html=True)

    left, right = st.columns([1, 1.55])
    with left:
        heading("Risk mix", "Values show employee counts")
        st.plotly_chart(risk_distribution(df), use_container_width=True,
                        config={"displayModeBar": False})
    with right:
        heading("Evidence for leaving or staying", "Red = predicted leavers · green = stayers")
        st.plotly_chart(feature_evidence_chart(df), use_container_width=True,
                        config={"displayModeBar": False})


def individual_view(population: pd.DataFrame, correlations: pd.DataFrame) -> None:
    ids = population["employee_id"].tolist()
    current = st.session_state.get("employee_id", ids[0])
    current = current if current in ids else ids[0]
    selected_name = st.selectbox(
        "Select employee", population["employee_name"].tolist(), index=ids.index(current),
    )
    row = population.loc[population["employee_name"] == selected_name].iloc[0]
    st.session_state.employee_id = row["employee_id"]

    st.markdown('<div class="eyebrow">EMPLOYEE REVIEW</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="page-title">{html.escape(row["employee_name"])}</h1>', unsafe_allow_html=True)
    st.caption(f"{row['role']} · {row['department']} · {row['location']} · {row['tenure_years']:.1f} years")

    risk_category, risk_tone = risk_band(row["attrition_risk_score"])
    impact_category, _ = impact_band(row["impact_score"])
    keepz_category, keepz_tone = keepz_band(row["Keepz"], population)
    prediction = "Likely to leave" if int(row["attrition_label"]) == 1 else "Likely to stay"
    prediction_tone = "bad" if int(row["attrition_label"]) == 1 else "good"

    cols = st.columns(4)
    with cols[0]:
        metric("Prediction", prediction, prediction_tone,
               "Logistic-regression classification")
    with cols[1]:
        st.plotly_chart(score_gauge(row["attrition_risk_score"], "Leave probability",
                                    risk_category, False), use_container_width=True,
                        config={"displayModeBar": False})
    with cols[2]:
        st.plotly_chart(score_gauge(row["impact_score"], "Company impact",
                                    impact_category, False), use_container_width=True,
                        config={"displayModeBar": False})
    with cols[3]:
        metric("Keepz", f"{row['Keepz']:.2f}", keepz_tone,
               f"{keepz_category} retention priority")

    drivers = driver_rows(row, population, correlations)
    concerns = [label.lower() for label, _, tone in drivers if tone == "bad"][:3]
    reason = ", ".join(concerns) if concerns else "no strongly adverse feature signal"
    replacement_category, replacement_tone = replacement_band(row["replacement_time_months"])
    summary = (
        f"{row['employee_name']} is predicted to {'leave' if row['attrition_label'] else 'stay'} "
        f"with a leave probability of {row['attrition_risk_score']:.2f}. Key signals to discuss: "
        f"{reason}. Their {keepz_category.lower()} Keepz score of {row['Keepz']:.2f} indicates "
        f"{'strong' if keepz_category == 'High' else 'moderate' if keepz_category == 'Medium' else 'lower'} "
        "retention priority relative to this portfolio."
    )
    left, right = st.columns([1, 2])
    with left:
        st.markdown(
            f'<div class="detail-card"><h3>Replacement difficulty</h3>'
            f'<div class="detail-value {replacement_tone}">{replacement_category}</div>'
            f'<p>Estimated replacement time: {row["replacement_time_months"]} months</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f'<div class="detail-card"><h3>Why this employee may be at risk</h3>'
            f'<p>{html.escape(summary)}</p></div>', unsafe_allow_html=True,
        )

    left, right = st.columns([1.35, 1])
    with left:
        heading("Signals to discuss", "Green = good · amber = medium · red = concern")
        for label, value, tone in drivers:
            st.markdown(f'<div class="driver-row {tone}"><span>{html.escape(label)}</span>'
                        f'<strong>{html.escape(value)}</strong></div>', unsafe_allow_html=True)
    with right:
        heading("Manager context", "Facts shaping company impact")
        context = [
            ("Knowledge risk", f"{row['knowledge_risk_score']}/5", "warn"),
            ("Dependencies", str(row["dependencies"]), "warn"),
            ("Client criticality", f"{row['client_criticality']}/5", "warn"),
            ("Replacement time", f"{row['replacement_time_months']} months", replacement_tone),
            ("Succession coverage", str(row["succession_coverage"]),
             "good" if row["succession_coverage"] == "Ready Successor" else "bad"),
        ]
        for label, value, tone in context:
            st.markdown(f'<div class="context-row {tone}"><span>{html.escape(label)}</span>'
                        f'<strong>{html.escape(value)}</strong></div>', unsafe_allow_html=True)


def geography_view(df: pd.DataFrame) -> None:
    cutoff = employees["Keepz"].quantile(.75)
    source = df.assign(high_keepz=df["Keepz"] >= cutoff)
    geo = source.groupby(["location", "latitude", "longitude"], as_index=False).agg(
        employees=("employee_id", "size"), avg_risk=("attrition_risk_score", "mean"),
        avg_impact=("impact_score", "mean"), avg_keepz=("Keepz", "mean"),
        high_keepz=("high_keepz", "sum"),
    )
    highest = geo.nlargest(1, "avg_keepz").iloc[0]
    st.markdown('<div class="eyebrow">GEOGRAPHIC EXPOSURE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Where is Keepz concentrated?</h1>', unsafe_allow_html=True)
    st.caption("Low average Keepz is green; medium is amber; high is red.")

    cols = st.columns(3)
    cards = [
        ("Locations", str(len(geo)), "neutral", "Offices represented"),
        ("Average Keepz", f"{df['Keepz'].mean():.2f}", "bad", "Across visible offices"),
        ("Highest average Keepz", highest["location"], "bad", f"{highest['avg_keepz']:.2f}"),
    ]
    for col, card in zip(cols, cards):
        with col:
            metric(*card)
    left, right = st.columns([1.35, 1])
    with left:
        heading("Keepz by office", "Size = headcount · color = average Keepz")
        st.plotly_chart(geography_map(geo), use_container_width=True,
                        config={"displayModeBar": False})
    with right:
        heading("Office comparison", "Average Keepz")
        st.plotly_chart(location_exposure(geo), use_container_width=True,
                        config={"displayModeBar": False})
    heading("Location values", "Figures represented on the map")
    table = geo[["location", "employees", "avg_risk", "avg_impact", "avg_keepz", "high_keepz"]].copy()
    table[["avg_risk", "avg_impact", "avg_keepz"]] = table[
        ["avg_risk", "avg_impact", "avg_keepz"]].round(2)
    table.columns = ["Location", "Employees", "Average leave probability",
                     "Average company impact", "Average Keepz", "High-Keepz employees"]
    st.dataframe(table.sort_values("Average Keepz", ascending=False),
                 hide_index=True, use_container_width=True)


inject_css()
employees, correlations = load_data()
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Team"

with st.sidebar:
    st.markdown('<div class="brand"><span>◆</span> Keepz</div>', unsafe_allow_html=True)
    st.caption("Manager retention brief")
    page = st.radio("Navigation", ["Individual", "Team", "Geography"],
                    key="nav_page", label_visibility="collapsed")
    st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
    department = st.selectbox("Department", ["All departments"] + sorted(employees["department"].unique()))
    location = st.selectbox("Location", ["All locations"] + sorted(employees["location"].unique()))
    st.caption("Keepz prioritizes whom the organisation most needs to retain.")

filtered = employees.copy()
if department != "All departments":
    filtered = filtered[filtered["department"] == department]
if location != "All locations":
    filtered = filtered[filtered["location"] == location]

if filtered.empty:
    st.warning("No employees match these filters.")
elif page == "Individual":
    individual_view(filtered, correlations)
elif page == "Geography":
    geography_view(filtered)
else:
    team_view(filtered)
