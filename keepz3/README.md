# Keep — Attrition Risk Dashboard

A polished Streamlit dashboard for managers to monitor retention risk across a
fictional 15-person team. All scores are deterministic and rule-based; no
machine-learning model is used.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Scoring

Keep Score is `100 - weighted attrition risk`. Risk inputs include overtime,
promotion delay, engagement, workload, compensation gap, manager relationship,
and recent score momentum. Business Impact uses seniority, team dependencies,
client criticality, specialised skills, critical-project ownership, and
replacement time. Exact weights and thresholds live in `core/constants.py`.

Colors are consistent throughout: red means risk, amber means watch, green
means healthy, and blue is the product/navigation color.
