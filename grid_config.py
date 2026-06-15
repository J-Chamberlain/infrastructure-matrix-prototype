"""Dash AG Grid column definitions for the resilience matrix prototype."""

from __future__ import annotations

from synthetic_data import GAP_CATEGORIES, INITIATIVES, REAF_COMPONENTS


SCORE_FIELDS = [
    "reaf_composite",
    *REAF_COMPONENTS,
    "building_condition_score",
    "utility_availability_score",
    *INITIATIVES,
]


def _level_class_rules():
    return {
        "level-enterprise": "params.data && params.data.hierarchy_level == 'Enterprise'",
        "level-majcom": "params.data && params.data.hierarchy_level == 'MAJCOM'",
        "level-installation": "params.data && params.data.hierarchy_level == 'Installation'",
        "level-mission": "params.data && params.data.hierarchy_level == 'Mission'",
        "level-asset": "params.data && params.data.hierarchy_level == 'Building/Asset'",
    }


def _overlay_rules(always: str | None = None, include_score_default: bool = False):
    prefix = always or "params.data && params.data.active_overlay"
    rules = {
        "blank-cell": "params.value == null || params.value === ''",
    }
    if always == "fsrm":
        rules.update(
            {
                "fsrm-weak": "params.data && Number(params.data.fsrm_eligibility_strength) < 40",
                "fsrm-mid": "params.data && Number(params.data.fsrm_eligibility_strength) >= 40 && Number(params.data.fsrm_eligibility_strength) < 70",
                "fsrm-strong": "params.data && Number(params.data.fsrm_eligibility_strength) >= 70",
            }
        )
    elif always == "milcon":
        rules.update(
            {
                "milcon-weak": "params.data && Number(params.data.milcon_eligibility_strength) < 40",
                "milcon-mid": "params.data && Number(params.data.milcon_eligibility_strength) >= 40 && Number(params.data.milcon_eligibility_strength) < 70",
                "milcon-strong": "params.data && Number(params.data.milcon_eligibility_strength) >= 70",
            }
        )
    else:
        rules.update(
            {
                "fsrm-weak": "params.data && params.data.active_overlay == 'fsrm' && Number(params.data.fsrm_eligibility_strength) < 40",
                "fsrm-mid": "params.data && params.data.active_overlay == 'fsrm' && Number(params.data.fsrm_eligibility_strength) >= 40 && Number(params.data.fsrm_eligibility_strength) < 70",
                "fsrm-strong": "params.data && params.data.active_overlay == 'fsrm' && Number(params.data.fsrm_eligibility_strength) >= 70",
                "milcon-weak": "params.data && params.data.active_overlay == 'milcon' && Number(params.data.milcon_eligibility_strength) < 40",
                "milcon-mid": "params.data && params.data.active_overlay == 'milcon' && Number(params.data.milcon_eligibility_strength) >= 40 && Number(params.data.milcon_eligibility_strength) < 70",
                "milcon-strong": "params.data && params.data.active_overlay == 'milcon' && Number(params.data.milcon_eligibility_strength) >= 70",
            }
        )
    if include_score_default:
        rules.update(
            {
                "score-low": "params.data && params.data.active_overlay == 'none' && Number(params.value) < 40",
                "score-mid": "params.data && params.data.active_overlay == 'none' && Number(params.value) >= 40 && Number(params.value) < 70",
                "score-high": "params.data && params.data.active_overlay == 'none' && Number(params.value) >= 70",
            }
        )
    return rules


def _score_col(field: str, header: str, width: int = 118):
    return {
        "field": field,
        "headerName": header,
        "width": width,
        "filter": "agNumberColumnFilter",
        "sortable": True,
        "cellClassRules": _overlay_rules(include_score_default=True),
        "valueFormatter": {"function": "return params.value == null ? '' : Math.round(Number(params.value));"},
    }


def _count_col(field: str, header: str, width: int = 118, gap_delta: bool = False):
    rules = _overlay_rules()
    if gap_delta:
        rules["gap-delta"] = "params.data && params.data.has_unassigned_gap_delta === true"
    formatter = (
        "return params.value == null ? '' : Number(params.value).toLocaleString() + "
        "(params.data && params.data.has_unassigned_gap_delta ? ' †' : '');"
        if gap_delta
        else "return params.value == null ? '' : Number(params.value).toLocaleString();"
    )
    return {
        "field": field,
        "headerName": header,
        "width": width,
        "filter": "agNumberColumnFilter",
        "sortable": True,
        "cellClassRules": rules,
        "valueFormatter": {"function": formatter},
    }


def _money_col(field: str, header: str):
    return {
        "field": field,
        "headerName": header,
        "width": 128,
        "filter": "agNumberColumnFilter",
        "sortable": True,
        "cellClassRules": _overlay_rules(),
        "valueFormatter": {"function": "return params.value == null ? '' : '$' + Number(params.value).toLocaleString() + 'M';"},
    }


def _text_col(field: str, header: str, width: int = 118):
    return {
        "field": field,
        "headerName": header,
        "width": width,
        "filter": True,
        "sortable": True,
        "cellClassRules": _overlay_rules(),
    }


def _yes_no_col(field: str, header: str, width: int = 118):
    return {
        "field": field,
        "headerName": header,
        "width": width,
        "filter": True,
        "sortable": True,
        "cellClassRules": _overlay_rules(),
        "valueFormatter": {
            "function": (
                "if (params.value == null || params.value === '') { return ''; } "
                "if (params.data && params.data.hierarchy_level == 'Building/Asset') { return params.value; } "
                "return Number(params.value).toLocaleString();"
            )
        },
    }


def _year_col(field: str, header: str, width: int = 112):
    return {
        "field": field,
        "headerName": header,
        "width": width,
        "filter": "agNumberColumnFilter",
        "sortable": True,
        "cellClassRules": _overlay_rules(),
        "valueFormatter": {"function": "return params.value == null ? '' : String(Math.round(Number(params.value)));"},
    }


def _group(header: str, summary_col: dict, detail_cols: list[dict]):
    return {
        "headerName": header,
        "marryChildren": True,
        "children": [
            {**summary_col, "columnGroupShow": "closed"},
            *[{**col, "columnGroupShow": "open"} for col in detail_cols],
        ],
    }


def _initiative_label(field: str) -> str:
    return field.replace("_progress", "").replace("_", " ").title()


PINNED_COLUMNS = [
    _group(
        "Level / Type",
        {
            "field": "row_meta",
            "headerName": "Level / Type",
            "pinned": "left",
            "width": 168,
            "filter": True,
            "cellClassRules": _level_class_rules(),
        },
        [
            {
                "field": "hierarchy_level",
                "headerName": "Level",
                "pinned": "left",
                "width": 132,
                "filter": True,
                "cellClassRules": _level_class_rules(),
            },
            {
                "field": "type",
                "headerName": "Type",
                "pinned": "left",
                "width": 126,
                "filter": True,
                "cellClassRules": _level_class_rules(),
            },
        ],
    ),
]


def build_column_defs():
    gap_detail_cols = [_count_col(f"gap_{category.lower().replace(' ', '_')}", category, 116) for category in GAP_CATEGORIES]
    return [
        *PINNED_COLUMNS,
        _group(
            "REAF Score",
            _score_col("reaf_composite", "REAF"),
            [
                _score_col("reaf_r1_a", "R1 A"),
                _score_col("reaf_r1_b", "R1 B"),
                _score_col("reaf_r2_a", "R2 A"),
                _score_col("reaf_r2_b", "R2 B"),
                _score_col("reaf_r3_a", "R3 A"),
                _score_col("reaf_r3_b", "R3 B"),
                _score_col("reaf_r4_a", "R4 A"),
                _score_col("reaf_r4_b", "R4 B"),
                _score_col("reaf_r5_a", "R5 A"),
                _score_col("reaf_r5_b", "R5 B"),
            ],
        ),
        _group("Infrastructure Gaps", _count_col("gap_total", "Total Gaps", 132, gap_delta=True), gap_detail_cols),
        _group(
            "Funding Requests",
            _money_col("funding_request_amount_m", "Requests"),
            [
                _count_col("funding_request_count", "Count", 110),
                _money_col("funding_request_amount_m", "Amount"),
                {
                    "field": "source_system",
                    "headerName": "Primary Source",
                    "width": 150,
                    "filter": True,
                    "sortable": True,
                },
            ],
        ),
        _group(
            "Building Condition",
            _score_col("building_condition_score", "FCI/Eq."),
            [_score_col("building_condition_score", "Condition Score"), {"field": "source_system", "headerName": "SMS Source", "width": 140, "filter": True}],
        ),
        _group(
            "Power / Utility Availability",
            _score_col("utility_availability_score", "Availability"),
            [_score_col("utility_availability_score", "Normalized Score"), {"field": "note", "headerName": "Evidence Note", "width": 240, "filter": True}],
        ),
        _group(
            "Initiative Progress",
            _score_col("smart_meter_progress", "Progress"),
            [_score_col(field, _initiative_label(field), 142) for field in INITIATIVES],
        ),
        _group(
            "Eligibility & Class.",
            {
                "headerName": "Eligible",
                "width": 128,
                "filter": "agNumberColumnFilter",
                "sortable": True,
                "valueGetter": {"function": "return Number(params.data.fsrm_eligible_count || 0) + Number(params.data.milcon_eligible_count || 0);"},
                "cellClassRules": _overlay_rules(),
                "valueFormatter": {"function": "return params.value == null ? '' : Number(params.value).toLocaleString();"},
            },
            [
                _text_col("fac_category", "FAC Category", 128),
                {
                    **_count_col("fsrm_eligible_count", "FSRM Eligible", 136),
                    "cellClassRules": _overlay_rules(always="fsrm"),
                },
                {
                    **_count_col("milcon_eligible_count", "MILCON Eligible", 148),
                    "cellClassRules": _overlay_rules(always="milcon"),
                },
            ],
        ),
        _group(
            "Condition Assessment",
            _score_col("condition_fci_score", "Avg FCI", 120),
            [
                _score_col("condition_fci_score", "FCI Score", 118),
                _count_col("service_life_years", "Svc Life (Yrs)", 132),
                _score_col("mdi_score", "MDI Score", 118),
            ],
        ),
        _group(
            "Requirements",
            _count_col("in_aces_pm_count", "ACES-PM", 120),
            [
                _count_col("gap_total", "Gap Count", 118, gap_delta=True),
                _yes_no_col("in_aces_pm", "In ACES-PM", 128),
            ],
        ),
        _group(
            "Prioritization",
            _count_col("on_base_ipl_count", "Base IPL", 120),
            [
                _yes_no_col("on_base_ipl", "On Base IPL", 126),
                _count_col("afcamp_rank", "AFCAMP Rank", 132),
            ],
        ),
        _group(
            "Programming",
            _count_col("in_fydp_count", "In FYDP", 116),
            [
                _text_col("funding_track", "Funding Track", 132),
                _yes_no_col("in_fydp", "In FYDP", 112),
                _year_col("exec_year", "Exec Year", 112),
            ],
        ),
        _group(
            "Budgeting",
            _count_col("dd1391_active_count", "DD1391", 116),
            [
                _text_col("dd1391_status", "DD1391 Status", 142),
                _text_col("pe_number", "PE Number", 132),
            ],
        ),
        _group(
            "Execution",
            _count_col("exec_status_active_count", "Active Exec", 124),
            [
                _yes_no_col("cto_issued", "CTO Issued", 122),
                _text_col("exec_status", "Exec Status", 148),
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
    "rowSelection": {"mode": "singleRow"},
    "treeData": True,
    "getDataPath": {"function": "getDataPath(params)"},
    "groupDefaultExpanded": 2,
    "autoGroupColumnDef": {
        "headerName": "Name",
        "field": "name",
        "pinned": "left",
        "width": 230,
        "filter": True,
        "cellRenderer": "agGroupCellRenderer",
        "cellRendererParams": {"suppressCount": True},
        "cellClassRules": _level_class_rules(),
    },
    "sideBar": False,
}
