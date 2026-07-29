from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

BLUE, GREEN, RED, AMBER, ORANGE = "#0070AD", "#178C3D", "#E30021", "#FFD068", "#FF9C29"
INK, MUTED, GRID, AXIS = "#272936", "#5B6472", "#D8DDE3", "#334155"


def _layout(fig: go.Figure, height: int, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=margin or {"l": 35, "r": 20, "t": 25, "b": 35},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": INK, "size": 12},
        hoverlabel={"bgcolor": "white", "font_color": INK},
    )
    return fig


def _keepz_colorscale(
    thresholds: tuple[float, float, float] | None = None
) -> tuple[list[list[float | str]], float]:
    maximum = 80
    return [
        [0, GREEN],
        [.25, AMBER],
        [.50, ORANGE],
        [.6875, RED],
        [1, RED],
    ], maximum


def probability_gauge(value: float, title: str, category: str,
                      high_is_bad: bool = True) -> go.Figure:
    percentage = value * 100
    if high_is_bad:
        color = RED if value >= .50 else AMBER if value >= .25 else GREEN
    else:
        color = GREEN if value >= .55 else AMBER if value >= .30 else RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={"suffix": "%", "font": {"size": 29, "color": color}},
        title={"text": title, "font": {"size": 13, "color": MUTED}},
        gauge={
            "axis": {"range": [0, 100], "visible": False},
            "bar": {"color": color, "thickness": .25},
            "bgcolor": "#EEF0F3",
            "borderwidth": 0,
        },
        domain={"x": [.06, .94], "y": [.22, 1]},
    ))
    fig.add_annotation(
        x=.5, y=.06, xref="paper", yref="paper", showarrow=False,
        text=f"<b>{category.upper()}</b>", font={"size": 13, "color": color},
    )
    return _layout(fig, 220, {"l": 12, "r": 12, "t": 12, "b": 4})


def attrition_criticality_scatter(
    df: pd.DataFrame, keepz_thresholds: tuple[float, float, float]
) -> go.Figure:
    x = df["attrition_probability"] * 100
    y = df["criticality_probability"] * 100
    custom = df[["employee_name", "role", "department", "Keepz"]].to_numpy()
    colorscale, color_max = _keepz_colorscale(keepz_thresholds)
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="markers", customdata=custom,
        marker={
            "size": 12,
            "color": df["Keepz"],
            "colorscale": colorscale,
            "cmin": 0,
            "cmax": color_max,
            "colorbar": {"title": {"text": "Keepz"}, "thickness": 14},
            "line": {"color": "white", "width": 1},
            "opacity": .85,
        },
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}"
            "<br>Attrition probability: <b>%{x:.1f}%</b>"
            "<br>Criticality probability: <b>%{y:.1f}%</b>"
            "<br>Keepz: <b>%{customdata[3]:.2f}</b><extra></extra>"
        ),
    ))
    fig.add_vline(x=50, line_dash="dash", line_color="#AEB4BC")
    fig.add_hline(y=50, line_dash="dash", line_color="#AEB4BC")
    labels = [
        (78, 77, "RETENTION ACTION", RED),
        (22, 77, "CRITICAL & STABLE", GREEN),
        (78, 9, "EXIT READINESS", AMBER),
        (22, 9, "MONITOR", MUTED),
    ]
    for lx, ly, text, color in labels:
        fig.add_annotation(x=lx, y=ly, text=f"<b>{text}</b>", showarrow=False,
                           font={"size": 10, "color": color})
    fig.update_xaxes(
        range=[0, 82], title="Attrition probability", gridcolor=GRID,
        title_font={"color": AXIS}, tickfont={"color": AXIS},
    )
    fig.update_yaxes(
        range=[0, 82], title="Criticality probability", gridcolor=GRID,
        title_font={"color": AXIS}, tickfont={"color": AXIS},
    )
    return _layout(fig, 455, {"l": 65, "r": 100, "t": 30, "b": 60})


def risk_distribution(df: pd.DataFrame) -> go.Figure:
    probability = df["attrition_probability"]
    bands = pd.cut(probability, [0, .25, .50, 1],
                   labels=["Low", "Medium", "High"], include_lowest=True)
    counts = bands.value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=.6,
        sort=False,
        marker={"colors": [RED, AMBER, GREEN],
                "line": {"color": "white", "width": 2}},
        textinfo="label+value",
        textposition="inside",
        insidetextfont={"color": "white", "size": 12},
        hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{len(df)}</b><br><span style='font-size:10px'>employees</span>",
        showarrow=False,
    )
    return _layout(fig, 330, {"l": 10, "r": 10, "t": 20, "b": 20})


def feature_importance_chart(importance: pd.DataFrame, model: str) -> go.Figure:
    labels = {
        "overtime_hours_month": "Monthly overtime",
        "work_life_balance": "Work-life balance",
        "workload_score": "Workload",
        "engagement_score": "Engagement",
        "promotion_wait_months": "Promotion wait",
        "position_tenure_years": "Position tenure",
        "internal_applications_12m": "Internal applications",
        "manager_rating": "Manager rating",
        "flexible_work_score": "Work flexibility",
        "job_level": "Job level",
        "performance_rating": "Performance",
        "direct_reports": "Direct reports",
        "active_projects": "Active projects",
        "client_facing": "Client facing",
        "succession_ready": "Successor ready",
        "replacement_time_months": "Replacement time",
        "tenure_years": "Tenure",
    }
    selected = (
        importance[importance["model"] == model]
        .nlargest(7, "importance")
        .sort_values("importance")
    )
    fig = go.Figure(go.Bar(
        x=selected["importance"] * 100,
        y=selected["feature"].map(labels).fillna(selected["feature"]),
        orientation="h",
        marker_color=BLUE,
        text=[f"{value:.1f}%" for value in selected["importance"] * 100],
        textposition="outside",
        hovertemplate="%{y}<br>Model importance: <b>%{x:.1f}%</b><extra></extra>",
    ))
    fig.update_xaxes(
        range=[0, max(30, float(selected["importance"].max() * 115))],
        title="Share of Random Forest importance",
        gridcolor=GRID,
        title_font={"color": AXIS},
        tickfont={"color": AXIS},
    )
    fig.update_yaxes(showgrid=False, tickfont={"color": AXIS})
    return _layout(fig, 340, {"l": 10, "r": 40, "t": 10, "b": 45})


def geography_map(
    geo: pd.DataFrame, keepz_thresholds: tuple[float, float, float]
) -> go.Figure:
    custom = geo[
        ["employees", "avg_attrition", "avg_criticality", "avg_keepz", "action_cases"]
    ].to_numpy()
    colorscale, high = _keepz_colorscale(keepz_thresholds)
    fig = go.Figure(go.Scattergeo(
        lon=geo["longitude"],
        lat=geo["latitude"],
        text=geo["location"],
        customdata=custom,
        mode="markers+text",
        textposition="top center",
        marker={
            "size": 12 + geo["employees"] * .6,
            "color": geo["avg_keepz"],
            "colorscale": colorscale,
            "cmin": 0,
            "cmax": high,
            "colorbar": {"title": {"text": "Avg Keepz"}, "thickness": 13},
            "line": {"color": "white", "width": 2},
        },
        hovertemplate=(
            "<b>%{text}</b><br>Employees: %{customdata[0]}"
            "<br>Average attrition: %{customdata[1]:.1%}"
            "<br>Average criticality: %{customdata[2]:.1%}"
            "<br>Average Keepz: <b>%{customdata[3]:.2f}</b>"
            "<br>Retention-action cases: %{customdata[4]}<extra></extra>"
        ),
    ))
    fig.update_geos(
        scope="asia",
        projection_type="mercator",
        center={"lat": 21, "lon": 79},
        lataxis_range=[7, 36],
        lonaxis_range=[67, 96],
        showland=True,
        landcolor="#F3F6F8",
        showcountries=True,
        countrycolor="#CBCBCB",
        showcoastlines=True,
        coastlinecolor="#CBCBCB",
        showframe=False,
        bgcolor="white",
    )
    return _layout(fig, 440, {"l": 0, "r": 0, "t": 0, "b": 0})


def location_comparison(
    geo: pd.DataFrame, keepz_thresholds: tuple[float, float, float]
) -> go.Figure:
    geo = geo.sort_values("avg_keepz")
    colorscale, high = _keepz_colorscale(keepz_thresholds)
    fig = go.Figure(go.Bar(
        x=geo["avg_keepz"],
        y=geo["location"],
        orientation="h",
        marker={
            "color": geo["avg_keepz"],
            "colorscale": colorscale,
            "cmin": 0,
            "cmax": high,
        },
        hovertemplate="%{y}<br>Average Keepz: <b>%{x:.2f}</b><extra></extra>",
    ))
    fig.update_xaxes(
        gridcolor=GRID, title="Average Keepz",
        title_font={"color": AXIS}, tickfont={"color": AXIS},
    )
    fig.update_yaxes(showgrid=False, tickfont={"color": AXIS})
    return _layout(fig, 440, {"l": 10, "r": 35, "t": 20, "b": 45})
