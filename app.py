"""Standalone Dash prototype for a spreadsheet-like infrastructure matrix."""

from __future__ import annotations

import dash
import dash_ag_grid as dag
from dash import Dash, Input, Output, dcc, html

from charts import fsrm_vs_milcon, maturity_by_gap, redundancy_summary
from color_modes import COLOR_MODES, legend_items, mode_options
from grid_config import GRID_OPTIONS, build_column_defs
from synthetic_data import LEVEL_ORDER, build_synthetic_data


BASE_DF = build_synthetic_data()

LEVEL_FILTERS = {
    "all": ["Enterprise", "Installation", "Mission", "Building"],
    "installation": ["Enterprise", "Installation"],
    "mission": ["Enterprise", "Installation", "Mission"],
    "buildings": ["Building"],
}

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
  max-width: 1780px;
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
.controls {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 14px;
}
.control-block {
  min-width: 220px;
}
.control-label {
  display: block;
  color: var(--muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .07em;
  margin-bottom: 6px;
}
.level-buttons {
  display: inline-flex;
  border: 1px solid var(--rule);
  background: var(--surface);
}
.level-buttons label {
  border-right: 1px solid var(--rule);
  padding: 8px 10px;
  font-size: 12px;
}
.level-buttons label:last-child {
  border-right: 0;
}
.level-buttons input {
  margin-right: 5px;
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
.grid-wrap {
  border: 1px solid var(--rule);
  background: var(--surface);
}
.charts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}
.chart-panel {
  border: 1px solid var(--rule);
  background: var(--surface);
  min-width: 0;
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
.level-enterprise, .level-installation, .level-mission {
  font-weight: 700;
}
.level-enterprise {
  background: #ebe2d3;
}
.level-installation {
  background: #f1eadf;
}
.level-mission {
  background: #f7f1e8;
}
.level-building {
  color: #34302b;
}
.blank-cell {
  color: #9b9184;
  background: repeating-linear-gradient(135deg, #faf8f4, #faf8f4 6px, #f1eee8 6px, #f1eee8 12px);
}
.flag-false {
  color: #7a7166;
}
.mode-fsrm-low { background: #f4eff9; }
.mode-fsrm-medium { background: #d6bee8; }
.mode-fsrm-high, .mode-fsrm-number-high, .mode-fsrm-flag-true { background: #8d5bb8; color: white; }
.mode-fsrm-number-low { background: #f4eff9; }
.mode-fsrm-number-medium { background: #d6bee8; }
.mode-milcon-low { background: #f3f2ed; }
.mode-milcon-medium { background: #d8ca8f; }
.mode-milcon-high, .mode-milcon-number-high, .mode-milcon-flag-true { background: #9b7b1a; color: white; }
.mode-milcon-number-low { background: #f3f2ed; }
.mode-milcon-number-medium { background: #d8ca8f; }
.mode-external-low { background: #edf5f5; }
.mode-external-medium { background: #9ecdd0; }
.mode-external-high, .mode-external-number-high, .mode-external-flag-true { background: #287f86; color: white; }
.mode-external-number-low { background: #edf5f5; }
.mode-external-number-medium { background: #9ecdd0; }
.mode-planning-concept { background: #f6eeee; }
.mode-planning-scoped, .mode-planning-number-medium { background: #ead7a7; }
.mode-planning-programmed { background: #9fc6a2; }
.mode-planning-validated, .mode-planning-number-high, .mode-planning-flag-true { background: #4f8b62; color: white; }
.mode-planning-number-low { background: #f6eeee; }
.mode-redundancy-single { background: #f1c7c0; }
.mode-redundancy-partial, .mode-redundancy-number-medium, .mode-redundancy-flag-true { background: #ead7a7; }
.mode-redundancy-redundant, .mode-redundancy-number-high { background: #79aa87; color: white; }
.mode-redundancy-number-low { background: #f1c7c0; }
.mode-cost-low, .mode-cost-number-low { background: #edf4ed; }
.mode-cost-medium, .mode-cost-number-medium { background: #b8d0a3; }
.mode-cost-high { background: #d8b15e; }
.mode-cost-very-high, .mode-cost-number-high { background: #b96d47; color: white; }
.mode-evidence-anecdotal, .mode-evidence-number-low { background: #f4eeee; }
.mode-evidence-limited { background: #e7d7aa; }
.mode-evidence-documented, .mode-evidence-number-medium { background: #a8c6db; }
.mode-evidence-strong, .mode-evidence-number-high, .mode-evidence-flag-true { background: #5f8fb2; color: white; }
@media (max-width: 1100px) {
  .topbar { align-items: stretch; flex-direction: column; }
  .charts { grid-template-columns: 1fr; }
}
"""


def filtered_records(level_filter: str, color_mode: str):
    levels = LEVEL_FILTERS[level_filter]
    filtered = BASE_DF[BASE_DF["hierarchy_level"].isin(levels)].copy()
    filtered["active_color_mode"] = color_mode
    return filtered.where(filtered.notna(), None).to_dict("records")


def build_legend(mode_key: str):
    return html.Div(
        [
            html.Span(f"Legend: {COLOR_MODES[mode_key]['label']}", className="legend-title"),
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


def create_app() -> Dash:
    app = dash.Dash(__name__)
    app.index_string = app.index_string.replace("</head>", f"<style>{CSS}</style></head>")

    app.layout = html.Div(
        className="app-shell",
        children=[
            html.Div(
                className="topbar",
                children=[
                    html.Div(
                        [
                            html.H1("Infrastructure Eligibility Matrix"),
                            html.P(
                                "Standalone Dash AG Grid prototype using flattened hierarchy rows, grouped columns, pinned identifiers, and synthetic data.",
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
                                    html.Label("Color mode", className="control-label"),
                                    dcc.Dropdown(
                                        id="color-mode",
                                        options=mode_options(),
                                        value="fsrm",
                                        clearable=False,
                                        searchable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Label("Hierarchy view", className="control-label"),
                                    dcc.RadioItems(
                                        id="level-filter",
                                        className="level-buttons",
                                        inputClassName="level-radio",
                                        options=[
                                            {"label": "All", "value": "all"},
                                            {"label": "Through installation", "value": "installation"},
                                            {"label": "Through mission", "value": "mission"},
                                            {"label": "Buildings", "value": "buildings"},
                                        ],
                                        value="all",
                                        inline=True,
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
                        rowData=filtered_records("all", "fsrm"),
                        getRowId="params.data.row_id",
                        dashGridOptions=GRID_OPTIONS,
                        dangerously_allow_code=True,
                        style={"height": "650px", "width": "100%"},
                    )
                ],
            ),
            html.Div(
                className="charts",
                children=[
                    html.Div(dcc.Graph(id="chart-fsrm-milcon", config={"displayModeBar": False}), className="chart-panel"),
                    html.Div(dcc.Graph(id="chart-maturity", config={"displayModeBar": False}), className="chart-panel"),
                    html.Div(dcc.Graph(id="chart-redundancy", config={"displayModeBar": False}), className="chart-panel"),
                ],
            ),
        ],
    )

    @app.callback(
        Output("matrix-grid", "rowData"),
        Output("legend", "children"),
        Output("chart-fsrm-milcon", "figure"),
        Output("chart-maturity", "figure"),
        Output("chart-redundancy", "figure"),
        Input("level-filter", "value"),
        Input("color-mode", "value"),
    )
    def update_view(level_filter, color_mode):
        row_data = filtered_records(level_filter, color_mode)
        chart_df = BASE_DF[BASE_DF["hierarchy_level"].isin(LEVEL_FILTERS[level_filter])]
        return (
            row_data,
            build_legend(color_mode),
            fsrm_vs_milcon(chart_df),
            maturity_by_gap(chart_df),
            redundancy_summary(chart_df),
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, port=8050)
