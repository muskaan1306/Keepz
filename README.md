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
Keepz = 100 * (0.7 * criticality_probability * attrition_probability
        + 0.3 * criticality_probability)
```

Keepz is an importance-to-retain score, not a probability. Criticality is
always counted because a critical employee matters even when their attrition
risk is currently low. Attrition probability then amplifies the score so that
critical employees who are more likely to leave rise to the top of the manager's
attention list.

Color bands:

- 0-20: green
- 20-40: amber
- 40-55: orange
- 55+: red

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
