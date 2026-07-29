"""Generate a reproducible HR dataset and Random Forest retention scores."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker
from sklearn.ensemble import RandomForestClassifier


SEED = 42
NUMBER_OF_EMPLOYEES = 80
MIN_PROBABILITY = 0.05
MAX_PROBABILITY = 0.80

random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HUBS = {
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
LOCATION_WEIGHTS = [9, 3, 8, 8, 3, 9, 3, 16, 16, 25]

# Roles and levels are normally available from an HRIS job catalogue.
ROLES = {
    "Engineering": [
        ("Software Engineer", 2), ("Senior Software Engineer", 3),
        ("Lead Engineer", 4), ("Engineering Manager", 5),
        ("Solution Architect", 5),
    ],
    "Sales": [
        ("Sales Executive", 1), ("Account Executive", 2),
        ("Key Account Manager", 4), ("Sales Manager", 5),
    ],
    "Marketing": [
        ("Marketing Executive", 1), ("Marketing Specialist", 2),
        ("Marketing Manager", 5),
    ],
    "Finance": [
        ("Finance Analyst", 2), ("Senior Finance Analyst", 3),
        ("Financial Controller", 5), ("Finance Manager", 5),
    ],
    "HR": [
        ("HR Executive", 1), ("Recruiter", 2),
        ("HR Business Partner", 4), ("HR Manager", 5),
    ],
    "Operations": [
        ("Operations Analyst", 2), ("Project Manager", 4),
        ("Program Manager", 5), ("Delivery Manager", 5),
    ],
    "Support": [
        ("Support Analyst", 2), ("L2 Support Engineer", 3),
        ("Support Team Lead", 4), ("Support Manager", 5),
    ],
}


def clamp(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def generate_employee(number: int) -> dict:
    department = random.choice(list(ROLES))
    role, job_level = random.choice(ROLES[department])
    location = random.choices(list(HUBS), weights=LOCATION_WEIGHTS, k=1)[0]
    latitude, longitude = HUBS[location]

    age = random.randint(max(22, 19 + job_level * 4), 60)
    tenure_years = round(clamp(np.random.gamma(2.2, 2.1), .5, age - 20), 1)
    position_tenure_years = round(random.uniform(.2, max(.2, tenure_years)), 1)
    promotion_wait_months = int(clamp(
        8 + position_tenure_years * 7 + np.random.normal(0, 5), 3, 48
    ))
    internal_applications_12m = int(np.random.poisson(
        .25 + max(0, promotion_wait_months - 18) / 24
    ))

    workload_score = random.choices([1, 2, 3, 4, 5], [8, 23, 36, 24, 9], k=1)[0]
    overtime_hours_month = int(clamp(
        np.random.normal(max(0, workload_score - 1) * 7, 5), 0, 45
    ))
    manager_rating = round(clamp(np.random.normal(3.4, .8), 1, 5), 1)
    work_life_balance = round(clamp(
        4.5 - overtime_hours_month / 18 - .18 * (workload_score - 3)
        + np.random.normal(0, .35), 1, 5
    ), 1)
    engagement_score = round(clamp(
        .48 * manager_rating + .38 * work_life_balance
        + np.random.normal(.5, .35), 1, 5
    ), 1)
    flexible_work_score = random.choices([1, 2, 3, 4, 5], [8, 16, 31, 29, 16], k=1)[0]
    absence_days_12m = int(clamp(np.random.poisson(
        2 + max(0, 3 - engagement_score) * 1.5
    ), 0, 15))
    performance_rating = random.choices([2, 3, 4, 5], [8, 49, 34, 9], k=1)[0]

    client_facing = int(
        department in {"Sales", "Operations", "Support"}
        or "Architect" in role or random.random() < .25
    )
    direct_reports = (
        random.randint(2, 12) if job_level >= 4 and random.random() < .7 else 0
    )
    active_projects = int(clamp(np.random.poisson(
        1.2 + .25 * job_level + .5 * client_facing
    ), 1, 6))
    succession_ready = int(
        job_level >= 4 and random.random() < .28
    )
    replacement_time_months = int(round(clamp(
        .5 + .35 * job_level + .25 * client_facing
        + .15 * active_projects - .4 * succession_ready
        + np.random.normal(0, .3), 1, 3
    )))

    return {
        "employee_id": f"E_{number:05d}",
        "employee_name": fake.unique.name(),
        "role": role,
        "department": department,
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "age": age,
        "job_level": job_level,
        "tenure_years": tenure_years,
        "position_tenure_years": position_tenure_years,
        "promotion_wait_months": promotion_wait_months,
        "internal_applications_12m": internal_applications_12m,
        "manager_rating": manager_rating,
        "engagement_score": engagement_score,
        "work_life_balance": work_life_balance,
        "workload_score": workload_score,
        "overtime_hours_month": overtime_hours_month,
        "absence_days_12m": absence_days_12m,
        "flexible_work_score": flexible_work_score,
        "performance_rating": performance_rating,
        "client_facing": client_facing,
        "direct_reports": direct_reports,
        "active_projects": active_projects,
        "succession_ready": succession_ready,
        "replacement_time_months": replacement_time_months,
    }


df = pd.DataFrame(
    generate_employee(number) for number in range(1, NUMBER_OF_EMPLOYEES + 1)
)

# These deterministic synthetic outcomes make the relationships intentional.
# In production, replace them with recorded voluntary exits and an agreed
# critical-role flag from historical HR data.
attrition_signal = (
    .075 * df["overtime_hours_month"]
    + .48 * df["workload_score"]
    + .035 * df["promotion_wait_months"]
    + .65 * df["internal_applications_12m"]
    + .09 * df["absence_days_12m"]
    - .72 * df["engagement_score"]
    - .58 * df["manager_rating"]
    - .45 * df["work_life_balance"]
    - .38 * df["flexible_work_score"]
)
criticality_signal = (
    .72 * df["job_level"]
    + .52 * df["performance_rating"]
    + .16 * df["direct_reports"]
    + .30 * df["active_projects"]
    + .62 * df["client_facing"]
    + .16 * df["replacement_time_months"]
    + .05 * df["tenure_years"]
    - 1.0 * df["succession_ready"]
)

# Predefined binary outcomes: top 30% attrition signal and top 45% criticality.
df["attrition_label"] = (
    attrition_signal >= attrition_signal.quantile(.70)
).astype(int)
df["criticality_label"] = (
    criticality_signal >= criticality_signal.quantile(.55)
).astype(int)

ATTRITION_FEATURES = [
    "tenure_years", "position_tenure_years", "promotion_wait_months",
    "internal_applications_12m", "manager_rating", "engagement_score",
    "work_life_balance", "workload_score", "overtime_hours_month",
    "absence_days_12m", "flexible_work_score",
]
CRITICALITY_FEATURES = [
    "job_level", "tenure_years", "performance_rating", "client_facing",
    "direct_reports", "active_projects", "succession_ready",
    "replacement_time_months",
]


def train_probability_model(
    features: list[str], label: str, probability_column: str
) -> tuple[RandomForestClassifier, pd.DataFrame]:
    model = RandomForestClassifier(
        n_estimators=350,
        max_depth=4,
        min_samples_leaf=4,
        max_features="sqrt",
        class_weight="balanced",
        random_state=SEED,
    )
    model.fit(df[features], df[label])
    raw_probability = model.predict_proba(df[features])[:, 1]
    # Shrink rather than merely clip probabilities into the realistic 5%-80%
    # demonstration interval, preventing implausible 99% predictions.
    bounded_probability = (
        MIN_PROBABILITY
        + (MAX_PROBABILITY - MIN_PROBABILITY) * raw_probability
    )
    df[probability_column] = bounded_probability.round(3)
    importance = pd.DataFrame({
        "model": probability_column,
        "feature": features,
        "importance": model.feature_importances_,
    })
    return model, importance


_, attrition_importance = train_probability_model(
    ATTRITION_FEATURES, "attrition_label", "attrition_probability"
)
_, criticality_importance = train_probability_model(
    CRITICALITY_FEATURES, "criticality_label", "criticality_probability"
)

df["attrition_prediction"] = np.where(
    df["attrition_probability"] >= .50, "Likely to leave", "Likely to stay"
)
df["criticality_prediction"] = np.where(
    df["criticality_probability"] >= .50, "Critical", "Non-critical"
)

# Keepz is an importance-to-retain score, not a probability. Criticality is
# always counted, while attrition probability amplifies urgent retention need.
df["Keepz"] = (
    100
    * (
        0.7 * df["criticality_probability"] * df["attrition_probability"]
        + 0.3 * df["criticality_probability"]
    )
).round(2)

feature_importance = pd.concat(
    [attrition_importance, criticality_importance], ignore_index=True
)
feature_importance["importance"] = feature_importance["importance"].round(4)

employee_scores_path = DATA_DIR / "employee_scores.csv"
feature_importance_path = DATA_DIR / "feature_importance.csv"
df.to_csv(employee_scores_path, index=False)
feature_importance.to_csv(feature_importance_path, index=False)

print("Dataset shape:", df.shape)
print("Attrition outcomes:", df["attrition_label"].value_counts().to_dict())
print("Criticality outcomes:", df["criticality_label"].value_counts().to_dict())
print("\nScore summary:")
print(df[[
    "attrition_probability", "criticality_probability", "Keepz"
]].describe().round(3))
print(f"\nCreated {employee_scores_path}")
print(f"Created {feature_importance_path}")
