# Keepz

Keepz is a Streamlit decision-support prototype for employee retention. It uses
two Random Forest classifiers:

- `attrition_probability`: likelihood of attrition, bounded to 0.05–0.80.
- `criticality_probability`: likelihood that the employee is business-critical,
  bounded to 0.05–0.80.

The binary training outcomes are predefined for the reproducible synthetic
demo. In production they must be replaced with recorded voluntary exits and an
agreed historical critical-role label.

The dashboard predictions apply a 50% threshold to the two model
probabilities. Employees at or above 50% on both are retention-action cases.

## Keepz formula

```text
Keepz = criticality_probability / attrition_probability
```

Keepz is a ratio, not a probability. A higher value means criticality is high
relative to attrition probability. Immediate retention action is identified
separately by employees who have both high attrition and high criticality.

## Reproducible fields

The 80-row demo uses fields that can normally be obtained from HRIS,
engagement, time, performance, staffing, and succession systems:

- Role, department, location, age, level, and tenure
- Position tenure, promotion wait, and internal applications
- Manager rating, engagement, work-life balance, workload, and flexibility
- Monthly overtime and absence
- Performance, client-facing status, direct reports, and active projects
- Successor readiness and historical replacement time

Replacement time is constrained to one–three months in the demonstration.

## Run

```powershell
pip install -r requirements.txt
python generate_and_score.py
streamlit run app.py
```

The generator writes:

- `data/employee_scores.csv`
- `data/feature_importance.csv`
