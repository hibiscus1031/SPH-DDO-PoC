#!/usr/bin/env python3
"""Pure prospective semantics for DDO-01E H4 locality decisions."""

from __future__ import annotations

from typing import Any


RUNGS = ("L0", "L1", "L2", "L3")
RUNG_STATUS = {
    "L0": "PARTICLE_LOCAL_INFORMATION_SUFFICIENT",
    "L1": "ONE_HOP_LOCALITY_SUPPORTED",
    "L2": "EXTENDED_BOUNDED_LOCALITY_SUPPORTED",
    "L3": "STRICT_LOCALITY_NOT_SUPPORTED_GLOBAL_CONTEXT_REQUIRED",
}


def locality_verdict(formal_h3: str, rung_evidence: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if formal_h3 == "H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE":
        return {"selected_rung": None, "status": "OBSERVABLE_MAPPING_NOT_IDENTIFIABLE"}
    if formal_h3 != "H3_OBSERVABLE_MAPPING_IDENTIFIABLE":
        return {"selected_rung": None, "status": "H4_LOCALITY_UNRESOLVED"}
    for index, rung in enumerate(RUNGS):
        evidence = rung_evidence.get(rung)
        if not evidence or evidence.get("h3_status") != "H3_OBSERVABLE_MAPPING_IDENTIFIABLE":
            continue
        broader = RUNGS[index + 1:]
        if not broader:
            return {"selected_rung": rung, "status": RUNG_STATUS[rung]}
        if any(name not in evidence.get("paired_degradation", {}) for name in broader):
            continue
        comparisons = [evidence["paired_degradation"][name] for name in broader]
        if all(item["relative_nrmse_upper95"] <= 0.05 and item["cvar_difference_upper95"] <= 0.05 for item in comparisons):
            return {"selected_rung": rung, "status": RUNG_STATUS[rung]}
    return {"selected_rung": None, "status": "H4_LOCALITY_UNRESOLVED"}

