"""Synthetic infrastructure hierarchy and metric data for the matrix prototype."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable

import pandas as pd


LEVEL_ORDER = {"Enterprise": 0, "Installation": 1, "Mission": 2, "Building": 3}
LIKELIHOOD_ORDER = {"Low": 1, "Medium": 2, "High": 3}
MATURITY_ORDER = {"Concept": 1, "Scoped": 2, "Programmed": 3, "Validated": 4}
REDUNDANCY_ORDER = {"Single point": 1, "Partial": 2, "Redundant": 3}
EVIDENCE_ORDER = {"Anecdotal": 1, "Limited": 2, "Documented": 3, "Strong": 4}
COST_ORDER = {"Low": 1, "Medium": 2, "High": 3, "Very high": 4}


@dataclass(frozen=True)
class BuildingSeed:
    enterprise: str
    installation: str
    mission: str
    building: str


def _choice(rng: random.Random, values: list[str], weights: list[int] | None = None) -> str:
    return rng.choices(values, weights=weights, k=1)[0]


def _score_for(label: str | None, order: dict[str, int], scale: int = 100) -> int | None:
    if not label:
        return None
    return round(order[label] / max(order.values()) * scale)


def _most_common(values: Iterable[str | None]) -> str | None:
    counts: dict[str, int] = {}
    for value in values:
        if value:
            counts[value] = counts.get(value, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda item: item[1])[0]


def _max_label(values: Iterable[str | None], order: dict[str, int]) -> str | None:
    valid = [value for value in values if value in order]
    if not valid:
        return None
    return max(valid, key=lambda value: order[value])


def _avg(values: Iterable[float | int | None]) -> float | None:
    valid = [value for value in values if value is not None and not pd.isna(value)]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 1)


def _building_rows(seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    enterprises = ["Continental Portfolio", "Pacific Portfolio"]
    installations = {
        "Continental Portfolio": ["Fort Adams", "Camp Meridian", "Base Sentinel"],
        "Pacific Portfolio": ["Joint Station Harbor", "Outpost Summit", "Depot Horizon"],
    }
    missions = ["Power Projection", "Cyber Operations", "Logistics", "Training"]
    source_systems = [" BUILDER SMS", "HQIIS", "ePRISMS", "Manual Survey"]
    gap_categories = ["Capacity", "Resilience", "Compliance", "Safety", "Modernization"]
    strategies = ["REEF: Reduce Demand", "REAF: Harden Critical Node", "REEF: Sequence Sustainment", "REAF: Add Backup Path"]
    gaps_tags = ["Energy", "Water", "Access", "Life Safety", "Mission Assurance"]
    maturity = list(MATURITY_ORDER)
    redundancy = list(REDUNDANCY_ORDER)
    cost = list(COST_ORDER)
    evidence = list(EVIDENCE_ORDER)
    likelihood = list(LIKELIHOOD_ORDER)

    seeds: list[BuildingSeed] = []
    for enterprise in enterprises:
        for installation in installations[enterprise]:
            for mission in rng.sample(missions, 3):
                for idx in range(1, rng.randint(3, 5)):
                    seeds.append(
                        BuildingSeed(
                            enterprise=enterprise,
                            installation=installation,
                            mission=mission,
                            building=f"B{rng.randint(100, 899)}-{idx}",
                        )
                    )

    rows = []
    for index, item in enumerate(seeds, start=1):
        fsrm = _choice(rng, likelihood, [3, 5, 4])
        milcon = _choice(rng, likelihood, [5, 4, 2])
        external = _choice(rng, likelihood, [4, 4, 3])
        plan = _choice(rng, maturity, [4, 5, 4, 2])
        red = _choice(rng, redundancy, [4, 4, 3])
        partial = _choice(rng, ["None", "Partial", "Substantial"], [3, 5, 2])
        cost_scale = _choice(rng, cost, [3, 5, 4, 2])
        evidence_strength = _choice(rng, evidence, [2, 4, 5, 3])
        applies_to_milcon = rng.random() > 0.18
        applies_to_external = rng.random() > 0.12

        rows.append(
            {
                "row_id": f"building-{index}",
                "hierarchy_level": "Building",
                "level_rank": LEVEL_ORDER["Building"],
                "enterprise": item.enterprise,
                "installation": item.installation,
                "mission": item.mission,
                "building": item.building,
                "hierarchy_label": item.building,
                "source_system": _choice(rng, source_systems),
                "gap_category": _choice(rng, gap_categories),
                "reef_reaf_strategy_tag": _choice(rng, strategies),
                "gaps_tag": _choice(rng, gaps_tags),
                "fsrm_likelihood": fsrm,
                "milcon_likelihood": milcon if applies_to_milcon else None,
                "external_funding_likelihood": external if applies_to_external else None,
                "planning_maturity": plan,
                "redundancy_status": red,
                "partial_fulfillment_status": partial,
                "cost_scale": cost_scale,
                "evidence_strength": evidence_strength,
                "fsrm_count": rng.randint(0, 8),
                "milcon_count": rng.randint(0, 4) if applies_to_milcon else None,
                "external_count": rng.randint(0, 5) if applies_to_external else None,
                "planning_doc_count": rng.randint(0, 6),
                "evidence_count": rng.randint(0, 9),
                "rough_order_cost_m": round(rng.uniform(0.4, 28.0), 1),
                "fsrm_score": _score_for(fsrm, LIKELIHOOD_ORDER),
                "milcon_score": _score_for(milcon, LIKELIHOOD_ORDER) if applies_to_milcon else None,
                "external_score": _score_for(external, LIKELIHOOD_ORDER) if applies_to_external else None,
                "planning_score": _score_for(plan, MATURITY_ORDER),
                "redundancy_score": _score_for(red, REDUNDANCY_ORDER),
                "cost_score": _score_for(cost_scale, COST_ORDER),
                "evidence_score": _score_for(evidence_strength, EVIDENCE_ORDER),
                "fsrm_ready_flag": fsrm == "High" and plan in ["Programmed", "Validated"],
                "milcon_ready_flag": applies_to_milcon and milcon == "High" and cost_scale in ["High", "Very high"],
                "external_partner_flag": applies_to_external and external in ["Medium", "High"],
                "planning_gap_flag": plan in ["Concept", "Scoped"],
                "partial_fulfillment_flag": partial in ["Partial", "Substantial"],
                "evidence_gap_flag": evidence_strength in ["Anecdotal", "Limited"],
                "cost_confidence": _choice(rng, ["Low", "Medium", "High"], [2, 4, 4]),
                "reason_evidence_note": f"{_choice(rng, gap_categories)} need from {_choice(rng, source_systems).strip()} with {_choice(rng, evidence).lower()} evidence.",
            }
        )
    return rows


def _aggregate_rows(buildings: pd.DataFrame, level: str, group_cols: list[str]) -> list[dict]:
    rows = []
    for keys, group in buildings.groupby(group_cols, sort=True, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        context = dict(zip(group_cols, keys))
        label = context[group_cols[-1]]
        row_id = f"{level.lower()}-" + "-".join(str(key).replace(" ", "_") for key in keys)

        row = {
            "row_id": row_id,
            "hierarchy_level": level,
            "level_rank": LEVEL_ORDER[level],
            "enterprise": context.get("enterprise"),
            "installation": context.get("installation"),
            "mission": context.get("mission"),
            "building": None,
            "hierarchy_label": label,
            "source_system": _most_common(group["source_system"]),
            "gap_category": _most_common(group["gap_category"]),
            "reef_reaf_strategy_tag": _most_common(group["reef_reaf_strategy_tag"]),
            "gaps_tag": _most_common(group["gaps_tag"]),
            "fsrm_likelihood": _max_label(group["fsrm_likelihood"], LIKELIHOOD_ORDER),
            "milcon_likelihood": _max_label(group["milcon_likelihood"], LIKELIHOOD_ORDER),
            "external_funding_likelihood": _max_label(group["external_funding_likelihood"], LIKELIHOOD_ORDER),
            "planning_maturity": _max_label(group["planning_maturity"], MATURITY_ORDER),
            "redundancy_status": _max_label(group["redundancy_status"], REDUNDANCY_ORDER),
            "partial_fulfillment_status": _most_common(group["partial_fulfillment_status"]),
            "cost_scale": _max_label(group["cost_scale"], COST_ORDER),
            "evidence_strength": _max_label(group["evidence_strength"], EVIDENCE_ORDER),
            "fsrm_count": int(group["fsrm_count"].fillna(0).sum()),
            "milcon_count": int(group["milcon_count"].fillna(0).sum()),
            "external_count": int(group["external_count"].fillna(0).sum()),
            "planning_doc_count": int(group["planning_doc_count"].fillna(0).sum()),
            "evidence_count": int(group["evidence_count"].fillna(0).sum()),
            "rough_order_cost_m": round(group["rough_order_cost_m"].fillna(0).sum(), 1),
            "fsrm_score": _avg(group["fsrm_score"]),
            "milcon_score": _avg(group["milcon_score"]),
            "external_score": _avg(group["external_score"]),
            "planning_score": _avg(group["planning_score"]),
            "redundancy_score": _avg(group["redundancy_score"]),
            "cost_score": _avg(group["cost_score"]),
            "evidence_score": _avg(group["evidence_score"]),
            "fsrm_ready_flag": bool(group["fsrm_ready_flag"].any()),
            "milcon_ready_flag": bool(group["milcon_ready_flag"].any()),
            "external_partner_flag": bool(group["external_partner_flag"].any()),
            "planning_gap_flag": bool(group["planning_gap_flag"].any()),
            "partial_fulfillment_flag": bool(group["partial_fulfillment_flag"].any()),
            "evidence_gap_flag": bool(group["evidence_gap_flag"].any()),
            "cost_confidence": _most_common(group["cost_confidence"]),
            "reason_evidence_note": f"Aggregate of {len(group)} building records; values show max status or summed counts.",
        }
        if level == "Enterprise":
            row["installation"] = None
            row["mission"] = None
        if level == "Installation":
            row["mission"] = None
        rows.append(row)
    return rows


def build_synthetic_data() -> pd.DataFrame:
    buildings = pd.DataFrame(_building_rows())
    aggregate_rows = []
    aggregate_rows.extend(_aggregate_rows(buildings, "Enterprise", ["enterprise"]))
    aggregate_rows.extend(_aggregate_rows(buildings, "Installation", ["enterprise", "installation"]))
    aggregate_rows.extend(_aggregate_rows(buildings, "Mission", ["enterprise", "installation", "mission"]))

    df = pd.concat([pd.DataFrame(aggregate_rows), buildings], ignore_index=True)
    df = df.sort_values(
        ["enterprise", "installation", "mission", "level_rank", "building"],
        na_position="first",
    ).reset_index(drop=True)
    return df
