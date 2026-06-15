"""Standalone Dash prototype for the resilience matrix tool."""

from __future__ import annotations

import dash
import dash_ag_grid as dag
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html

from charts import gap_stacked_bar, reaf_box_plot, reaf_radar_profile, reaf_ridge_plot
from color_modes import OVERLAYS, legend_items, overlay_options
from grid_config import GRID_OPTIONS, build_column_defs
from synthetic_data import (
    apply_role_scope,
    build_synthetic_data,
    descendants_for,
    initial_expanded_ids,
)


BASE_DF = build_synthetic_data()

ROLE_OPTIONS = [
    {"label": "Enterprise user", "value": "enterprise"},
    {"label": "ARC MAJCOM user", "value": "majcom_acc"},
    {"label": "Talon Point installation user", "value": "installation_nellis"},
    {"label": "Talon Point fighter mission user", "value": "mission_nellis_fighter"},
    {"label": "Single asset user", "value": "asset_first"},
]

CHART_UNIT_OPTIONS = [
    {"label": "MAJCOM rollups", "value": "majcom"},
    {"label": "Installation rollups", "value": "installation"},
    {"label": "Mission rollups", "value": "mission"},
]

GRID_TEXT_OPTIONS = [
    {"label": "Small", "value": "small"},
    {"label": "Normal", "value": "normal"},
    {"label": "Large", "value": "large"},
]

RADAR_DETAIL_OPTIONS = [
    {"label": "Selected unit", "value": "selected"},
    {"label": "Drill down one level", "value": "drilldown"},
]

CSS = """
:root {
  --bg: #f8f6f1;
  --surface: #fffdfa;
  --ink: #20201d;
  --muted: #625d55;
  --rule: #d8d0c2;
  --accent: #6b5b30;
  --font-ui: "Public Sans", "Avenir Next", "Segoe UI", sans-serif;
}
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-ui);
}
.app-shell {
  max-width: 1860px;
  margin: 0 auto;
  padding: 22px 24px 34px;
}
.topbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-end;
  border-bottom: 1px solid var(--rule);
  padding-bottom: 14px;
}
h1 {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 680;
  letter-spacing: 0;
}
.subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
.controls, .chart-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
}
.control-block {
  min-width: 200px;
}
.control-block.compact {
  min-width: 130px;
}
.control-label {
  display: block;
  color: var(--muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .07em;
  margin-bottom: 6px;
}
.button-row {
  display: flex;
  gap: 6px;
}
button {
  border: 1px solid var(--rule);
  background: var(--surface);
  color: var(--ink);
  padding: 8px 10px;
  cursor: pointer;
}
button:hover {
  border-color: var(--accent);
}
.legend {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 14px 0;
  min-height: 30px;
}
.legend-title {
  color: var(--muted);
  font-size: 12px;
  margin-right: 4px;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #282520;
}
.swatch {
  width: 18px;
  height: 12px;
  border: 1px solid rgba(0,0,0,.12);
}
.status-line {
  margin-left: auto;
}
.unit-status {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border: 1px solid #b6a266;
  background: #f2ead2;
  color: #1d3558;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}
.unit-status-label {
  color: var(--muted);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .07em;
  margin-right: 7px;
  text-transform: uppercase;
}
.chart-filter {
  width: 220px;
  min-width: 220px;
}
.chart-unit-control {
  width: 190px;
  min-width: 190px;
}
.chart-filter .Select-control,
.chart-unit-control .Select-control {
  border-radius: 2px;
}
.chart-filter .Select--multi .Select-value {
  max-width: 92px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chart-filter .Select-menu-outer {
  min-width: 360px;
}
.chart-filter .Select-multi-value-wrapper {
  max-height: 34px;
  overflow: hidden;
}
.chart-filter .Select-placeholder {
  font-size: 13px;
}
.chart-filter .Select-input {
  max-width: 20px;
}
.chart-filter .Select-value-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chart-filter .Select-value,
.chart-unit-control .Select-value {
  line-height: 28px;
}
.chart-filter .Select-arrow-zone,
.chart-unit-control .Select-arrow-zone {
  width: 26px;
}
.grid-wrap, .chart-panel {
  border: 1px solid var(--rule);
  background: var(--surface);
}
.grid-wrap {
  margin-top: 12px;
}
.chart-toggle-row {
  display: flex;
  justify-content: center;
  margin: 8px 0 0;
}
.chart-toggle {
  min-width: 132px;
  padding: 6px 12px;
  font-size: 12px;
  color: var(--muted);
  background: #fbfaf7;
}
.chart-panel {
  margin-top: 8px;
  padding: 12px;
  background: #eee7dc;
}
.chart-panel.is-collapsed {
  display: none;
}
.charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 12px;
}
.chart-card {
  min-width: 0;
  border: 1px solid color-mix(in oklab, var(--rule) 75%, white 25%);
  background: #fff;
}
.pin-active {
  border-color: #6b5b30;
  box-shadow: inset 0 0 0 2px rgba(107, 91, 48, .18);
}
.ag-theme-quartz {
  --ag-font-family: var(--font-ui);
  --ag-font-size: 12px;
  --ag-header-background-color: #eee7dc;
  --ag-odd-row-background-color: #fbfaf7;
  --ag-border-color: #ddd5c8;
  --ag-row-hover-color: #f1eadf;
  --ag-selected-row-background-color: #ede3d0;
}
.grid-font-small {
  --ag-font-size: 11px;
}
.grid-font-normal {
  --ag-font-size: 12px;
}
.grid-font-large {
  --ag-font-size: 14px;
}
.level-enterprise, .level-majcom, .level-installation, .level-mission {
  font-weight: 700;
}
.level-enterprise {
  background: #e8dfcf;
  box-shadow: inset 3px 0 0 #b9aa8d;
}
.level-majcom {
  background: #eee6d8;
  box-shadow: inset 5px 0 0 #c5b79b;
  padding-left: 15px;
}
.level-installation {
  background: #f4eee4;
  box-shadow: inset 7px 0 0 #d0c3aa;
  padding-left: 17px;
}
.level-mission {
  background: #f8f3ec;
  box-shadow: inset 9px 0 0 #d8ccb7;
  padding-left: 19px;
}
.level-asset { color: #34302b; }
.blank-cell {
  color: #9b9184;
  background: #e9e8e4;
}
.score-low { background: #e8c9c5; }
.score-mid { background: #e6dca7; }
.score-high { background: #c7d9c4; }
.fsrm-weak { background: #f1edf7; }
.fsrm-mid { background: #cdb4db; }
.fsrm-strong { background: #7c4d9f; color: white; }
.milcon-weak { background: #f4f1e6; }
.milcon-mid { background: #d4bd68; }
.milcon-strong { background: #8a6d16; color: white; }
.gap-delta {
  font-weight: 700;
  box-shadow: inset 0 -2px 0 #8a6d16;
}
@media (max-width: 1200px) {
  .topbar { align-items: stretch; flex-direction: column; }
  .charts { grid-template-columns: 1fr; }
}
"""


def scoped_df(role: str) -> pd.DataFrame:
    return apply_role_scope(BASE_DF, role).copy()


def grid_df(role: str, overlay: str) -> pd.DataFrame:
    df = scoped_df(role)
    df["active_overlay"] = overlay
    return df.where(df.notna(), None)


def visible_df(role: str, expanded_ids: list[str], overlay: str) -> pd.DataFrame:
    expanded = set(expanded_ids or [])
    df = scoped_df(role)

    def is_visible(row) -> bool:
        path = row["path"]
        ancestor_ids = ["|".join(path[:index]) for index in range(1, len(path))]
        return all(ancestor in expanded for ancestor in ancestor_ids)

    visible = df[df.apply(is_visible, axis=1)].copy()
    visible["is_expanded"] = visible["row_id"].isin(expanded)
    visible["active_overlay"] = overlay
    return visible.where(visible.notna(), None)


def records(df: pd.DataFrame) -> list[dict]:
    return df.where(df.notna(), None).to_dict("records")


def build_legend(mode_key: str):
    return html.Div(
        [
            html.Span(f"Overlay: {OVERLAYS[mode_key]['label']}", className="legend-title"),
            *[
                html.Span(
                    [html.Span(className="swatch", style={"background": color}), html.Span(label)],
                    className="legend-item",
                )
                for label, color in legend_items(mode_key)
            ],
        ],
        className="legend",
    )


def chart_scope_df(role: str, pinned_row_id: str | None, visible: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if not pinned_row_id:
        return visible, "Dynamic: charts follow visible expanded rows"
    scope = descendants_for(scoped_df(role), pinned_row_id)
    label = scope.iloc[0]["name"] if not scope.empty else pinned_row_id
    return scope, f"Pinned: {label}"


def dropdown_options(values: list[str]) -> list[dict]:
    return [{"label": value, "value": value} for value in values]


def sorted_values(df: pd.DataFrame, field: str) -> list[str]:
    return sorted(value for value in df[field].dropna().unique().tolist())


def selected_or_all(selected: list[str] | None, available: list[str]) -> list[str]:
    return selected if selected else available


def chart_filter_df(role: str, chart_unit: str, majcoms: list[str] | None, installations: list[str] | None, missions: list[str] | None) -> tuple[pd.DataFrame, str]:
    df = scoped_df(role)
    available_majcoms = sorted_values(df, "majcom")
    majcom_values = selected_or_all(majcoms, available_majcoms)
    majcom_df = df[df["majcom"].isin(majcom_values)]

    available_installations = sorted_values(majcom_df, "installation")
    installation_values = selected_or_all(installations, available_installations)
    installation_df = majcom_df[majcom_df["installation"].isin(installation_values)]

    available_missions = sorted_values(installation_df, "mission")
    mission_values = selected_or_all(missions, available_missions)

    if chart_unit == "majcom":
        return df[(df["hierarchy_level"] == "MAJCOM") & (df["majcom"].isin(majcom_values))], "majcom"
    if chart_unit == "installation":
        return majcom_df[(majcom_df["hierarchy_level"] == "Installation") & (majcom_df["installation"].isin(installation_values))], "installation"
    return installation_df[(installation_df["hierarchy_level"] == "Mission") & (installation_df["mission"].isin(mission_values))], "mission"


def radar_filter_df(role: str, chart_unit: str, radar_detail: str, majcoms: list[str] | None, installations: list[str] | None, missions: list[str] | None) -> tuple[pd.DataFrame, str | None]:
    if radar_detail != "drilldown":
        chart_df, _unit = chart_filter_df(role, chart_unit, majcoms, installations, missions)
        return chart_df, None

    df = scoped_df(role)
    majcom_values = selected_or_all(majcoms, sorted_values(df, "majcom"))
    majcom_df = df[df["majcom"].isin(majcom_values)]
    installation_values = selected_or_all(installations, sorted_values(majcom_df, "installation"))
    installation_df = majcom_df[majcom_df["installation"].isin(installation_values)]
    mission_values = selected_or_all(missions, sorted_values(installation_df, "mission"))

    if chart_unit == "majcom":
        return majcom_df[(majcom_df["hierarchy_level"] == "Installation") & (majcom_df["installation"].isin(installation_values))], "name"
    return installation_df[(installation_df["hierarchy_level"] == "Mission") & (installation_df["mission"].isin(mission_values))], "name"


def create_app() -> Dash:
    app = dash.Dash(__name__)
    app.index_string = app.index_string.replace("</head>", f"<style>{CSS}</style></head>")
    initial_scope = scoped_df("enterprise")
    initial_majcoms = sorted_values(initial_scope, "majcom")
    initial_installations = sorted_values(initial_scope, "installation")
    initial_missions = sorted_values(initial_scope, "mission")

    app.layout = html.Div(
        className="app-shell",
        children=[
            dcc.Store(id="pinned-row-id", data=None),
            dcc.Store(id="charts-expanded", data=False),
            html.Div(
                className="topbar",
                children=[
                    html.Div(
                        [
                            html.H1("Resilience Matrix Tool"),
                            html.P(
                                "Dash AG Grid prototype for energy resilience indicators, infrastructure gaps, and funding eligibility.",
                                className="subtitle",
                            ),
                        ]
                    ),
                    html.Div(
                        className="controls",
                        children=[
                            html.Div(
                                className="control-block",
                                children=[
                                    html.Label("Role scope", className="control-label"),
                                    dcc.Dropdown(id="role-scope", options=ROLE_OPTIONS, value="enterprise", clearable=False),
                                ],
                            ),
                            html.Div(
                                className="control-block",
                                children=[
                                    html.Label("Funding overlay", className="control-label"),
                                    dcc.Dropdown(id="overlay-mode", options=overlay_options(), value="none", clearable=False),
                                ],
                            ),
                            html.Div(
                                className="control-block compact",
                                children=[
                                    html.Label("Table text", className="control-label"),
                                    dcc.Dropdown(id="grid-text-size", options=GRID_TEXT_OPTIONS, value="normal", clearable=False),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(id="legend"),
            html.Div(
                className="grid-wrap",
                children=[
                    dag.AgGrid(
                        id="matrix-grid",
                        className="ag-theme-quartz grid-font-normal",
                        columnDefs=build_column_defs(),
                        rowData=records(grid_df("enterprise", "none")),
                        getRowId="params.data.row_id",
                        dashGridOptions=GRID_OPTIONS,
                        dangerously_allow_code=True,
                        enableEnterpriseModules=True,
                        selectedRows=[],
                        style={"height": "calc(100vh - 260px)", "minHeight": "650px", "width": "100%"},
                    )
                ],
            ),
            html.Div(
                className="chart-toggle-row",
                children=html.Button("Show charts", id="chart-toggle", n_clicks=0, className="chart-toggle"),
            ),
            html.Div(
                id="chart-panel",
                className="chart-panel is-collapsed",
                children=[
                    html.Div(
                        className="chart-controls",
                        children=[
                            html.Div(
                                className="control-block chart-unit-control",
                                children=[
                                    html.Label("Chart unit", className="control-label"),
                                    dcc.Dropdown(
                                        id="chart-unit",
                                        options=CHART_UNIT_OPTIONS,
                                        value="installation",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block chart-unit-control",
                                children=[
                                    html.Label("Radar detail", className="control-label"),
                                    dcc.Dropdown(
                                        id="radar-detail",
                                        options=RADAR_DETAIL_OPTIONS,
                                        value="selected",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block chart-filter",
                                children=[
                                    html.Label("MAJCOM", className="control-label"),
                                    dcc.Dropdown(
                                        id="chart-majcom-filter",
                                        options=dropdown_options(initial_majcoms),
                                        value=initial_majcoms,
                                        multi=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block chart-filter",
                                children=[
                                    html.Label("Installation", className="control-label"),
                                    dcc.Dropdown(
                                        id="chart-installation-filter",
                                        options=dropdown_options(initial_installations),
                                        value=initial_installations,
                                        multi=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block chart-filter",
                                children=[
                                    html.Label("Mission", className="control-label"),
                                    dcc.Dropdown(
                                        id="chart-mission-filter",
                                        options=dropdown_options(initial_missions),
                                        value=initial_missions,
                                        multi=True,
                                    ),
                                ],
                            ),
                            html.Div(id="pin-status", className="status-line"),
                        ],
                    ),
                    html.Div(
                        className="charts",
                        children=[
                            html.Div(dcc.Graph(id="reaf-box-chart", config={"displayModeBar": False}), className="chart-card"),
                            html.Div(dcc.Graph(id="reaf-ridge-chart", config={"displayModeBar": False}), className="chart-card"),
                            html.Div(dcc.Graph(id="reaf-radar-chart", config={"displayModeBar": False}), className="chart-card"),
                            html.Div(dcc.Graph(id="gap-bar-chart", config={"displayModeBar": False}), className="chart-card"),
                        ],
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("chart-majcom-filter", "options"),
        Output("chart-majcom-filter", "value"),
        Input("role-scope", "value"),
    )
    def update_majcom_filter(role):
        values = sorted_values(scoped_df(role), "majcom")
        return dropdown_options(values), values

    @app.callback(
        Output("chart-installation-filter", "options"),
        Output("chart-installation-filter", "value"),
        Input("role-scope", "value"),
        Input("chart-majcom-filter", "value"),
    )
    def update_installation_filter(role, majcoms):
        df = scoped_df(role)
        values = selected_or_all(majcoms, sorted_values(df, "majcom"))
        filtered = df[df["majcom"].isin(values)]
        installations = sorted_values(filtered, "installation")
        return dropdown_options(installations), installations

    @app.callback(
        Output("chart-mission-filter", "options"),
        Output("chart-mission-filter", "value"),
        Input("role-scope", "value"),
        Input("chart-majcom-filter", "value"),
        Input("chart-installation-filter", "value"),
    )
    def update_mission_filter(role, majcoms, installations):
        df = scoped_df(role)
        majcom_values = selected_or_all(majcoms, sorted_values(df, "majcom"))
        filtered = df[df["majcom"].isin(majcom_values)]
        installation_values = selected_or_all(installations, sorted_values(filtered, "installation"))
        filtered = filtered[filtered["installation"].isin(installation_values)]
        missions = sorted_values(filtered, "mission")
        return dropdown_options(missions), missions

    @app.callback(
        Output("charts-expanded", "data"),
        Input("chart-toggle", "n_clicks"),
        State("charts-expanded", "data"),
    )
    def update_chart_visibility(_toggle_clicks, expanded):
        if dash.ctx.triggered_id == "chart-toggle":
            return not bool(expanded)
        return bool(expanded)

    @app.callback(
        Output("matrix-grid", "rowData"),
        Output("matrix-grid", "className"),
        Output("legend", "children"),
        Output("chart-panel", "className"),
        Output("chart-toggle", "children"),
        Output("pin-status", "children"),
        Output("reaf-box-chart", "figure"),
        Output("reaf-ridge-chart", "figure"),
        Output("reaf-radar-chart", "figure"),
        Output("gap-bar-chart", "figure"),
        Input("overlay-mode", "value"),
        Input("role-scope", "value"),
        Input("grid-text-size", "value"),
        Input("charts-expanded", "data"),
        Input("chart-unit", "value"),
        Input("radar-detail", "value"),
        Input("chart-majcom-filter", "value"),
        Input("chart-installation-filter", "value"),
        Input("chart-mission-filter", "value"),
    )
    def update_view(overlay, role, grid_text_size, charts_expanded, chart_unit, radar_detail, majcoms, installations, missions):
        chart_df, chart_unit = chart_filter_df(role, chart_unit, majcoms, installations, missions)
        radar_df, radar_group = radar_filter_df(role, chart_unit, radar_detail, majcoms, installations, missions)
        chart_classes = ["chart-panel"]
        if not charts_expanded:
            chart_classes.append("is-collapsed")
        return (
            records(grid_df(role, overlay)),
            f"ag-theme-quartz grid-font-{grid_text_size or 'normal'}",
            build_legend(overlay),
            " ".join(chart_classes),
            "Hide charts" if charts_expanded else "Show charts",
            html.Div(
                className="unit-status",
                children=[
                    html.Span("Unit", className="unit-status-label"),
                    html.Span(f"{chart_unit.title()} rollups"),
                ],
            ),
            reaf_box_plot(chart_df),
            reaf_ridge_plot(chart_df),
            reaf_radar_profile(radar_df, radar_group),
            gap_stacked_bar(chart_df, chart_unit),
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, port=8050)
