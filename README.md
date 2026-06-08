# Resilience Matrix Tool Prototype

Standalone Dash prototype for an interactive resilience matrix using Dash AG Grid for the table and Plotly for responsive charts.

The prototype visualizes energy resilience indicators, infrastructure gaps, funding eligibility, and initiative progress across a five-level organizational hierarchy:

```text
Enterprise -> MAJCOM -> Installation -> Mission -> Building/Asset
```

## Run

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:8050>.

## Current Prototype Behavior

- Five-level synthetic hierarchy: Enterprise, MAJCOM, Installation, Mission, Building/Asset.
- Community-compatible flattened hierarchy with independent row expand/collapse by clicking the `Name` cell.
- Pinned identity columns: `Level`, `Name`, and `Type`.
- Collapsible column groups:
  - REAF Score
  - Infrastructure Gaps
  - Funding Requests
  - Building Condition
  - Power / Utility Availability
  - Initiative Progress
  - FSRM Eligible
  - MILCON Eligible
- FSRM and MILCON eligibility columns are always color-coded by eligibility strength.
- Optional overlay selector applies FSRM or MILCON coloring across other matrix columns.
- Mission-level gap cells show a `†` marker when mission gap counts include unassigned gaps not present in child building rows.
- Simulated RBAC scope selector demonstrates server-side row filtering shape for Enterprise, MAJCOM, Installation, Mission, and Asset users.
- Chart panel includes:
  - scored indicator distribution chart
  - REAF small-multiple distribution option
  - scored-series paging and locked reference series
  - count-based stacked bar chart with X-axis and stack-dimension switchers
  - chart pin/unpin behavior based on the selected grid row

## AG Grid Enterprise Note

The revised design brief calls for AG Grid native row grouping. AG Grid row grouping is an Enterprise feature. This standalone prototype does not assume an Enterprise license, so it keeps a runnable Community-compatible hierarchy fallback.

The data model includes `path`, `parent_id`, `hierarchy_level`, and rollup fields so a licensed implementation can swap the hierarchy renderer to AG Grid row grouping or tree data later.

## Files

- `app.py`: Dash layout, callbacks, inline prototype CSS, hierarchy state, role scope, overlay state, and chart pinning.
- `synthetic_data.py`: deterministic five-level synthetic data generator, rollups, unassigned mission gap markers, and RBAC scope helpers.
- `grid_config.py`: Dash AG Grid column groups, pinned identity columns, formatters, and conditional styling.
- `color_modes.py`: FSRM/MILCON overlay metadata and legends.
- `charts.py`: Plotly scored distribution and count stacked bar builders.
- `PORTING_NOTES.md`: implementation notes for moving the pattern into a production Dash-adjacent codebase.
