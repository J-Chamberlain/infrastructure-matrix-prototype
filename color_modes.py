"""Funding overlay metadata for grid and legend rendering."""

OVERLAYS = {
    "none": {
        "label": "No overlay",
        "description": "Default formatting on non-eligibility columns.",
        "legend": [
            ("Low score", "#d36b63"),
            ("Mid score", "#d9c76a"),
            ("High score", "#6fa66f"),
        ],
    },
    "fsrm": {
        "label": "FSRM overlay",
        "description": "Apply FSRM eligibility strength across other matrix columns.",
        "legend": [
            ("Weak", "#f1edf7"),
            ("Moderate", "#cdb4db"),
            ("Strong", "#7c4d9f"),
        ],
    },
    "milcon": {
        "label": "MILCON overlay",
        "description": "Apply MILCON eligibility strength across other matrix columns.",
        "legend": [
            ("Weak", "#f4f1e6"),
            ("Moderate", "#d4bd68"),
            ("Strong", "#8a6d16"),
        ],
    },
}


def overlay_options():
    return [{"label": config["label"], "value": key} for key, config in OVERLAYS.items()]


def legend_items(mode_key: str):
    return OVERLAYS[mode_key]["legend"]
