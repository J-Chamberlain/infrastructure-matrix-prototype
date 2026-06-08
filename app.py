"""Standalone Dash prototype for the resilience matrix tool."""

from __future__ import annotations

import dash
import dash_ag_grid as dag
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html

from charts import COUNT_DIMENSIONS, SCORED_INDICATORS, count_stacked_bar, scored_distribution
from color_modes import OVERLAYS, legend_items, overlay_options
from grid_config import GRID_OPTIONS, build_column_defs
from synthetic_data import (
    LEVEL_FILTERS,
    LEVEL_ORDER,
    apply_role_scope,
    build_synthetic_data,
    descendants_for,
    initial_expanded_ids,
)


BASE_DF = build_synthetic_data()

ROLE_OPTIONS = [
    {"label": "Enterprise user", "value": "enterprise"},
    {"label": "ACC MAJCOM user", "value": "majcom_acc"},
    {"label": "Nellis installation user", "value": "installation_nellis"},
    {"label": "Nellis fighter mission user", "value": "mission_nellis_fighter"},
    {"label": "Single asset user", "value": "asset_first"},
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
  color: var(--muted);
  font-size: 12px;
  margin-left: auto;
}
.grid-wrap, .chart-panel {
  border: 1px solid var(--rule);
  background: var(--surface);
}
.chart-panel {
  margin-top: 16px;
  padding: 12px;
}
.charts {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
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
.level-enterprise, .level-majcom, .level-installation, .level-mission {
  font-weight: 700;
}
.level-enterprise { background: #e8dfcf; }
.level-majcom { background: #eee6d8; }
.level-installation { background: #f4eee4; }
.level-mission { background: #f8f3ec; }
.level-asset { color: #34302b; }
.blank-cell {
  color: #9b9184;
  background: repeating-linear-gradient(135deg, #faf8f4, #faf8f4 6px, #f1eee8 6px, #f1eee8 12px);
}
.score-low { background: #f2cbc7; }
.score-mid { background: #eee2a3; }
.score-high { background: #bdd9bd; }
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


def visible_df(role: str, expanded_ids: list[str], depth: str, overlay: str) -> pd.DataFrame:
    expanded = set(expanded_ids or [])
    levels = LEVEL_FILTERS[depth]
    df = scoped_df(role)

    def is_visible(row) -> bool:
        if row["hierarchy_level"] not in levels:
            return False
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


def create_app() -> Dash:
    app = dash.Dash(__name__)
    app.index_string = app.index_string.replace("</head>", f"<style>{CSS}</style></head>")

    app.layout = html.Div(
        className="app-shell",
        children=[
            dcc.Store(id="expanded-ids", data=list(initial_expanded_ids(BASE_DF))),
            dcc.Store(id="pinned-row-id", data=None),
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
                                className="control-block",
                                children=[
                                    html.Label("Hierarchy depth", className="control-label"),
                                    dcc.Dropdown(
                                        id="depth-filter",
                                        options=[
                                            {"label": "Enterprise only", "value": "enterprise"},
                                            {"label": "Through MAJCOM", "value": "majcom"},
                                            {"label": "Through installation", "value": "installation"},
                                            {"label": "Through mission", "value": "mission"},
                                            {"label": "All levels", "value": "all"},
                                        ],
                                        value="all",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Label("Expansion", className="control-label"),
                                    html.Div(
                                        className="button-row",
                                        children=[
                                            html.Button("Expand all", id="expand-all", n_clicks=0),
                                            html.Button("Collapse", id="collapse-all", n_clicks=0),
                                        ],
                                    ),
                                ]
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
                        className="ag-theme-quartz",
                        columnDefs=build_column_defs(),
                        rowData=records(visible_df("enterprise", list(initial_expanded_ids(BASE_DF)), "all", "none")),
                        getRowId="params.data.row_id",
                        dashGridOptions=GRID_OPTIONS,
                        dangerously_allow_code=True,
                        selectedRows=[],
                        style={"height": "650px", "width": "100%"},
                    )
                ],
            ),
            html.Div(
                id="chart-panel",
                className="chart-panel",
                children=[
                    html.Div(
                        className="chart-controls",
                        children=[
                            html.Div(
                                className="control-block compact",
                                children=[
                                    html.Label("Score chart", className="control-label"),
                                    dcc.Dropdown(
                                        id="score-chart-view",
                                        options=[
                                            {"label": "Composite", "value": "composite"},
                                            {"label": "REAF multiples", "value": "small_multiples"},
                                        ],
                                        value="composite",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block compact",
                                children=[
                                    html.Label("Series page", className="control-label"),
                                    dcc.Slider(id="series-window", min=0, max=3, step=1, value=0, marks=None, tooltip={"placement": "bottom"}),
                                ],
                            ),
                            html.Div(
                                className="control-block",
                                children=[
                                    html.Label("Locked score references", className="control-label"),
                                    dcc.Dropdown(
                                        id="locked-series",
                                        options=[{"label": label, "value": field} for field, label in SCORED_INDICATORS],
                                        value=[],
                                        multi=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block compact",
                                children=[
                                    html.Label("Count X", className="control-label"),
                                    dcc.Dropdown(
                                        id="count-x",
                                        options=[{"label": label, "value": value} for value, label in COUNT_DIMENSIONS.items()],
                                        value="installation",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-block compact",
                                children=[
                                    html.Label("Stack by", className="control-label"),
                                    dcc.Dropdown(
                                        id="count-stack",
                                        options=[{"label": label, "value": value} for value, label in COUNT_DIMENSIONS.items()],
                                        value="gap_category",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Label("Chart pin", className="control-label"),
                                    html.Div(
                                        className="button-row",
                                        children=[
                                            html.Button("Pin selected", id="pin-chart", n_clicks=0),
                                            html.Button("Unpin", id="unpin-chart", n_clicks=0),
                                        ],
                                    ),
                                ]
                            ),
                            html.Div(id="pin-status", className="status-line"),
                        ],
                    ),
                    html.Div(
                        className="charts",
                        children=[
                            html.Div(dcc.Graph(id="score-chart", config={"displayModeBar": False}), className="chart-card"),
                            html.Div(dcc.Graph(id="count-chart", config={"displayModeBar": False}), className="chart-card"),
                        ],
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("expanded-ids", "data"),
        Input("matrix-grid", "cellClicked"),
        Input("expand-all", "n_clicks"),
        Input("collapse-all", "n_clicks"),
        Input("role-scope", "value"),
        State("expanded-ids", "data"),
    )
    def update_expansion(cell, _expand_clicks, _collapse_clicks, role, expanded_ids):
        trigger = dash.ctx.triggered_id
        df = scoped_df(role)
        if trigger == "expand-all":
            return df.loc[df["children_count"] > 0, "row_id"].tolist()
        if trigger in ["collapse-all", "role-scope"]:
            return df.loc[df["hierarchy_level"] == "Enterprise", "row_id"].tolist()
        expanded = set(expanded_ids or [])
        if trigger == "matrix-grid" and cell and cell.get("colId") == "name":
            row = cell.get("data", {})
            row_id = row.get("row_id")
            if row.get("children_count", 0) > 0 and row_id:
                if row_id in expanded:
                    expanded.remove(row_id)
                else:
                    expanded.add(row_id)
        return list(expanded)

    @app.callback(
        Output("pinned-row-id", "data"),
        Input("pin-chart", "n_clicks"),
        Input("unpin-chart", "n_clicks"),
        State("matrix-grid", "selectedRows"),
        State("pinned-row-id", "data"),
    )
    def update_pin(_pin_clicks, _unpin_clicks, selected_rows, pinned_id):
        trigger = dash.ctx.triggered_id
        if trigger == "unpin-chart":
            return None
        if trigger == "pin-chart" and selected_rows:
            return selected_rows[0].get("row_id")
        return pinned_id

    @app.callback(
        Output("matrix-grid", "rowData"),
        Output("legend", "children"),
        Output("chart-panel", "className"),
        Output("pin-status", "children"),
        Output("score-chart", "figure"),
        Output("count-chart", "figure"),
        Input("expanded-ids", "data"),
        Input("overlay-mode", "value"),
        Input("role-scope", "value"),
        Input("depth-filter", "value"),
        Input("pinned-row-id", "data"),
        Input("score-chart-view", "value"),
        Input("series-window", "value"),
        Input("locked-series", "value"),
        Input("count-x", "value"),
        Input("count-stack", "value"),
    )
    def update_view(expanded_ids, overlay, role, depth, pinned_row_id, score_view, series_window, locked_series, count_x, count_stack):
        visible = visible_df(role, expanded_ids, depth, overlay)
        chart_df, pin_status = chart_scope_df(role, pinned_row_id, visible)
        chart_panel_class = "chart-panel pin-active" if pinned_row_id else "chart-panel"
        return (
            records(visible),
            build_legend(overlay),
            chart_panel_class,
            pin_status,
            scored_distribution(chart_df, score_view, series_window, locked_series),
            count_stacked_bar(chart_df, count_x, count_stack),
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, port=8050)
