# Porting Notes

## Repo Inspection Summary

- Target repo is currently an Astro/TypeScript site with React components.
- Package manager appears to be npm via `package.json` and `package-lock.json`.
- No Python package manager file was found (`requirements.txt`, `pyproject.toml`, Poetry, Pipfile, or uv lock).
- Local `python3 --version` returned Python 3.14.3, but the repo does not declare a Python runtime.
- No existing Dash, Plotly, pandas, or Dash AG Grid usage was found.
- Styling conventions use restrained editorial tokens in `src/styles/tokens.css` and `src/styles/base.css`, with warm surfaces, Public Sans UI typography, and thin rule borders.

## Recommended Porting Shape

Because the target app is not currently a Dash app, port this as a separate module/folder inside the eventual Dash-adjacent repo rather than into the Astro site directly.

Suggested eventual structure:

```text
dash_app/
  infrastructure_matrix/
    __init__.py
    data.py
    grid_config.py
    color_modes.py
    charts.py
    layout.py
    callbacks.py
```

Keep synthetic data in a development-only path and replace it with the real data access layer later.

## Dependencies

Prototype dependencies:

```text
dash
dash-ag-grid
pandas
plotly
```

Before porting, confirm the target Dash-adjacent repo's pinned versions. Dash AG Grid syntax can vary by major version, so keep `columnDefs`, `dashGridOptions`, and callback property names aligned with the installed version.

## AG Grid Feature Assumptions

No AG Grid Enterprise license was found in this repo. The prototype therefore avoids:

- row grouping
- row aggregation
- pivoting
- tree data

Hierarchy is represented with normal rows:

- `hierarchy_level`
- `level_rank`
- identifier columns
- indented `hierarchy_label`
- bold parent-row styles
- app-state buttons that filter visible levels

If the target repo later confirms an Enterprise license, true tree data or row grouping could replace the flattened fallback. The current approach should remain the default until that license is explicit.

## Files To Port

- `synthetic_data.py`: Use as a schema/reference only. Replace generated rows with real data.
- `grid_config.py`: Port most directly. This contains pinned columns, grouped columns, summary/detail `columnGroupShow`, and cell class rules.
- `color_modes.py`: Port directly unless the product already has a status/color taxonomy.
- `charts.py`: Port as optional supplemental visuals.
- `app.py`: Split into layout, callbacks, and styling according to the target Dash app conventions.

## Data Contract

The grid expects one record per visible row with these categories of fields:

- identifiers: `hierarchy_level`, `enterprise`, `installation`, `mission`, `building`, `hierarchy_label`
- tags: `source_system`, `gap_category`, `reef_reaf_strategy_tag`, `gaps_tag`
- likelihoods: `fsrm_likelihood`, `milcon_likelihood`, `external_funding_likelihood`
- statuses: `planning_maturity`, `redundancy_status`, `partial_fulfillment_status`, `cost_scale`, `evidence_strength`
- counts and scores: `*_count`, `*_score`, `planning_doc_count`, `rough_order_cost_m`
- flags: `*_flag`
- notes: `reason_evidence_note`

Blank and non-applicable values should be `None`/null, not placeholder text. The grid handles those cells with a subdued blank style.

## Styling Notes

The prototype CSS loosely follows the current repo's restrained warm surface, Public Sans UI font, thin borders, and compact controls. When integrating into a Dash app, move these styles to the app's normal stylesheet or theme system.

Avoid making the color modes too saturated across every column. The current rule set emphasizes only the selected metric family and leaves other values readable.

## Known Incompatibilities / Follow-Up

- The current repo is Astro, not Dash. This prototype should not be mounted directly without a Python web service or separate Dash app.
- The prototype uses synthetic aggregate parent rows. Real data will need clear aggregation rules for parent levels.
- Column group open/closed state is local to AG Grid. If the product needs saved user preferences, add persistence later.
- The hierarchy controls filter by level, they do not perform true expand/collapse per parent. That is intentional to avoid Enterprise features.
