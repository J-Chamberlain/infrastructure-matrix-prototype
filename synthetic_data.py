"""Synthetic resilience matrix data with five-level hierarchy and rollups."""

from __future__ import annotations

import random
from collections.abc import Iterable

import pandas as pd


LEVEL_ORDER = {
    "Enterprise": 0,
    "MAJCOM": 1,
    "Installation": 2,
    "Mission": 3,
    "Building/Asset": 4,
}

LEVEL_FILTERS = {
    "enterprise": ["Enterprise"],
    "majcom": ["Enterprise", "MAJCOM"],
    "installation": ["Enterprise", "MAJCOM", "Installation"],
    "mission": ["Enterprise", "MAJCOM", "Installation", "Mission"],
    "all": ["Enterprise", "MAJCOM", "Installation", "Mission", "Building/Asset"],
}

REAF_COMPONENTS = [
    "reaf_r1_a",
    "reaf_r1_b",
    "reaf_r2_a",
    "reaf_r2_b",
    "reaf_r3_a",
    "reaf_r3_b",
    "reaf_r4_a",
    "reaf_r4_b",
    "reaf_r5_a",
    "reaf_r5_b",
]

GAP_CATEGORIES = [
    "HVAC",
    "Electrical",
    "Water",
    "Fuel",
    "Controls",
    "Envelope",
    "Backup Power",
    "Cyber",
]

INITIATIVES = [
    "smart_meter_progress",
    "microgrid_progress",
    "backup_power_progress",
]

SCORED_FIELDS = [
    "reaf_composite",
    *REAF_COMPONENTS,
    "building_condition_score",
    "utility_availability_score",
    *INITIATIVES,
]

COUNT_FIELDS = [
    "gap_total",
    *[f"gap_{category.lower().replace(' ', '_')}" for category in GAP_CATEGORIES],
    "funding_request_count",
    "funding_request_amount_m",
    "fsrm_eligible_count",
    "milcon_eligible_count",
]

BOOL_COUNT_FIELDS = [
    "in_aces_pm_count",
    "on_base_ipl_count",
    "in_fydp_count",
    "dd1391_active_count",
    "cto_issued_count",
    "exec_status_active_count",
]

ROLLUP_AVG_FIELDS = [
    "reaf_composite",
    *REAF_COMPONENTS,
    "building_condition_score",
    "utility_availability_score",
    *INITIATIVES,
    "fsrm_eligibility_strength",
    "milcon_eligibility_strength",
    "condition_fci_score",
    "mdi_score",
]

ROLLUP_SUM_FIELDS = COUNT_FIELDS + BOOL_COUNT_FIELDS + ["unassigned_gap_count"]


def _choice(rng: random.Random, values: list[str], weights: list[int] | None = None) -> str:
    return rng.choices(values, weights=weights, k=1)[0]


def _avg(values: Iterable[float | int | None]) -> float | None:
    valid = [value for value in values if value is not None and not pd.isna(value)]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 1)


def _sum(values: Iterable[float | int | None]) -> float:
    valid = [value for value in values if value is not None and not pd.isna(value)]
    return round(sum(valid), 1)


def _min_value(values: Iterable[float | int | None]) -> float | int | None:
    valid = [value for value in values if value is not None and not pd.isna(value)]
    if not valid:
        return None
    return min(valid)


def _mode(values: Iterable[str | None]) -> str | None:
    valid = [value for value in values if value]
    if not valid:
        return None
    counts = pd.Series(valid).value_counts()
    return str(counts.index[0])


def _score(rng: random.Random, low: int = 20, high: int = 96) -> int:
    return rng.randint(low, high)


def _score_band(score: float | int | None) -> str | None:
    if score is None or pd.isna(score):
        return None
    if score < 40:
        return "Low"
    if score < 70:
        return "Medium"
    return "High"


def _gap_field(category: str) -> str:
    return f"gap_{category.lower().replace(' ', '_')}"


def _node_id(*parts: str) -> str:
    return "|".join(part.replace("|", "-") for part in parts if part)


def _asset_rows(seed: int = 7) -> pd.DataFrame:
    rng = random.Random(seed)
    enterprises = ["Air Force Enterprise"]
    majcoms = {
        "Air Force Enterprise": ["ARC", "ETG", "PAC", "SPC"],
    }
    installations = {
        "ARC": ["Cobalt Ridge AFB", "Mesa Verde AFB", "Redstone Flats AFB", "Silver Dunes AFB", "Talon Point AFB", "Vega Springs AFB"],
        "ETG": ["Aurora Gate AFB", "Blue Mesa AFB", "Cedar Run AFB", "Falcon Hollow AFB", "Juniper Field AFB", "Prairie Star AFB"],
        "PAC": ["Coral Bay AB", "Granite Shoals AB", "Harbor Crest AB", "Koa Ridge AB", "Orchid Valley AB", "Typhoon Point AB"],
        "SPC": ["Aster Mesa SFB", "Comet Basin SFB", "Kepler Ridge SFB", "Nova Hills SFB", "Pioneer Flats SFB", "Zenith Range SFB"],
    }
    missions = ["Fighter Operations", "Training", "Cyber Operations", "Logistics", "Command Support"]
    asset_types = ["Hangar", "Operations", "Utility Plant", "Dormitory", "Warehouse", "Clinic"]
    source_systems = ["BUILDER SMS", "NexGen IT", "AMP", "Power Study", "Manual Survey"]
    fac_categories = {
        "Hangar": ["2111", "2112", "2114"],
        "Operations": ["1412", "1414", "1495"],
        "Utility Plant": ["8910", "8920", "8930"],
        "Dormitory": ["7211", "7213", "7214"],
        "Warehouse": ["4421", "4422", "4428"],
        "Clinic": ["5100", "5500", "5300"],
    }
    dd1391_statuses = ["Submitted", "MAJCOM", "AFIMSC", "HAF", "OSD"]
    exec_statuses = ["Design", "Contract Award", "Construction", "Closeout", "Complete"]

    rows: list[dict] = []
    asset_index = 1
    for enterprise in enterprises:
        for majcom in majcoms[enterprise]:
            for installation in installations[majcom]:
                for mission in missions:
                    for asset_offset in range(rng.randint(4, 7)):
                        gap_counts = {field: rng.randint(0, 3) for field in [_gap_field(category) for category in GAP_CATEGORIES]}
                        gap_total = sum(gap_counts.values())
                        building_condition = _score(rng, 22, 94)
                        utility_score = _score(rng, 25, 98)
                        fsrm_strength = min(100, round(gap_total * 8 + (100 - building_condition) * 0.55 + rng.randint(0, 16)))
                        milcon_strength = min(100, round(gap_total * 5 + max(0, 65 - utility_score) * 0.75 + rng.randint(0, 18)))
                        funding_count = rng.randint(0, 5)
                        asset_type = _choice(rng, asset_types)
                        local_building_number = f"B{1000 + asset_index}"
                        installation_code = "".join(part[0] for part in installation.replace("-", " ").split())[:4].upper()
                        rpuid = f"AF-{installation_code}-{asset_index:03d}"
                        asset_name = f"{local_building_number} - {rpuid}"
                        in_aces_pm = funding_count > 0 and rng.random() < 0.72
                        on_base_ipl = funding_count > 0 and rng.random() < 0.54
                        afcamp_rank = rng.randint(1, 450) if on_base_ipl and rng.random() < 0.68 else None
                        funding_track = ""
                        if funding_count > 0:
                            funding_track = "MILCON" if rng.random() < 0.32 or milcon_strength > fsrm_strength + 10 else "FSRM"
                        in_fydp = bool(funding_track and rng.random() < 0.42)
                        exec_year = rng.randint(2027, 2031) if in_fydp else None
                        dd1391_status = _choice(rng, dd1391_statuses) if funding_track == "MILCON" and rng.random() < 0.58 else ""
                        cto_issued = funding_track == "FSRM" and rng.random() < 0.34
                        exec_status = _choice(rng, exec_statuses) if funding_track and rng.random() < 0.46 else "None"
                        node_id = _node_id(enterprise, majcom, installation, mission, rpuid)

                        rows.append(
                            {
                                "row_id": node_id,
                                "parent_id": _node_id(enterprise, majcom, installation, mission),
                                "path": [enterprise, majcom, installation, mission, asset_name],
                                "hierarchy_level": "Building/Asset",
                                "level_rank": LEVEL_ORDER["Building/Asset"],
                                "name": asset_name,
                                "row_meta": "Building/Asset / " + asset_type,
                                "type": asset_type,
                                "enterprise": enterprise,
                                "majcom": majcom,
                                "installation": installation,
                                "mission": mission,
                                "building_asset": asset_name,
                                "local_building_number": local_building_number,
                                "rpuid": rpuid,
                                "source_system": _choice(rng, source_systems),
                                "reaf_composite": None,
                                **{field: None for field in REAF_COMPONENTS},
                                "gap_total": gap_total,
                                **gap_counts,
                                "unassigned_gap_count": 0,
                                "has_unassigned_gap_delta": False,
                                "funding_request_count": funding_count,
                                "funding_request_amount_m": round(funding_count * rng.uniform(0.4, 4.8), 1),
                                "building_condition_score": building_condition,
                                "utility_availability_score": utility_score,
                                "smart_meter_progress": _score(rng, 5, 100),
                                "microgrid_progress": _score(rng, 0, 88),
                                "backup_power_progress": _score(rng, 15, 100),
                                "fsrm_eligible_count": rng.randint(0, max(1, gap_total)),
                                "milcon_eligible_count": rng.randint(0, max(1, gap_total // 2 + 1)),
                                "fsrm_eligibility_strength": fsrm_strength,
                                "milcon_eligibility_strength": milcon_strength,
                                "fsrm_band": _score_band(fsrm_strength),
                                "milcon_band": _score_band(milcon_strength),
                                "fac_category": _choice(rng, fac_categories[asset_type]),
                                "condition_fci_score": building_condition,
                                "service_life_years": rng.randint(1, 42),
                                "mdi_score": _score(rng, 35, 100),
                                "in_aces_pm": "Yes" if in_aces_pm else "No",
                                "in_aces_pm_count": int(in_aces_pm),
                                "on_base_ipl": "Yes" if on_base_ipl else "No",
                                "on_base_ipl_count": int(on_base_ipl),
                                "afcamp_rank": afcamp_rank,
                                "funding_track": funding_track,
                                "in_fydp": "Yes" if in_fydp else "No",
                                "in_fydp_count": int(in_fydp),
                                "exec_year": exec_year,
                                "dd1391_status": dd1391_status,
                                "dd1391_active_count": int(bool(dd1391_status)),
                                "pe_number": f"PE{rng.randint(100000, 999999)}" if in_fydp else "",
                                "cto_issued": "Yes" if cto_issued else ("No" if funding_track == "FSRM" else ""),
                                "cto_issued_count": int(cto_issued),
                                "exec_status": exec_status,
                                "exec_status_active_count": int(exec_status != "None"),
                                "rbac_enterprise": enterprise,
                                "rbac_majcom": majcom,
                                "rbac_installation": installation,
                                "rbac_mission": mission,
                                "rbac_asset": asset_name,
                                "note": "Asset-level source record; REAF is unavailable at this resolution.",
                            }
                        )
                        asset_index += 1
    return pd.DataFrame(rows)


def _mission_reaf_rows(asset_df: pd.DataFrame, seed: int = 19) -> dict[str, dict[str, int]]:
    rng = random.Random(seed)
    mission_scores: dict[str, dict[str, int]] = {}
    for keys, _group in asset_df.groupby(["enterprise", "majcom", "installation", "mission"], sort=True):
        mission_id = _node_id(*keys)
        component_scores = {field: _score(rng, 24, 96) for field in REAF_COMPONENTS}
        component_scores["reaf_composite"] = round(sum(component_scores.values()) / len(REAF_COMPONENTS))
        mission_scores[mission_id] = component_scores
    return mission_scores


def _aggregate(asset_df: pd.DataFrame, level: str, group_cols: list[str], mission_reaf: dict[str, dict[str, int]]) -> pd.DataFrame:
    rows = []
    rng = random.Random(31 + LEVEL_ORDER[level])
    for keys, group in asset_df.groupby(group_cols, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        context = dict(zip(group_cols, keys))
        row_id = _node_id(*[str(context[col]) for col in group_cols])
        parent_cols = group_cols[:-1]
        parent_id = _node_id(*[str(context[col]) for col in parent_cols]) if parent_cols else None
        unassigned_gap_count = rng.randint(1, 10) if level == "Mission" else int(_sum(group["unassigned_gap_count"]))

        row = {
            "row_id": row_id,
            "parent_id": parent_id,
            "path": [str(context[col]) for col in group_cols],
            "hierarchy_level": level,
            "level_rank": LEVEL_ORDER[level],
            "name": str(context[group_cols[-1]]),
            "row_meta": f"{level} / Rollup",
            "type": "Rollup",
            "enterprise": context.get("enterprise"),
            "majcom": context.get("majcom"),
            "installation": context.get("installation"),
            "mission": context.get("mission"),
            "building_asset": None,
            "local_building_number": None,
            "rpuid": None,
            "source_system": "Rollup",
            "unassigned_gap_count": unassigned_gap_count,
            "has_unassigned_gap_delta": bool(unassigned_gap_count > 0 and level == "Mission"),
            "rbac_enterprise": context.get("enterprise"),
            "rbac_majcom": context.get("majcom"),
            "rbac_installation": context.get("installation"),
            "rbac_mission": context.get("mission"),
            "rbac_asset": None,
            "note": "Rollup row.",
        }

        for field in ROLLUP_SUM_FIELDS:
            if field == "unassigned_gap_count":
                continue
            row[field] = _sum(group[field])
        row["gap_total"] = row["gap_total"] + unassigned_gap_count

        if level == "Mission":
            row.update(mission_reaf[row_id])
        else:
            child_group_cols = ["enterprise", "majcom", "installation", "mission"]
            child_scores = []
            for child_keys, _child_group in group.groupby(child_group_cols, sort=True):
                child_scores.append(mission_reaf[_node_id(*child_keys)])
            for field in ["reaf_composite", *REAF_COMPONENTS]:
                row[field] = _avg(score[field] for score in child_scores)

        for field in ["building_condition_score", "utility_availability_score", *INITIATIVES]:
            row[field] = _avg(group[field])
        row["fsrm_eligibility_strength"] = _avg(group["fsrm_eligibility_strength"])
        row["milcon_eligibility_strength"] = _avg(group["milcon_eligibility_strength"])
        row["fsrm_band"] = _score_band(row["fsrm_eligibility_strength"])
        row["milcon_band"] = _score_band(row["milcon_eligibility_strength"])
        row["fac_category"] = None
        row["condition_fci_score"] = _avg(group["condition_fci_score"])
        row["service_life_years"] = _avg(group["service_life_years"])
        row["mdi_score"] = _avg(group["mdi_score"])
        row["in_aces_pm"] = row["in_aces_pm_count"]
        row["on_base_ipl"] = row["on_base_ipl_count"]
        row["afcamp_rank"] = _min_value(group["afcamp_rank"])
        row["funding_track"] = _mode(group["funding_track"])
        row["in_fydp"] = row["in_fydp_count"]
        row["exec_year"] = _min_value(group["exec_year"])
        row["dd1391_status"] = _mode(group["dd1391_status"])
        row["dd1391_active_count"] = _sum(group["dd1391_active_count"])
        row["pe_number"] = None
        row["cto_issued"] = row["cto_issued_count"]
        row["exec_status"] = _mode(group["exec_status"])
        rows.append(row)
    return pd.DataFrame(rows)


def build_synthetic_data() -> pd.DataFrame:
    assets = _asset_rows()
    mission_reaf = _mission_reaf_rows(assets)
    missions = _aggregate(assets, "Mission", ["enterprise", "majcom", "installation", "mission"], mission_reaf)
    installations = _aggregate(assets, "Installation", ["enterprise", "majcom", "installation"], mission_reaf)
    majcoms = _aggregate(assets, "MAJCOM", ["enterprise", "majcom"], mission_reaf)
    enterprise = _aggregate(assets, "Enterprise", ["enterprise"], mission_reaf)
    df = pd.concat([enterprise, majcoms, installations, missions, assets], ignore_index=True)

    df["children_count"] = df["row_id"].map(df.groupby("parent_id").size()).fillna(0).astype(int)
    df = df.sort_values(
        ["enterprise", "majcom", "installation", "mission", "level_rank", "building_asset"],
        na_position="first",
    ).reset_index(drop=True)
    return df.where(df.notna(), None)


def initial_expanded_ids(df: pd.DataFrame) -> set[str]:
    return set(df.loc[df["hierarchy_level"].isin(["Enterprise", "MAJCOM", "Installation"]), "row_id"])


def descendants_for(df: pd.DataFrame, row_id: str) -> pd.DataFrame:
    row = df[df["row_id"] == row_id]
    if row.empty:
        return df.iloc[0:0]
    path = row.iloc[0]["path"]
    mask = df["path"].apply(lambda value: value[: len(path)] == path)
    return df[mask]


def apply_role_scope(df: pd.DataFrame, role: str) -> pd.DataFrame:
    if role == "enterprise":
        return df
    if role == "majcom_acc":
        return df[(df["rbac_majcom"].isna()) | (df["rbac_majcom"] == "ARC")]
    if role == "installation_nellis":
        return df[
            df["hierarchy_level"].isin(["Enterprise", "MAJCOM"])
            | (df["rbac_installation"] == "Talon Point AFB")
        ]
    if role == "mission_nellis_fighter":
        return df[
            df["hierarchy_level"].isin(["Enterprise", "MAJCOM", "Installation"])
            | ((df["rbac_installation"] == "Talon Point AFB") & (df["rbac_mission"] == "Fighter Operations"))
        ]
    if role == "asset_first":
        first_asset = df[df["hierarchy_level"] == "Building/Asset"].iloc[0]
        return df[
            df["hierarchy_level"].isin(["Enterprise", "MAJCOM", "Installation", "Mission"])
            | (df["rbac_asset"] == first_asset["rbac_asset"])
        ]
    return df
