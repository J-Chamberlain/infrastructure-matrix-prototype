"""Plotly summary charts for the matrix prototype."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


CHART_TEMPLATE = "plotly_white"


def fsrm_vs_milcon(df: pd.DataFrame) -> go.Figure:
    counts = (
        df.dropna(subset=["fsrm_likelihood", "milcon_likelihood"])
        .groupby(["fsrm_likelihood", "milcon_likelihood"])
        .size()
        .reset_index(name="records")
    )
    fig = px.density_heatmap(
        counts,
        x="fsrm_likelihood",
        y="milcon_likelihood",
        z="records",
        histfunc="sum",
        category_orders={"fsrm_likelihood": ["Low", "Medium", "High"], "milcon_likelihood": ["Low", "Medium", "High"]},
        color_continuous_scale=["#f7f3ef", "#d6bee8", "#8d5bb8"],
        title="FSRM vs MILCON likelihood",
        template=CHART_TEMPLATE,
    )
    fig.update_layout(height=285, margin=dict(l=42, r=18, t=48, b=42), coloraxis_showscale=False)
    return fig


def maturity_by_gap(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby(["gap_category", "planning_maturity"]).size().reset_index(name="records")
    fig = px.bar(
        counts,
        x="gap_category",
        y="records",
        color="planning_maturity",
        barmode="stack",
        category_orders={"planning_maturity": ["Concept", "Scoped", "Programmed", "Validated"]},
        color_discrete_map={
            "Concept": "#d7aaa3",
            "Scoped": "#d8bd71",
            "Programmed": "#8eb792",
            "Validated": "#4f8b62",
        },
        title="Planning maturity by gap category",
        template=CHART_TEMPLATE,
    )
    fig.update_layout(height=285, margin=dict(l=42, r=18, t=48, b=58), legend_title_text="")
    return fig


def redundancy_summary(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby(["redundancy_status", "partial_fulfillment_status"]).size().reset_index(name="records")
    fig = px.bar(
        counts,
        x="redundancy_status",
        y="records",
        color="partial_fulfillment_status",
        barmode="group",
        category_orders={"redundancy_status": ["Single point", "Partial", "Redundant"]},
        color_discrete_map={"None": "#d9d2c5", "Partial": "#d8bd71", "Substantial": "#8fb3c7"},
        title="Redundancy and partial fulfillment",
        template=CHART_TEMPLATE,
    )
    fig.update_layout(height=285, margin=dict(l=42, r=18, t=48, b=42), legend_title_text="")
    return fig
