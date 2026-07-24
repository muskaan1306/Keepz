"""Plotly chart factory functions with a shared visual language."""

import plotly.express as px
import plotly.graph_objects as go

from core.constants import AMBER, BLUE, GREEN, RED, RISK_COLORS, SLATE


def _layout(fig, height=330):
    fig.update_layout(
        height=height, margin=dict(l=20, r=20, t=35, b=20),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#45546C"),
        legend_title_text="", hoverlabel=dict(bgcolor="#102044", font_color="white"),
    )
    return fig


def team_trend(data):
    fig = px.line(data, x="month", y="keep_score", markers=True)
    fig.update_traces(line=dict(color=BLUE, width=3), marker=dict(size=8))
    fig.update_yaxes(range=[0, 100], title=None, gridcolor="#EDF1F7")
    fig.update_xaxes(title=None, tickformat="%b")
    return _layout(fig)


def risk_donut(employees):
    counts = employees["risk_level"].value_counts().rename_axis("risk").reset_index(name="employees")
    fig = px.pie(
        counts, names="risk", values="employees", hole=.68,
        color="risk", color_discrete_map=RISK_COLORS,
    )
    fig.update_traces(textinfo="value+label", sort=False)
    fig.add_annotation(text=f"<b>{len(employees)}</b><br><span>Team</span>", showarrow=False)
    return _layout(fig, 300)


def horizontal_bars(data, x, y, color=BLUE, height=320):
    colors = [RED if value >= 11 else AMBER if value >= 7 else GREEN for value in data[x]]
    fig = go.Figure(go.Bar(x=data[x], y=data[y], orientation="h", marker_color=colors))
    fig.update_xaxes(title=None, gridcolor="#EDF1F7")
    fig.update_yaxes(title=None)
    return _layout(fig, height)


def risk_matrix(employees):
    fig = px.scatter(
        employees, x="keep_score", y="business_impact", color="risk_level",
        size="priority_score", size_max=24, color_discrete_map=RISK_COLORS,
        hover_name="employee_name",
        hover_data={
            "role": True, "location": True, "keep_score": ":.1f",
            "business_impact": ":.1f", "monthly_change": ":+.1f",
            "priority_score": False, "risk_level": True,
        },
    )
    fig.add_vline(x=65, line_dash="dash", line_color="#AAB5C5")
    fig.add_hline(y=65, line_dash="dash", line_color="#AAB5C5")
    labels = [
        (35, 90, "Immediate Retention Priority", RED),
        (82, 90, "Protect and Develop", BLUE),
        (35, 38, "Watch Closely", AMBER),
        (82, 38, "Stable", GREEN),
    ]
    for x, y, text, color in labels:
        fig.add_annotation(x=x, y=y, text=f"<b>{text}</b>", showarrow=False, font=dict(color=color, size=12))
    fig.update_xaxes(range=[20, 100], title="Keep Score", gridcolor="#EDF1F7")
    fig.update_yaxes(range=[20, 105], title="Business Impact", gridcolor="#EDF1F7")
    return _layout(fig, 540)


def keep_gauge(score):
    color = RED if score < 55 else AMBER if score < 72 else GREEN
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font": {"size": 42, "color": "#102044"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0},
            "bar": {"color": color, "thickness": .28},
            "bgcolor": "#EDF1F7", "borderwidth": 0,
            "steps": [
                {"range": [0, 55], "color": "#FDECEC"},
                {"range": [55, 72], "color": "#FFF4DE"},
                {"range": [72, 100], "color": "#E6F6EF"},
            ],
        },
    ))
    return _layout(fig, 270)


def employee_trend(data):
    fig = px.line(data, x="month", y="keep_score", markers=True)
    fig.update_traces(line=dict(color=BLUE, width=3), marker=dict(size=9))
    fig.update_yaxes(range=[0, 100], title=None, gridcolor="#EDF1F7")
    fig.update_xaxes(title=None, tickformat="%b")
    return _layout(fig, 300)


def location_bubble(summary):
    fig = px.scatter(
        summary, x="location", y="average_keep_score", size="employees",
        color="at_risk", color_continuous_scale=["#BFD5FF", RED],
        hover_data=["employees", "at_risk", "top_driver"], size_max=42,
    )
    fig.update_yaxes(range=[35, 95], title="Average Keep Score", gridcolor="#EDF1F7")
    fig.update_xaxes(title=None)
    fig.update_coloraxes(colorbar_title="At risk")
    return _layout(fig, 390)
