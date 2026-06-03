"""Color mode metadata shared by the grid, legend, and Dash controls."""

COLOR_MODES = {
    "fsrm": {
        "label": "FSRM eligibility",
        "fields": ["fsrm_likelihood", "fsrm_score", "fsrm_count", "fsrm_ready_flag"],
        "legend": [
            ("Low", "#f4eff9"),
            ("Medium", "#d6bee8"),
            ("High", "#8d5bb8"),
        ],
    },
    "milcon": {
        "label": "MILCON eligibility",
        "fields": ["milcon_likelihood", "milcon_score", "milcon_count", "milcon_ready_flag"],
        "legend": [
            ("Low", "#f3f2ed"),
            ("Medium", "#d8ca8f"),
            ("High", "#9b7b1a"),
        ],
    },
    "external": {
        "label": "External funding eligibility",
        "fields": ["external_funding_likelihood", "external_score", "external_count", "external_partner_flag"],
        "legend": [
            ("Low", "#edf5f5"),
            ("Medium", "#9ecdd0"),
            ("High", "#287f86"),
        ],
    },
    "planning": {
        "label": "Planning maturity",
        "fields": ["planning_maturity", "planning_score", "planning_doc_count", "planning_gap_flag"],
        "legend": [
            ("Concept", "#f6eeee"),
            ("Scoped", "#ead7a7"),
            ("Programmed", "#9fc6a2"),
            ("Validated", "#4f8b62"),
        ],
    },
    "redundancy": {
        "label": "Redundancy / partial fulfillment",
        "fields": ["redundancy_status", "partial_fulfillment_status", "redundancy_score", "partial_fulfillment_flag"],
        "legend": [
            ("Single point", "#f1c7c0"),
            ("Partial", "#ead7a7"),
            ("Redundant", "#a9cfb5"),
            ("N/A", "#f1eee8"),
        ],
    },
    "cost": {
        "label": "Cost scale",
        "fields": ["cost_scale", "cost_score", "rough_order_cost_m", "cost_confidence"],
        "legend": [
            ("Low", "#edf4ed"),
            ("Medium", "#b8d0a3"),
            ("High", "#d8b15e"),
            ("Very high", "#b96d47"),
        ],
    },
    "evidence": {
        "label": "Evidence strength",
        "fields": ["evidence_strength", "evidence_score", "evidence_count", "evidence_gap_flag"],
        "legend": [
            ("Anecdotal", "#f4eeee"),
            ("Limited", "#e7d7aa"),
            ("Documented", "#a8c6db"),
            ("Strong", "#5f8fb2"),
        ],
    },
}


def mode_options():
    return [{"label": config["label"], "value": key} for key, config in COLOR_MODES.items()]


def legend_items(mode_key):
    return COLOR_MODES[mode_key]["legend"]
