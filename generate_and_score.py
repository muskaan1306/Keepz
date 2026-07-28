"""Generate demo employees, two logistic scores, and the Keepz value."""

import random
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


random.seed(42)
np.random.seed(42)
NUMBER_OF_EMPLOYEES = 80
fake = Faker("en_IN")
Faker.seed(42)

# Resolve outputs relative to this script instead of the caller's working directory.
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

hubs = {
    "Chennai": (13.0827, 80.2707),
    "Delhi": (28.6139, 77.2090),
    "Noida": (28.5355, 77.3910),
    "Gurgaon": (28.4595, 77.0266),
    "Kolkata": (22.5726, 88.3639),
    "Mumbai": (19.0760, 72.8777),
    "Navi Mumbai": (19.0330, 73.0297),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4867),
    "Bangalore": (12.9716, 77.5946),
}

location_weights = [10, 2, 12, 9, 1, 8, 3, 15, 18, 22]

roles_by_department = {
    "Engineering": [
        "Software Engineer", "Senior Software Engineer", "Lead Engineer",
        "Principal Engineer", "Cloud Engineer", "DevOps Engineer",
        "SRE Engineer", "Data Engineer", "Data Scientist", "AI Engineer",
        "QA Engineer", "Automation Test Engineer", "Engineering Manager",
        "Solution Architect", "Technical Architect",
    ],
    "Sales": [
        "Sales Executive", "Account Executive",
        "Business Development Representative", "Inside Sales Representative",
        "Sales Manager", "Senior Sales Manager", "Key Account Manager",
        "Enterprise Account Manager", "Regional Sales Manager", "Sales Director",
    ],
    "Marketing": [
        "Marketing Executive", "Marketing Specialist",
        "Content Marketing Specialist", "Digital Marketing Specialist",
        "SEO Specialist", "Product Marketing Manager", "Marketing Manager",
        "Brand Manager", "Growth Marketing Manager", "Marketing Director",
    ],
    "Finance": [
        "Finance Analyst", "Senior Finance Analyst", "Accounts Executive",
        "Accountant", "Senior Accountant", "Financial Controller",
        "Finance Manager", "Tax Specialist", "FP&A Manager", "Finance Director",
    ],
    "HR": [
        "HR Executive", "HR Generalist", "Talent Acquisition Specialist",
        "Recruiter", "Senior Recruiter", "HR Business Partner",
        "Learning & Development Specialist", "Compensation Analyst",
        "HR Manager", "HR Director",
    ],
    "Operations": [
        "Operations Executive", "Operations Analyst", "Business Analyst",
        "Project Coordinator", "Project Manager", "Program Manager",
        "Operations Manager", "Delivery Manager", "Senior Delivery Manager",
        "Operations Director",
    ],
    "Support": [
        "Technical Support Engineer", "Support Analyst",
        "Customer Support Executive", "Service Desk Analyst",
        "Application Support Engineer", "L2 Support Engineer",
        "L3 Support Engineer", "Support Team Lead", "Support Manager",
        "Customer Success Manager",
    ],
}

# The original notebook uses a 1-to-6 role hierarchy.
level_1 = {
    "Sales Executive", "Business Development Representative",
    "Inside Sales Representative", "Marketing Executive", "Accounts Executive",
    "HR Executive", "Operations Executive", "Customer Support Executive",
}
level_3 = {
    "Senior Software Engineer", "Senior Finance Analyst", "Senior Accountant",
    "Tax Specialist", "Senior Recruiter", "L2 Support Engineer",
}
level_4 = {
    "Lead Engineer", "HR Business Partner", "L3 Support Engineer",
    "Support Team Lead",
}
level_6 = {
    "Principal Engineer", "Sales Director", "Marketing Director",
    "Finance Director", "HR Director", "Operations Director",
}

manager_words = {
    "Manager", "Architect", "Controller", "Director",
}


def get_job_level(role):
    if role in level_1:
        return 1
    if role in level_3:
        return 3
    if role in level_4:
        return 4
    if role in level_6:
        return 6
    if any(word in role for word in manager_words):
        return 5
    return 2


high_demand_roles = {
    "Cloud Engineer": 5,
    "AI Engineer": 5,
    "Data Scientist": 5,
    "DevOps Engineer": 5,
    "SRE Engineer": 5,
    "Software Engineer": 4,
    "Data Engineer": 4,
}


def sigmoid(value):
    return 1 / (1 + np.exp(-value))


employees = []

for number in range(1, NUMBER_OF_EMPLOYEES + 1):
    # Employee detailsnam
    department = random.choice(list(roles_by_department))
    role = random.choice(roles_by_department[department])
    job_level = get_job_level(role)
    location = random.choices(
        list(hubs), weights=location_weights, k=1
    )[0]
    latitude, longitude = hubs[location]
    gender = random.choice(["M", "F"])
    age = random.randint(max(22, 20 + job_level * 3), 60)

    # Career details
    tenure_years = round(
        min(age - 20, max(0.5, np.random.gamma(2, 2))), 1
    )
    position_tenure = round(random.uniform(0.2, tenure_years), 1)
    time_since_joining_team = round(
        random.uniform(0, min(5, tenure_years)), 1
    )
    promotion_delay_months = int(
        min(60, max(6, round(6 + position_tenure * 8 + np.random.normal(0, 6))))
    )
    internal_job_applications = np.random.poisson(
        0.5 + promotion_delay_months / 30
    )

    # Workload is generated first because overtime affects work-life balance.
    workload = random.randint(1, 5)
    overtime_hours = random.randint(workload * 4, workload * 12)
    average_weekly_hours = round(40 + overtime_hours / 4, 1)
    client_escalation_count = np.random.poisson(
        max(0.2, workload - 0.5)
    )

    # Engagement details
    manager_relationship = round(random.uniform(1, 5), 1)
    work_life_balance = round(
        min(5, max(1, 4.8 - overtime_hours / 16 + np.random.normal(0, 0.45))),
        1,
    )
    engagement = round(
        min(
            5,
            max(
                1,
                0.5 * manager_relationship
                + 0.3 * work_life_balance
                + random.uniform(0.5, 1.5),
            ),
        ),
        1,
    )
    peer_recognition_count = np.random.poisson(
        max(0.5, 1 + engagement)
    )
    awards_received = random.choices(
        [0, 1, 2, 3],
        weights=[70, 18 + peer_recognition_count, 8, 2],
        k=1,
    )[0]

    # Compensation details
    compensation_gap = round(random.uniform(-25, 25), 1)
    # Positive compensation gap produces a generally higher salary percentile.
    salary_percentile = int(
        min(100, max(1, 50 + compensation_gap + np.random.normal(0, 10)))
    )

    # Mobility details
    distance_to_office_km = round(np.random.gamma(2, 8), 1)
    work_flexibility_score = random.randint(1, 5)
    remote_work_eligibility = random.choices(
        [0, 1], weights=[40, 60], k=1
    )[0]

    # Market demand and business impact details
    skill_criticality_score = high_demand_roles.get(
        role, random.randint(1, 5)
    )
    knowledge_risk_score = min(
        5, max(1, job_level + random.randint(-1, 1))
    )
    dependencies = max(
        0, int(np.random.normal(job_level * 3, 2))
    )
    client_criticality = min(
        5, max(1, job_level + random.randint(-1, 1))
    )
    specialised_skills = int(
        min(10, max(1, round(skill_criticality_score * 1.6 + np.random.normal(0, 1.2))))
    )
    owner_probability = min(
        0.75, 0.05 + 0.06 * job_level + 0.05 * client_criticality
    )
    critical_project_owner = int(random.random() < owner_probability)
    replacement_time_months = int(
        min(
            18,
            max(
                1,
                round(
                    job_level
                    + 0.8 * skill_criticality_score
                    + np.random.normal(0, 1)
                ),
            ),
        )
    )
    no_backup_weight = 15 + 5 * knowledge_risk_score
    succession_coverage = random.choices(
        ["Ready Successor", "Partial Backup", "No Backup"],
        weights=[35 - 3 * job_level, 40, no_backup_weight],
        k=1,
    )[0]
    performance_rating = random.choices(
        [2, 3, 4, 5], weights=[10, 50, 30, 10], k=1
    )[0]

    # Example historical outcomes used to train logistic regression.
    attrition_probability = sigmoid(
        -0.8
        + 0.045 * overtime_hours
        + 0.020 * max(0, overtime_hours - 30)
        + 0.025 * promotion_delay_months
        + 0.20 * internal_job_applications
        + 0.010 * distance_to_office_km
        - 0.35 * engagement
        - 0.25 * manager_relationship
        - 0.20 * work_life_balance
        - 0.020 * compensation_gap
        - 0.15 * work_flexibility_score
        - 0.15 * remote_work_eligibility
    )

    no_backup = 1 if succession_coverage == "No Backup" else 0
    impact_probability = sigmoid(
        -6.0
        + 0.35 * job_level
        + 0.35 * skill_criticality_score
        + 0.30 * knowledge_risk_score
        + 0.10 * dependencies
        + 0.30 * client_criticality
        + 0.10 * specialised_skills
        + 0.55 * critical_project_owner
        + 0.12 * replacement_time_months
        + 0.35 * no_backup
        + 0.20 * (performance_rating - 3)
    )

    employees.append({
        "employee_id": f"E_{number:05d}",
        "employee_name": fake.unique.name(),
        "role": role,
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "department": department,
        "job_level": job_level,
        "gender": gender,
        "age": age,
        "tenure_years": tenure_years,
        "position_tenure": position_tenure,
        "time_since_joining_team": time_since_joining_team,
        "promotion_delay_months": promotion_delay_months,
        "internal_job_applications": internal_job_applications,
        "manager_relationship": manager_relationship,
        "engagement": engagement,
        "work_life_balance": work_life_balance,
        "peer_recognition_count": peer_recognition_count,
        "awards_received": awards_received,
        "workload": workload,
        "overtime_hours": overtime_hours,
        "average_weekly_hours": average_weekly_hours,
        "client_escalation_count": client_escalation_count,
        "salary_percentile": salary_percentile,
        "compensation_gap": compensation_gap,
        "distance_to_office_km": distance_to_office_km,
        "work_flexibility_score": work_flexibility_score,
        "remote_work_eligibility": remote_work_eligibility,
        "skill_criticality_score": skill_criticality_score,
        "knowledge_risk_score": knowledge_risk_score,
        "dependencies": dependencies,
        "client_criticality": client_criticality,
        "specialised_skills": specialised_skills,
        "critical_project_owner": critical_project_owner,
        "replacement_time_months": replacement_time_months,
        "succession_coverage": succession_coverage,
        "performance_rating": performance_rating,
        # Deterministic demo labels prevent random contradictions in 80 rows.
        "attrition_label": int(attrition_probability >= 0.30),
        "impact_label": int(impact_probability >= 0.50),
    })


df = pd.DataFrame(employees)

# Each model uses only features that logically relate to its outcome. This is
# more stable than giving dozens of sparse role/location columns to 80 records.
attrition_features = [
    "tenure_years", "position_tenure", "promotion_delay_months",
    "internal_job_applications", "manager_relationship", "engagement",
    "work_life_balance", "workload", "overtime_hours",
    "client_escalation_count", "compensation_gap", "salary_percentile",
    "distance_to_office_km", "work_flexibility_score",
    "remote_work_eligibility",
]

impact_features = [
    "job_level", "performance_rating", "skill_criticality_score",
    "knowledge_risk_score", "dependencies", "client_criticality",
    "specialised_skills", "critical_project_owner",
    "replacement_time_months", "succession_coverage",
]


def create_score(label_column, score_column, feature_columns):
    """Fit one model and convert its probability into a score from 0 to 100."""
    categorical_features = [
        column for column in feature_columns
        if df[column].dtype == "object"
    ]
    numeric_features = [
        column for column in feature_columns
        if column not in categorical_features
    ]
    preprocessing = ColumnTransformer([
        ("numeric", StandardScaler(), numeric_features),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
    ])
    model = Pipeline([
        ("prepare_features", preprocessing),
        (
            "logistic_regression",
            LogisticRegression(max_iter=1000, C=0.35),
        ),
    ])
    model.fit(df[feature_columns], df[label_column])
    probability = model.predict_proba(df[feature_columns])[:, 1]
    # Two decimal places prevent a small probability displaying as literal zero.
    df[score_column] = (probability * 100).round(2)


create_score(
    "attrition_label", "attrition_risk_score", attrition_features
)
create_score("impact_label", "impact_score", impact_features)

# Keepz is an unbounded retention-priority value, not a probability.
# Converting attrition probability to odds gives a 0-to-infinity scale.
# Exit impact then multiplies that urgency by a value between 1 and 5.
attrition_probability = (df["attrition_risk_score"] / 100).clip(
    lower=0.000001, upper=0.999999
)
attrition_odds = attrition_probability / (1 - attrition_probability)
impact_multiplier = 1 + 4 * (df["impact_score"] / 100)
df["Keepz"] = (attrition_odds * impact_multiplier).round(2)

correlations = df.select_dtypes(include="number").corr().round(2)

employee_scores_path = DATA_DIR / "employee_scores.csv"
correlations_path = DATA_DIR / "feature_correlations.csv"

df.to_csv(employee_scores_path, index=False)
correlations.to_csv(correlations_path)

print("Dataset shape:", df.shape)
print("Attrition model features:", len(attrition_features))
print("Impact model features:", len(impact_features))
print("\nScore summary:")
print(
    df[
        ["Keepz", "impact_score", "attrition_risk_score"]
    ].describe().round(2)
)
print(f"\nCreated {employee_scores_path}")
print(f"Created {correlations_path}")
