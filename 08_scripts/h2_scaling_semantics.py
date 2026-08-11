#!/usr/bin/env python3
"""Pure deterministic CA-03 H2 scaling semantics; no SPH data access."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from statistics import median
from typing import Any, Iterable, Sequence


PASS = "PASS"
FAIL = "FAIL"
UNRESOLVED = "UNRESOLVED"


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def deterministic_pool_permutation(
    pool: Sequence[Any], domain: str, canonical_pair_track_id: str, count: int
) -> tuple[list[Any], list[dict[str, Any]]]:
    """Select distinct finite-pool values by sequential full-digest modulo."""
    remaining = sorted(pool, key=lambda value: json.dumps(value, sort_keys=True))
    if count < 0 or count > len(remaining):
        raise ValueError("requested distinct count is outside the frozen pool")
    selected: list[Any] = []
    records: list[dict[str, Any]] = []
    for replicate in range(count):
        hash_input = f"{domain}|{canonical_pair_track_id}|r={replicate}"
        digest = sha256_hex(hash_input)
        index = int(digest, 16) % len(remaining)
        value = remaining.pop(index)
        selected.append(value)
        records.append({
            "replicate_id": replicate,
            "hash_input": hash_input,
            "sha256": digest,
            "selected_value": value,
        })
    return selected, records


def log_response_bounds(point: dict[str, Any]) -> dict[str, float]:
    if not bool(point.get("audit_valid", True)):
        raise ValueError("INVALID_MANDATORY_AUDIT")
    target = float(point["T"])
    uncertainty = float(point["U"])
    scale = float(point["S"])
    if not all(math.isfinite(v) for v in (target, uncertainty, scale)):
        raise ValueError("NONFINITE_RESPONSE_INPUT")
    if uncertainty < 0.0 or scale <= 0.0:
        raise ValueError("INVALID_UNCERTAINTY_OR_SCALE")
    if target - uncertainty <= 0.0:
        raise ValueError("LOG_RESPONSE_UNRESOLVED")
    y = target / scale
    y_minus = (target - uncertainty) / scale
    y_plus = (target + uncertainty) / scale
    return {
        "Y": y,
        "Y_minus": y_minus,
        "Y_plus": y_plus,
        "z": math.log(y),
        "z_minus": math.log(y_minus),
        "z_plus": math.log(y_plus),
    }


def local_log_slope(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    xa, xb = float(a["x"]), float(b["x"])
    if not (xa > 0.0 and xb > xa):
        raise ValueError("INVALID_FORMAL_COORDINATE_ORDER")
    za, zb = log_response_bounds(a), log_response_bounds(b)
    denominator = math.log(xb / xa)
    p = (zb["z"] - za["z"]) / denominator
    p_minus = (zb["z_minus"] - za["z_plus"]) / denominator
    p_plus = (zb["z_plus"] - za["z_minus"]) / denominator
    if not all(math.isfinite(v) for v in (p, p_minus, p_plus)):
        raise ValueError("NONFINITE_LOCAL_SLOPE")
    if p_minus > 0.0:
        classification = "EXPECTED_SIGN_SUPPORTED"
    elif p_plus < 0.0:
        classification = "OPPOSITE_SIGN"
    else:
        classification = "PLATEAU_OR_UNCERTAINTY_OVERLAP"
    return {
        "x_a": xa,
        "x_b": xb,
        "replicate_id": a["replicate_id"],
        "p": p,
        "p_minus": p_minus,
        "p_plus": p_plus,
        "classification": classification,
    }


def evaluate_track(
    points: Iterable[dict[str, Any]], *, required_levels: int = 3, required_replicates: int = 3
) -> dict[str, Any]:
    point_list = list(points)
    grouped: dict[float, dict[Any, dict[str, Any]]] = defaultdict(dict)
    try:
        for point in point_list:
            x = float(point["x"])
            replicate = point["replicate_id"]
            if replicate in grouped[x]:
                raise ValueError("DUPLICATE_REPLICATE_AT_LEVEL")
            log_response_bounds(point)
            grouped[x][replicate] = point
        levels = sorted(grouped)
        if len(levels) < required_levels:
            raise ValueError("INSUFFICIENT_LEVELS")
        replicate_sets = [set(grouped[level]) for level in levels]
        if any(len(values) != required_replicates for values in replicate_sets):
            raise ValueError("INSUFFICIENT_REPLICATES")
        if any(values != replicate_sets[0] for values in replicate_sets[1:]):
            raise ValueError("REPLICATE_PAIRING_INTEGRITY_FAILURE")
        replicates = sorted(replicate_sets[0], key=str)
        slopes = []
        for xa, xb in zip(levels[:-1], levels[1:]):
            for replicate in replicates:
                slopes.append(local_log_slope(grouped[xa][replicate], grouped[xb][replicate]))
        supported = sum(item["classification"] == "EXPECTED_SIGN_SUPPORTED" for item in slopes)
        monotonicity = supported / len(slopes)
        dispersions = []
        for level in levels:
            bounds = [log_response_bounds(grouped[level][replicate]) for replicate in replicates]
            dispersions.append(max(item["z_plus"] for item in bounds) - min(item["z_minus"] for item in bounds))
        changes = []
        for xa, xb in zip(levels[:-1], levels[1:]):
            for replicate in replicates:
                za = log_response_bounds(grouped[xa][replicate])
                zb = log_response_bounds(grouped[xb][replicate])
                changes.append(max(0.0, zb["z_minus"] - za["z_plus"], za["z_minus"] - zb["z_plus"]))
        d_t = float(median(dispersions))
        c_t = float(median(changes))
        return {
            "status": "COMPLETE",
            "reason": None,
            "level_count": len(levels),
            "replicate_count": len(replicates),
            "interval_count": len(slopes),
            "supported_interval_count": supported,
            "m_t": monotonicity,
            "D_t": d_t,
            "C_t": c_t,
            "dispersion_gate_pass": d_t < c_t,
            "representative_slope_descriptive": float(median(item["p"] for item in slopes)),
            "local_slopes": slopes,
        }
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return {
            "status": UNRESOLVED,
            "reason": str(exc),
            "level_count": len(grouped),
            "replicate_count": None,
            "interval_count": 0,
            "supported_interval_count": 0,
            "m_t": None,
            "D_t": None,
            "C_t": None,
            "dispersion_gate_pass": None,
            "representative_slope_descriptive": None,
            "local_slopes": [],
        }


def evaluate_family(track_points: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    if len(track_points) < 2:
        return {"verdict": UNRESOLVED, "reason": "INSUFFICIENT_SCIENTIFIC_TRACKS", "M_family": None, "tracks": {}}
    tracks = {name: evaluate_track(points) for name, points in track_points.items()}
    unresolved = [name for name, result in tracks.items() if result["status"] != "COMPLETE"]
    if unresolved:
        return {"verdict": UNRESOLVED, "reason": "TRACK_UNRESOLVED:" + ",".join(unresolved), "M_family": None, "tracks": tracks}
    m_family = sum(result["m_t"] for result in tracks.values()) / len(tracks)
    monotonicity_pass = m_family >= 0.75
    dispersion_pass = all(result["dispersion_gate_pass"] for result in tracks.values())
    return {
        "verdict": PASS if monotonicity_pass and dispersion_pass else FAIL,
        "reason": None if monotonicity_pass and dispersion_pass else (
            "MONOTONICITY_GATE_FAIL" if not monotonicity_pass else "DISPERSION_GATE_FAIL"
        ),
        "M_family": m_family,
        "monotonicity_gate_pass": monotonicity_pass,
        "dispersion_gate_pass": dispersion_pass,
        "tracks": tracks,
    }


def combine_layout_scope(refinement_verdict: str, spectral_verdict: str) -> str:
    if FAIL in (refinement_verdict, spectral_verdict):
        return FAIL
    if refinement_verdict == PASS and spectral_verdict == PASS:
        return PASS
    return UNRESOLVED


def map_component_verdict(
    regular_refinement: str,
    regular_spectral: str,
    jitter_refinement: str,
    jitter_spectral: str,
    *,
    support_ratio_diagnostic: Any = None,
) -> dict[str, str]:
    del support_ratio_diagnostic
    regular = combine_layout_scope(regular_refinement, regular_spectral)
    jitter = combine_layout_scope(jitter_refinement, jitter_spectral)
    if regular == FAIL:
        component = "H2_SCALING_FAIL_REGULAR_SCOPE"
    elif regular == UNRESOLVED:
        component = "H2_SCALING_UNRESOLVED"
    elif jitter == PASS:
        component = "H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT"
    elif jitter == FAIL:
        component = "H2_SCALING_PASS_REGULAR_SCOPE_ONLY"
    else:
        component = "H2_SCALING_PASS_REGULAR_SCOPE_DISORDER_UNRESOLVED"
    return {"regular_scope": regular, "jitter_scope": jitter, "component_verdict": component}


def project_summary(component_verdicts: Sequence[str]) -> str:
    canonical = "H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT"
    regular_only = {
        canonical,
        "H2_SCALING_PASS_REGULAR_SCOPE_ONLY",
        "H2_SCALING_PASS_REGULAR_SCOPE_DISORDER_UNRESOLVED",
    }
    if len(component_verdicts) == 5 and all(value == canonical for value in component_verdicts):
        return "DDO01CR_SPATIAL_DEFECT_SCALING_QUALIFIED"
    if any(value in regular_only for value in component_verdicts) and len(set(component_verdicts)) > 1:
        return "DDO01CR_COMPONENTWISE_SCALING_PARTIALLY_QUALIFIED"
    if len(component_verdicts) == 5 and all(value == "H2_SCALING_FAIL_REGULAR_SCOPE" for value in component_verdicts):
        return "DDO01CR_SCALING_NOT_SUPPORTED"
    return "DDO01CR_SCALING_EVIDENCE_MIXED_OR_UNRESOLVED"
