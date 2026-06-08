# Porting Notes

## Intended Production Shape

Port this prototype into a Dash-adjacent application as a feature module, not as a monolithic `app.py`.

Suggested structure:

```text
resilience_matrix/
  __init__.py
  data_contract.py
  data_access.py
  rbac.py
  grid_config.py
  overlays.py
  charts.py
  layout.py
  callbacks.py
```

Keep `synthetic_data.py` development-only. The production data layer should return the same field contract but enforce row visibility before records are sent to Dash.

## Dependencies

Prototype dependencies:

```text
dash
dash-ag-grid
pandas
plotly
```

Pin versions in the target repo. This prototype was validated with Dash 4.2.0 and Dash AG Grid 35.2.0 under Python 3.14.3.

## Row Hierarchy

Design target:

```text
Enterprise -> MAJCOM -> Installation -> Mission -> Building/Asset
```

The brief requests AG Grid native row grouping with independently collapsible levels. That requires AG Grid Enterprise. This repo does not include a license, so the runnable prototype uses flattened rows with app-managed expansion state.

Production options:

- With AG Grid Enterprise: use native row grouping or tree data, using the existing `path`/`parent_id` fields and server-side rollup rows.
- Without AG Grid Enterprise: retain the current flattened fallback with explicit expansion state and pinned identity columns.

Do not silently enable Enterprise-only features without confirming licensing.

## Data Contract

Each row should include:

- hierarchy: `row_id`, `parent_id`, `path`, `hierarchy_level`, `level_rank`, `name`, `type`
- org scope: `enterprise`, `majcom`, `installation`, `mission`, `building_asset`
- REAF: `reaf_composite`, `reaf_r1_a` ... `reaf_r5_b`
- gaps: `gap_total`, category gap fields, `unassigned_gap_count`, `has_unassigned_gap_delta`
- funding: `funding_request_count`, `funding_request_amount_m`
- condition and availability: `building_condition_score`, `utility_availability_score`
- initiative progress: `smart_meter_progress`, `microgrid_progress`, `backup_power_progress`
- eligibility: `fsrm_eligible_count`, `milcon_eligible_count`, `fsrm_eligibility_strength`, `milcon_eligibility_strength`
- RBAC scope keys: `rbac_enterprise`, `rbac_majcom`, `rbac_installation`, `rbac_mission`, `rbac_asset`

Blank/non-applicable values should be null, not placeholder strings. Example: REAF fields are null at Building/Asset level.

## Rollups

Current prototype rollup assumptions:

- score fields roll up by average
- count fields roll up by sum
- Mission rows may include `unassigned_gap_count`
- Mission gap total may therefore exceed the sum of visible child Building/Asset gap counts
- `has_unassigned_gap_delta` marks that discrepancy and the grid displays a `†` marker

Production should replace these assumptions with approved business rules per metric.

## RBAC

RBAC must be enforced server-side. The prototype's role selector is only a shape demonstration.

Production requirements:

- authenticate the user before building row data
- map the user to one or more organization scopes
- filter rows in the data access layer, not in client-only grid state
- include parent context rows for authorized descendants
- never send peer organizations outside the user's permission scope to the browser

The current `apply_role_scope()` function is intentionally simple and should be replaced with real authorization logic.

## Color Overlay System

FSRM and MILCON eligibility columns are always colored by their own eligibility strength.

The optional overlay selector applies one of these lenses to other matrix columns:

- no overlay
- FSRM overlay
- MILCON overlay

Only one overlay should be active at a time. Keep score-band formatting as the default when no overlay is active.

## Chart Panel

Current prototype chart model:

- scored indicator distribution chart for 0-100 metrics
- REAF small-multiple mode for R-category sub-scores
- stacked bar chart for count-based fields
- X-axis and stack-dimension switchers
- chart pin/unpin based on selected grid row
- locked scored-series references while paging through the remaining indicators

Production follow-up:

- wire chart updates to AG Grid native expansion events if Enterprise row grouping is used
- persist chart pin state if users need saved analysis sessions
- confirm default stacked bar dimensions with users
- replace synthetic initiative names with the approved initiative list

## Known Open Items

- exact infrastructure gap taxonomy
- funding request source systems and ingestion rules
- complete initiative list
- final FSRM and MILCON color ramps
- final visual treatment for unassigned mission-level gaps
- complete scored indicator inventory beyond REAF, condition, availability, and initiative progress
