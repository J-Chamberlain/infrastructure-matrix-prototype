# Infrastructure Matrix Prototype

Standalone Dash prototype for a spreadsheet-like infrastructure eligibility matrix. It is intentionally separate from the Astro/TypeScript app in the parent repo.

## Run

```sh
cd matrix_prototype
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:8050>.

## What It Demonstrates

- Synthetic Enterprise -> Installation -> Mission -> Building hierarchy.
- Flattened hierarchy rows with indentation and parent-row styling.
- View controls for all levels, through installation, through mission, and buildings only.
- Dash AG Grid grouped column headers with collapsed summary columns and expanded detail columns through `columnGroupShow`.
- Pinned identifier columns on the left.
- User-selectable color modes with an updating legend.
- Rule-based conditional formatting for likelihoods, statuses, scores, flags, blank cells, and non-applicable cells.
- Sorting and filtering through AG Grid column controls.
- Plotly summary charts below the grid.

## Files

- `app.py`: Dash layout, callbacks, CSS, and launch entrypoint.
- `synthetic_data.py`: deterministic synthetic data generator and aggregate parent rows.
- `grid_config.py`: AG Grid column definitions and grouped column behavior.
- `color_modes.py`: color mode metadata and legend entries.
- `charts.py`: lightweight Plotly chart builders.
- `PORTING_NOTES.md`: integration notes for moving this pattern into the target repo.

## Licensing Assumption

This prototype uses Dash AG Grid Community-compatible features only. It does not use AG Grid Enterprise row grouping, tree data, aggregation, or pivoting.
