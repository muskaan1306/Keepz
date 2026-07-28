from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

BLUE, GREEN, RED, AMBER, YELLOW = "#0070AD", "#178C3D", "#E30021", "#FF9C29", "#FFD068"
INK, MUTED, GRID = "#272936", "#5B6472", "#E2E4E8"


def _layout(fig: go.Figure, height: int, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height, margin=margin or {"l": 35, "r": 20, "t": 25, "b": 35},
        paper_bgcolor="white", plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": INK, "size": 12},
        hoverlabel={"bgcolor": "white", "font_color": INK},
    )
    return fig


def score_gauge(value: float, title: str, category: str,
                good_when_high: bool | None = True) -> go.Figure:
    if good_when_high is None:
        color = BLUE
    else:
        good = value >= 60 if good_when_high else value < 20
        bad = value < 35 if good_when_high else value >= 50
        color = GREEN if good else RED if bad else AMBER
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        number={"suffix": "/100", "font": {"size": 29, "color": color}},
        title={"text": title, "font": {"size": 13, "color": MUTED}},
        gauge={"axis": {"range": [0, 100], "visible": False},
               "bar": {"color": color, "thickness": .25},
               "bgcolor": "#EEF0F3", "borderwidth": 0},
        domain={"x": [.06, .94], "y": [.22, 1]},
    ))
    fig.add_annotation(x=.5, y=.06, xref="paper", yref="paper", showarrow=False,
                       text=f"<b>{category.upper()}</b>",
                       font={"size": 13, "color": color})
    return _layout(fig, 220, {"l": 12, "r": 12, "t": 12, "b": 4})


def risk_impact_scatter(df: pd.DataFrame) -> go.Figure:
    custom = df[["employee_name", "role", "department", "Keepz"]].to_numpy()
    color_cap = max(float(df["Keepz"].quantile(.95)), .01)
    fig = go.Figure(go.Scatter(
        x=df["attrition_risk_score"], y=df["impact_score"], mode="markers",
        customdata=custom,
        marker={
            "size": 11, "color": df["Keepz"], "opacity": .84,
            "colorscale": [[0, GREEN], [.5, AMBER], [1, RED]],
            "cmin": 0, "cmax": color_cap,
            "colorbar": {
                "title": {"text": "Keepz<br>(to P95)", "side": "right"},
                "thickness": 14, "len": .74, "y": .5,
            },
            "line": {"color": "white", "width": 1},
        },
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}"
            "<br>Leave probability: <b>%{x:.2f}</b>"
            "<br>Company impact: <b>%{y:.2f}</b>"
            "<br>Keepz: <b>%{customdata[3]:.2f}</b><extra></extra>"
        ),
    ))
    fig.add_vline(x=50, line_dash="dash", line_color="#CBCBCB")
    fig.add_hline(y=70, line_dash="dash", line_color="#CBCBCB")
    fig.add_annotation(x=98, y=98, text="<b>PRIORITY ZONE</b>", showarrow=False,
                       xanchor="right", font={"color": RED})
    fig.update_xaxes(range=[0, 100], title="Leave probability", gridcolor=GRID, zeroline=False)
    fig.update_yaxes(range=[0, 100], title="Company impact", gridcolor=GRID, zeroline=False)
    return _layout(fig, 455, {"l": 65, "r": 105, "t": 35, "b": 65})


def risk_distribution(df: pd.DataFrame) -> go.Figure:
    bands = pd.cut(df["attrition_risk_score"], [-.01, 20, 50, 100],
                   labels=["Low", "Medium", "High"], include_lowest=True)
    counts = bands.value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=.6, sort=False,
        marker={"colors": [RED, AMBER, GREEN], "line": {"color": "white", "width": 2}},
        textinfo="label+value", textposition="inside",
        insidetextfont={"color": "white", "size": 12},
        hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{len(df)}</b><br><span style='font-size:10px'>employees</span>",
                       showarrow=False)
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode="show")
    return _layout(fig, 330, {"l": 10, "r": 10, "t": 20, "b": 20})


def feature_evidence_chart(df: pd.DataFrame) -> go.Figure:
    labels = {
        "overtime_hours": "Overtime", "work_life_balance": "Work-life<br>balance",
        "workload": "Workload", "engagement": "Engagement",
        "client_escalation_count": "Client<br>escalations",
        "work_flexibility_score": "Work<br>flexibility",
        "manager_relationship": "Manager<br>relationship",
    }
    leave, stay = df[df["attrition_label"] == 1], df[df["attrition_label"] == 0]
    if leave.empty or stay.empty:
        fig = go.Figure()
        fig.add_annotation(
            x=.5, y=.5, xref="paper", yref="paper", showarrow=False,
            text="Both predicted leavers and stayers are needed for this comparison.",
            font={"color": MUTED},
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return _layout(fig, 330)
    features = list(labels)
    x_labels = [labels[f] for f in features]
    normalized = {}
    raw = {}
    for cohort_name, cohort in [("Predicted to leave", leave), ("Predicted to stay", stay)]:
        normalized[cohort_name], raw[cohort_name] = [], []
        for feature in features:
            minimum, maximum = float(df[feature].min()), float(df[feature].max())
            mean = float(cohort[feature].mean())
            normalized[cohort_name].append(
                0 if maximum == minimum else (mean - minimum) / (maximum - minimum) * 100
            )
            raw[cohort_name].append(mean)
    fig = go.Figure()
    for name, color in [("Predicted to leave", RED), ("Predicted to stay", GREEN)]:
        fig.add_trace(go.Bar(
            name=name, x=x_labels, y=normalized[name], marker_color=color,
            customdata=raw[name], text=[f"{value:.0f}" for value in normalized[name]],
            textposition="outside",
            hovertemplate=(
                f"<b>{name}</b><br>%{{x}}"
                "<br>Normalized average: %{y:.1f}%"
                "<br>Raw average: %{customdata:.1f}<extra></extra>"
            ),
        ))
    fig.update_layout(
        barmode="group",
        legend={"orientation": "h", "x": .5, "xanchor": "center", "y": 1.16},
    )
    fig.update_xaxes(showgrid=False, tickfont={"size": 10})
    fig.update_yaxes(range=[0, 112], color=INK, title="Average position in feature range (%)",
                     gridcolor=GRID, zeroline=False)
    return _layout(fig, 360, {"l": 55, "r": 15, "t": 50, "b": 65})


def geography_map(geo: pd.DataFrame) -> go.Figure:
    custom = geo[["employees", "avg_risk", "avg_keepz", "high_keepz"]].to_numpy()
    fig = go.Figure(go.Scattergeo(
        lon=geo["longitude"], lat=geo["latitude"], text=geo["location"],
        customdata=custom, mode="markers+text", textposition="top center",
        marker={
            "size": 12 + geo["employees"] * .55, "color": geo["avg_keepz"],
            "colorscale": [[0, GREEN], [.5, AMBER], [1, RED]],
            "cmin": float(geo["avg_keepz"].min()),
            "cmax": max(float(geo["avg_keepz"].max()), .01),
            "colorbar": {"title": {"text": "Avg Keepz"}, "thickness": 13},
            "line": {"color": "white", "width": 2},
        },
        hovertemplate=(
            "<b>%{text}</b><br>Employees: %{customdata[0]}"
            "<br>Average leave probability: %{customdata[1]:.2f}"
            "<br>Average Keepz: <b>%{customdata[2]:.2f}</b>"
            "<br>High-Keepz employees: %{customdata[3]}<extra></extra>"
        ),
    ))
    fig.update_geos(
        scope="asia", projection_type="mercator", center={"lat": 21, "lon": 79},
        lataxis_range=[7, 36], lonaxis_range=[67, 96], showland=True,
        landcolor="#F3F6F8", showcountries=True, countrycolor="#CBCBCB",
        showcoastlines=True, coastlinecolor="#CBCBCB", showframe=False, bgcolor="white",
    )
    return _layout(fig, 440, {"l": 0, "r": 0, "t": 0, "b": 0})


def location_exposure(geo: pd.DataFrame) -> go.Figure:
    geo = geo.sort_values("avg_keepz")
    fig = go.Figure(go.Bar(
        x=geo["avg_keepz"], y=geo["location"], orientation="h",
        marker={"color": geo["avg_keepz"],
                "colorscale": [[0, GREEN], [.5, AMBER], [1, RED]],
                "cmin": float(geo["avg_keepz"].min()),
                "cmax": max(float(geo["avg_keepz"].max()), .01)},
        text=[f"<b>{x:.2f}</b>" for x in geo["avg_keepz"]], textposition="inside",
        textfont={"color": "white", "size": 12},
        hovertemplate="%{y}<br>Average Keepz: <b>%{x:.2f}</b><extra></extra>",
    ))
    fig.update_xaxes(gridcolor=GRID, title="Average Keepz")
    fig.update_yaxes(showgrid=False)
    return _layout(fig, 440, {"l": 10, "r": 35, "t": 20, "b": 45})
