"""Dash AG Grid column definitions and styling helpers."""

from __future__ import annotations

from color_modes import COLOR_MODES


PINNED_COLUMNS = [
    {
        "field": "hierarchy_label",
        "headerName": "Hierarchy",
        "pinned": "left",
        "width": 220,
        "cellClassRules": {
            "level-enterprise": "params.data && params.data.hierarchy_level == 'Enterprise'",
            "level-installation": "params.data && params.data.hierarchy_level == 'Installation'",
            "level-mission": "params.data && params.data.hierarchy_level == 'Mission'",
            "level-building": "params.data && params.data.hierarchy_level == 'Building'",
        },
        "valueFormatter": {
            "function": """
                const level = params.data ? params.data.hierarchy_level : '';
                const prefix = level === 'Installation' ? '  ' : level === 'Mission' ? '    ' : level === 'Building' ? '      ' : '';
                return prefix + (params.value || '');
            """
        },
    },
    {"field": "hierarchy_level", "headerName": "Level", "pinned": "left", "width": 132, "filter": True},
    {"field": "enterprise", "headerName": "Enterprise", "pinned": "left", "width": 180, "filter": True},
    {"field": "installation", "headerName": "Installation", "pinned": "left", "width": 160, "filter": True},
    {"field": "mission", "headerName": "Mission", "pinned": "left", "width": 160, "filter": True},
    {"field": "building", "headerName": "Building", "pinned": "left", "width": 120, "filter": True},
]


def _metric_rules(mode: str):
    return {
        f"mode-{mode}-low": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Low'",
        f"mode-{mode}-medium": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Medium'",
        f"mode-{mode}-high": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'High'",
        f"mode-{mode}-very-high": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Very high'",
        "blank-cell": "params.value == null || params.value === ''",
    }


def _status_rules(mode: str):
    return {
        f"mode-{mode}-concept": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Concept'",
        f"mode-{mode}-scoped": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Scoped'",
        f"mode-{mode}-programmed": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Programmed'",
        f"mode-{mode}-validated": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Validated'",
        f"mode-{mode}-single": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Single point'",
        f"mode-{mode}-partial": f"params.data && params.data.active_color_mode == '{mode}' && (params.value == 'Partial' || params.value == 'Substantial')",
        f"mode-{mode}-redundant": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Redundant'",
        f"mode-{mode}-anecdotal": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Anecdotal'",
        f"mode-{mode}-limited": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Limited'",
        f"mode-{mode}-documented": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Documented'",
        f"mode-{mode}-strong": f"params.data && params.data.active_color_mode == '{mode}' && params.value == 'Strong'",
        "blank-cell": "params.value == null || params.value === ''",
    }


def _number_rules(mode: str):
    return {
        f"mode-{mode}-number-low": f"params.data && params.data.active_color_mode == '{mode}' && Number(params.value) > 0 && Number(params.value) < 35",
        f"mode-{mode}-number-medium": f"params.data && params.data.active_color_mode == '{mode}' && Number(params.value) >= 35 && Number(params.value) < 70",
        f"mode-{mode}-number-high": f"params.data && params.data.active_color_mode == '{mode}' && Number(params.value) >= 70",
        "blank-cell": "params.value == null || params.value === ''",
    }


def _flag_rules(mode: str):
    return {
        f"mode-{mode}-flag-true": f"params.data && params.data.active_color_mode == '{mode}' && params.value === true",
        "flag-false": "params.value === false",
        "blank-cell": "params.value == null || params.value === ''",
    }


def _col(field, header, mode=None, width=125, formatter=None, kind="metric"):
    rules = {}
    if mode and kind == "metric":
        rules = _metric_rules(mode)
    if mode and kind == "status":
        rules = _status_rules(mode)
    if mode and kind == "number":
        rules = _number_rules(mode)
    if mode and kind == "flag":
        rules = _flag_rules(mode)
    col = {
        "field": field,
        "headerName": header,
        "width": width,
        "filter": True,
        "sortable": True,
        "cellClassRules": rules,
    }
    if formatter:
        col["valueFormatter"] = {"function": formatter}
    return col


def _group(header, summary_col, detail_cols):
    return {
        "headerName": header,
        "marryChildren": True,
        "children": [
            {**summary_col, "columnGroupShow": "closed"},
            *[{**col, "columnGroupShow": "open"} for col in detail_cols],
        ],
    }


def build_column_defs():
    money_formatter = "return params.value == null ? '' : '$' + Number(params.value).toLocaleString() + 'M';"
    percent_formatter = "return params.value == null ? '' : Math.round(Number(params.value)) + '%';"
    int_formatter = "return params.value == null ? '' : Number(params.value).toLocaleString();"

    return [
        *PINNED_COLUMNS,
        _col("source_system", "Source System", width=150),
        _col("gap_category", "Gap Category", width=145),
        _group(
            "FSRM Eligibility",
            _col("fsrm_likelihood", "FSRM", "fsrm"),
            [
                _col("fsrm_score", "Score", "fsrm", formatter=percent_formatter, kind="number"),
                _col("fsrm_count", "Count", "fsrm", formatter=int_formatter, kind="number"),
                _col("fsrm_ready_flag", "Ready", "fsrm", kind="flag"),
            ],
        ),
        _group(
            "MILCON Eligibility",
            _col("milcon_likelihood", "MILCON", "milcon"),
            [
                _col("milcon_score", "Score", "milcon", formatter=percent_formatter, kind="number"),
                _col("milcon_count", "Count", "milcon", formatter=int_formatter, kind="number"),
                _col("milcon_ready_flag", "Ready", "milcon", kind="flag"),
            ],
        ),
        _group(
            "External Funding",
            _col("external_funding_likelihood", "External", "external"),
            [
                _col("external_score", "Score", "external", formatter=percent_formatter, kind="number"),
                _col("external_count", "Count", "external", formatter=int_formatter, kind="number"),
                _col("external_partner_flag", "Partner", "external", kind="flag"),
            ],
        ),
        _group(
            "REEF/REAF Strategy Tags",
            _col("reef_reaf_strategy_tag", "Strategy", width=210),
            [
                _col("gaps_tag", "GAPS Link", width=140),
                _col("reason_evidence_note", "Evidence Note", width=300),
            ],
        ),
        _group(
            "GAPS Tags",
            _col("gaps_tag", "GAPS", width=120),
            [
                _col("gap_category", "Category", width=130),
                _col("source_system", "Source", width=140),
            ],
        ),
        _group(
            "Planning Maturity",
            _col("planning_maturity", "Maturity", "planning", kind="status"),
            [
                _col("planning_score", "Score", "planning", formatter=percent_formatter, kind="number"),
                _col("planning_doc_count", "Docs", "planning", formatter=int_formatter, kind="number"),
                _col("planning_gap_flag", "Gap", "planning", kind="flag"),
            ],
        ),
        _group(
            "Redundancy / Partial Fulfillment",
            _col("redundancy_status", "Redundancy", "redundancy", width=145, kind="status"),
            [
                _col("partial_fulfillment_status", "Partial Status", "redundancy", width=145, kind="status"),
                _col("redundancy_score", "Score", "redundancy", formatter=percent_formatter, kind="number"),
                _col("partial_fulfillment_flag", "Partial", "redundancy", kind="flag"),
            ],
        ),
        _group(
            "Cost Scale",
            _col("cost_scale", "Cost", "cost"),
            [
                _col("cost_score", "Score", "cost", formatter=percent_formatter, kind="number"),
                _col("rough_order_cost_m", "ROM", "cost", formatter=money_formatter, kind="number"),
                _col("cost_confidence", "Confidence", width=130),
            ],
        ),
        _group(
            "Evidence Strength",
            _col("evidence_strength", "Evidence", "evidence", kind="status"),
            [
                _col("evidence_score", "Score", "evidence", formatter=percent_formatter, kind="number"),
                _col("evidence_count", "Count", "evidence", formatter=int_formatter, kind="number"),
                _col("evidence_gap_flag", "Gap", "evidence", kind="flag"),
            ],
        ),
    ]


GRID_OPTIONS = {
    "defaultColDef": {
        "resizable": True,
        "sortable": True,
        "filter": True,
        "floatingFilter": True,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
    "animateRows": False,
    "enableCellTextSelection": True,
    "suppressMenuHide": True,
    "sideBar": False,
}


def active_mode_fields(mode_key: str) -> list[str]:
    return COLOR_MODES[mode_key]["fields"]
