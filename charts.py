"""Plotly chart builders for the resilience matrix prototype."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from synthetic_data import GAP_CATEGORIES, INITIATIVES, REAF_COMPONENTS


CHART_TEMPLATE = "plotly_white"

SCORED_INDICATORS = [
    ("reaf_composite", "REAF Composite"),
    ("building_condition_score", "Building Condition"),
    ("utility_availability_score", "Utility Availability"),
    ("smart_meter_progress", "Smart Meter"),
    ("microgrid_progress", "Microgrid"),
    ("backup_power_progress", "Backup Power"),
]

REAF_SMALL_MULTIPLES = [(field, field.replace("reaf_", "").replace("_", " ").upper()) for field in REAF_COMPONENTS]
REAF_LABELS = [
    ("reaf_r1_a", "R1a"),
    ("reaf_r1_b", "R1b"),
    ("reaf_r2_a", "R2a"),
    ("reaf_r2_b", "R2b"),
    ("reaf_r3_a", "R3a"),
    ("reaf_r3_b", "R3b"),
    ("reaf_r4_a", "R4a"),
    ("reaf_r4_b", "R4b"),
    ("reaf_r5_a", "R5a"),
    ("reaf_r5_b", "R5b"),
]

COUNT_DIMENSIONS = {
    "hierarchy_level": "Hierarchy Level",
    "majcom": "MAJCOM",
    "installation": "Installation",
    "mission": "Mission",
    "gap_category": "Infrastructure Category",
    "eligibility": "Funding Eligibility",
}


def _score_band(score: float | int | None) -> str:
    if score is None or pd.isna(score):
        return "No data"
    if score < 40:
        return "Low"
    if score < 70:
        return "Mid"
    return "High"


def _empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        height=310,
        margin=dict(l=42, r=18, t=48, b=42),
        annotations=[dict(text="No rows available for this chart state", x=0.5, y=0.5, showarrow=False)],
    )
    return fig


def _threshold_shapes(axis: str = "y") -> list[dict]:
    if axis == "y":
        return [
            dict(type="rect", xref="paper", x0=0, x1=1, yref="y", y0=0, y1=50, fillcolor="rgba(211,107,99,.16)", line_width=0, layer="below"),
            dict(type="rect", xref="paper", x0=0, x1=1, yref="y", y0=50, y1=80, fillcolor="rgba(217,199,106,.18)", line_width=0, layer="below"),
            dict(type="rect", xref="paper", x0=0, x1=1, yref="y", y0=80, y1=100, fillcolor="rgba(111,166,111,.16)", line_width=0, layer="below"),
        ]
    return [
        dict(type="rect", yref="paper", y0=0, y1=1, xref="x", x0=0, x1=50, fillcolor="rgba(211,107,99,.14)", line_width=0, layer="below"),
        dict(type="rect", yref="paper", y0=0, y1=1, xref="x", x0=50, x1=80, fillcolor="rgba(217,199,106,.15)", line_width=0, layer="below"),
        dict(type="rect", yref="paper", y0=0, y1=1, xref="x", x0=80, x1=100, fillcolor="rgba(111,166,111,.14)", line_width=0, layer="below"),
    ]


def _unit_label(row: pd.Series) -> str:
    if row.get("hierarchy_level") == "Mission" and row.get("installation"):
        return f"{row.get('installation')} / {row.get('name')}"
    return str(row.get("name") or "Unassigned")


def reaf_box_plot(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure("REAF score distributions")
    fig = go.Figure()
    for _, row in df.sort_values("name").iterrows():
        values = pd.Series([row[field] for field, _label in REAF_LABELS if field in df and row[field] is not None]).dropna()
        if values.empty:
            continue
        fig.add_trace(
            go.Box(
                y=values,
                name=_unit_label(row),
                boxpoints="all",
                jitter=0.35,
                pointpos=0,
                marker=dict(size=4, color="#1f2933", opacity=0.58),
                line=dict(color="#2b2925"),
                fillcolor="rgba(255,255,255,.62)",
            )
        )
    fig.update_layout(
        title="REAF score distributions by selected unit",
        template=CHART_TEMPLATE,
        height=330,
        margin=dict(l=44, r=16, t=46, b=42),
        showlegend=False,
        shapes=_threshold_shapes("y"),
    )
    fig.update_yaxes(range=[0, 100], title="Score")
    fig.update_xaxes(title="", tickangle=-18)
    return fig


def _kde(values: pd.Series, x_grid: np.ndarray) -> np.ndarray:
    values = values.dropna().astype(float).to_numpy()
    if values.size == 0:
        return np.zeros_like(x_grid)
    bandwidth = max(4.5, values.std() * 0.55) if values.size > 1 else 7.5
    density = np.exp(-0.5 * ((x_grid[:, None] - values[None, :]) / bandwidth) ** 2).sum(axis=1)
    if density.max() > 0:
        density = density / density.max()
    return density


def reaf_ridge_plot(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure("REAF score ridges")
    x_grid = np.linspace(0, 100, 161)
    fig = go.Figure()
    band_defs = [
        (0, 50, "rgba(211,107,99,.58)"),
        (50, 80, "rgba(217,199,106,.58)"),
        (80, 100, "rgba(111,166,111,.62)"),
    ]
    for index, (field, label) in enumerate(reversed(REAF_LABELS)):
        baseline = index
        density = _kde(df[field], x_grid) * 0.72
        for low, high, color in band_defs:
            mask = (x_grid >= low) & (x_grid <= high)
            band_x = x_grid[mask]
            band_y = baseline + density[mask]
            polygon_x = list(band_x) + list(reversed(band_x))
            polygon_y = list(band_y) + [baseline] * len(band_x)
            fig.add_trace(
                go.Scatter(
                    x=polygon_x,
                    y=polygon_y,
                    mode="lines",
                    fill="toself",
                    line=dict(color=color, width=1),
                    fillcolor=color,
                    hovertemplate=f"{label}<br>Score: %{{x:.0f}}<extra></extra>",
                    showlegend=False,
                )
            )
        fig.add_trace(
            go.Scatter(
                x=x_grid,
                y=np.full_like(x_grid, baseline),
                mode="lines",
                line=dict(color="rgba(98,93,85,.4)", width=1),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_annotation(x=0, y=baseline + 0.35, text=label, showarrow=False, xanchor="right", font=dict(size=10, color="#625d55"))
    fig.update_layout(
        title="REAF score ridges",
        template=CHART_TEMPLATE,
        height=330,
        margin=dict(l=48, r=16, t=46, b=42),
    )
    fig.update_xaxes(range=[0, 100], title="Score")
    fig.update_yaxes(visible=False, range=[-0.35, len(REAF_LABELS) - 0.05])
    return fig


def _radar_values(df: pd.DataFrame) -> tuple[list[float], list[float]]:
    a_fields = ["reaf_r1_a", "reaf_r2_a", "reaf_r3_a", "reaf_r4_a", "reaf_r5_a"]
    b_fields = ["reaf_r1_b", "reaf_r2_b", "reaf_r3_b", "reaf_r4_b", "reaf_r5_b"]
    return [float(df[field].mean()) for field in a_fields], [float(df[field].mean()) for field in b_fields]


def reaf_radar_profile(df: pd.DataFrame, group_field: str | None = None) -> go.Figure:
    if df.empty:
        return _empty_figure("REAF profile")
    axes = ["R1", "R2", "R3", "R4", "R5"]
    theta = axes + [axes[0]]

    if group_field:
        grouped = list(df.dropna(subset=[group_field]).groupby(group_field, sort=True))[:6]
        if not grouped:
            return _empty_figure("REAF profile")
        cols = min(3, len(grouped))
        rows = int(np.ceil(len(grouped) / cols))
        fig = make_subplots(rows=rows, cols=cols, specs=[[{"type": "polar"} for _ in range(cols)] for _ in range(rows)], subplot_titles=[str(name) for name, _ in grouped])
        for index, (_name, group) in enumerate(grouped, start=1):
            row = int(np.ceil(index / cols))
            col = ((index - 1) % cols) + 1
            a_values, b_values = _radar_values(group)
            fig.add_trace(go.Scatterpolar(r=a_values + [a_values[0]], theta=theta, mode="lines+markers", name="A sub-scores", line=dict(color="#2f5f8f", width=2), marker=dict(size=5), showlegend=index == 1), row=row, col=col)
            fig.add_trace(go.Scatterpolar(r=b_values + [b_values[0]], theta=theta, mode="lines+markers", name="B sub-scores", line=dict(color="#8a6d16", width=2), marker=dict(size=5), showlegend=index == 1), row=row, col=col)
        fig.update_layout(
            title="REAF profile drilldown",
            template=CHART_TEMPLATE,
            height=330,
            margin=dict(l=28, r=28, t=56, b=22),
            legend=dict(orientation="h", y=-0.08),
        )
        fig.update_polars(radialaxis=dict(range=[0, 100], tickvals=[50, 80, 100]), angularaxis=dict(direction="clockwise"))
        return fig

    a_values, b_values = _radar_values(df)
    fig = go.Figure()
    for radius, color, name in [(100, "rgba(111,166,111,.12)", "Strong"), (80, "rgba(217,199,106,.16)", "Moderate"), (50, "rgba(211,107,99,.16)", "Poor")]:
        fig.add_trace(go.Scatterpolar(r=[radius] * 6, theta=theta, fill="toself", fillcolor=color, line=dict(width=0), name=name, hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatterpolar(r=a_values + [a_values[0]], theta=theta, mode="lines+markers", name="A sub-scores", line=dict(color="#2f5f8f", width=2), marker=dict(size=6)))
    fig.add_trace(go.Scatterpolar(r=b_values + [b_values[0]], theta=theta, mode="lines+markers", name="B sub-scores", line=dict(color="#8a6d16", width=2), marker=dict(size=6)))
    fig.update_layout(
        title="REAF profile",
        template=CHART_TEMPLATE,
        height=330,
        margin=dict(l=28, r=28, t=46, b=24),
        polar=dict(radialaxis=dict(range=[0, 100], tickvals=[50, 80, 100]), angularaxis=dict(direction="clockwise")),
        legend=dict(orientation="h", y=-0.08),
    )
    return fig


def gap_stacked_bar(df: pd.DataFrame, unit_label: str) -> go.Figure:
    if df.empty:
        return _empty_figure("Gap counts by category")
    rows = []
    for _, row in df.iterrows():
        unit_name = _unit_label(row)
        for category in GAP_CATEGORIES:
            field = f"gap_{category.lower().replace(' ', '_')}"
            rows.append({"unit_name": unit_name, "gap_category": category, "count": row.get(field) or 0})
    plot_df = pd.DataFrame(rows).groupby(["unit_name", "gap_category"], as_index=False)["count"].sum()
    fig = px.bar(
        plot_df,
        x="unit_name",
        y="count",
        color="gap_category",
        barmode="stack",
        category_orders={"gap_category": GAP_CATEGORIES, "unit_name": sorted(plot_df["unit_name"].unique().tolist())},
        template=CHART_TEMPLATE,
        title=f"Gap counts by {unit_label}",
        labels={"unit_name": unit_label.title(), "count": "Gaps", "gap_category": "Gap type"},
    )
    fig.update_layout(height=330, margin=dict(l=44, r=16, t=46, b=92), legend=dict(orientation="h", y=-0.32))
    fig.update_xaxes(tickangle=-18)
    return fig


def scored_distribution(df: pd.DataFrame, chart_view: str, window_start: int, locked_fields: list[str] | None = None) -> go.Figure:
    locked_fields = locked_fields or []
    if df.empty:
        return _empty_figure("Scored indicator distribution")

    if chart_view == "small_multiples":
        fields = REAF_SMALL_MULTIPLES
        title = "REAF small multiples"
    else:
        unlocked = [item for item in SCORED_INDICATORS if item[0] not in locked_fields]
        start = min(max(window_start, 0), max(len(unlocked) - 1, 0))
        fields = [(field, label) for field, label in SCORED_INDICATORS if field in locked_fields]
        fields.extend(unlocked[start : start + 3])
        title = "Scored indicator distribution"

    rows = []
    for field, label in fields:
        if field not in df:
            continue
        for value in df[field].dropna():
            rows.append({"indicator": label, "score": value, "band": _score_band(value)})

    plot_df = pd.DataFrame(rows)
    if plot_df.empty:
        return _empty_figure(title)

    fig = px.violin(
        plot_df,
        x="indicator",
        y="score",
        color="band",
        box=True,
        points="all",
        category_orders={"band": ["Low", "Mid", "High"]},
        color_discrete_map={"Low": "#d36b63", "Mid": "#d9c76a", "High": "#6fa66f"},
        template=CHART_TEMPLATE,
        title=title,
    )
    fig.update_yaxes(range=[0, 100], title="Score")
    fig.update_xaxes(title="")
    fig.update_layout(height=330, margin=dict(l=42, r=18, t=48, b=74), legend_title_text="Band")
    return fig


def _count_long(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        for category in GAP_CATEGORIES:
            field = f"gap_{category.lower().replace(' ', '_')}"
            rows.append(
                {
                    "hierarchy_level": row["hierarchy_level"],
                    "majcom": row["majcom"],
                    "installation": row["installation"],
                    "mission": row["mission"],
                    "gap_category": category,
                    "eligibility": "FSRM",
                    "count": row.get("fsrm_eligible_count") or 0,
                    "gap_count": row.get(field) or 0,
                }
            )
            rows.append(
                {
                    "hierarchy_level": row["hierarchy_level"],
                    "majcom": row["majcom"],
                    "installation": row["installation"],
                    "mission": row["mission"],
                    "gap_category": category,
                    "eligibility": "MILCON",
                    "count": row.get("milcon_eligible_count") or 0,
                    "gap_count": row.get(field) or 0,
                }
            )
    return pd.DataFrame(rows)


def count_stacked_bar(df: pd.DataFrame, x_dimension: str, stack_dimension: str) -> go.Figure:
    if df.empty:
        return _empty_figure("Count-based matrix summary")
    long_df = _count_long(df)
    value_col = "gap_count" if stack_dimension == "gap_category" or x_dimension == "gap_category" else "count"
    grouped = (
        long_df.groupby([x_dimension, stack_dimension], dropna=False)[value_col]
        .sum()
        .reset_index(name="records")
    )
    grouped[x_dimension] = grouped[x_dimension].fillna("Unassigned")
    grouped[stack_dimension] = grouped[stack_dimension].fillna("Unassigned")
    fig = px.bar(
        grouped,
        x=x_dimension,
        y="records",
        color=stack_dimension,
        barmode="stack",
        template=CHART_TEMPLATE,
        title="Count-based matrix summary",
        labels={
            x_dimension: COUNT_DIMENSIONS.get(x_dimension, x_dimension),
            stack_dimension: COUNT_DIMENSIONS.get(stack_dimension, stack_dimension),
            "records": "Count",
        },
    )
    fig.update_layout(height=330, margin=dict(l=42, r=18, t=48, b=84), legend_title_text="")
    return fig
