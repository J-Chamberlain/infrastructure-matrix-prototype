"""Plotly chart builders for the resilience matrix prototype."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
