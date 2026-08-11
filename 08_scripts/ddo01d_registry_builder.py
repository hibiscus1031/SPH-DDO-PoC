#!/usr/bin/env python3
"""Build the exact target-free CA-04 mechanism-stratified 512-case registry."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "06_manifests/ddo01d_case_registry.json"
RESOLUTIONS = (16, 24, 32, 48, 64)
SUPPORT_RATIOS = (2.0, 3.0, 4.0, 5.0)
SINGLE_MODES = ((1, 0), (2, 0), (3, 0), (1, 1), (1, 2), (2, 1))
MULTI_MODE_SETS = (((1, 0), (0, 2)), ((1, 1), (2, -1)), ((1, 0), (2, 1), (0, 3)))
DENSITY_AMPLITUDES = (0.0025, 0.005, 0.01, 0.02)
VELOCITY_AMPLITUDES = (0.025, 0.05, 0.1, 0.2)
PHASES = (0.0, math.pi / 4.0, math.pi / 2.0)
PROBES = ("density", "longitudinal", "transverse")
JITTER_FRACTIONS = (0.0, 0.025, 0.05, 0.1)
JITTER_SEEDS = (20260811, 20260817, 20260823)
FAMILY_QUOTA = 128


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha_rank(domain: str, value: Any) -> str:
    return hashlib.sha256(f"{domain}|{canonical_json(value)}".encode("utf-8")).hexdigest()


def mode_signature(modes: list[list[int]]) -> str:
    return "+".join(f"{mode[0]},{mode[1]}" for mode in modes)


def candidate_valid(candidate: dict[str, Any]) -> bool:
    resolution = int(candidate["resolution_per_axis"])
    ratio = float(candidate["support_over_dx"])
    if ratio / resolution >= 0.5:
        return False
    return all(resolution / math.hypot(*mode) >= 8.0 for mode in candidate["mode_indices"])


def axis_value(candidate: dict[str, Any], axis: str) -> str:
    if axis == "resolution_hdx":
        return f"{candidate['resolution_per_axis']}|{candidate['support_over_dx']}"
    if axis == "probe_mode":
        return f"{candidate['probe']}|{mode_signature(candidate['mode_indices'])}"
    if axis == "probe_amplitude":
        return f"{candidate['probe']}|{candidate['active_amplitude']}"
    if axis == "phase_signature":
        return ",".join(format(value, ".17g") for value in candidate["phases_radians"])
    if axis == "mode_signature":
        return mode_signature(candidate["mode_indices"])
    return str(candidate[axis])


def balanced_select(
    candidates: list[dict[str, Any]], quota: int, axes: tuple[str, ...], domain: str
) -> list[dict[str, Any]]:
    """Greedy marginal-balance selection with target-free SHA-256 tie breaks."""
    if len(candidates) <= quota:
        return sorted(candidates, key=lambda item: sha_rank(domain, item))
    categories = {axis: sorted({axis_value(item, axis) for item in candidates}) for axis in axes}
    counts = {axis: defaultdict(int) for axis in axes}
    remaining = list(candidates)
    selected = []
    for step in range(quota):
        after = step + 1
        scored = []
        for item in remaining:
            deltas = []
            normalized_counts = []
            for axis in axes:
                value = axis_value(item, axis)
                current = counts[axis][value]
                ideal = after / len(categories[axis])
                delta = ((current + 1 - ideal) ** 2 - (current - ideal) ** 2) / max(ideal, 1.0)
                deltas.append(delta)
                normalized_counts.append((current + 1) * len(categories[axis]) / after)
            score = (max(normalized_counts), sum(deltas), sha_rank(domain, item))
            scored.append((score, item))
        _, chosen = min(scored, key=lambda pair: pair[0])
        selected.append(chosen)
        remaining.remove(chosen)
        for axis in axes:
            counts[axis][axis_value(chosen, axis)] += 1
    return selected


def base_candidate(
    family: str,
    resolution: int,
    ratio: float,
    modes: tuple[tuple[int, int], ...],
    probe: str,
    amplitude: float,
    phases: tuple[float, ...],
) -> dict[str, Any]:
    density_amplitude = amplitude if probe == "density" else 0.01
    velocity_amplitude = amplitude if probe != "density" else 0.1
    return {
        "macro_family": family,
        "field_subtype": "multi_mode" if family == "F2" else "single_mode",
        "resolution_per_axis": resolution,
        "support_over_dx": ratio,
        "mode_indices": [list(mode) for mode in modes],
        "probe": probe,
        "polarization": "none" if probe == "density" else probe,
        "active_amplitude": amplitude,
        "density_amplitude": density_amplitude,
        "velocity_amplitude": velocity_amplitude,
        "phases_radians": list(phases),
        "rho0": 1.0,
        "c0": 10.0,
        "kinematic_viscosity": 0.01,
        "dtype": "float64",
        "layout_class": "regular",
        "jitter_fraction": 0.0,
        "jitter_seed": None,
    }


def family_candidates(family: str) -> list[dict[str, Any]]:
    output = []
    if family == "F1":
        mode_sets = tuple((mode,) for mode in SINGLE_MODES)
    elif family == "F2":
        mode_sets = MULTI_MODE_SETS
    elif family == "F3":
        mode_sets = tuple((mode,) for mode in ((1, 1), (1, 2), (2, 1)))
    else:
        raise ValueError(family)
    for resolution in RESOLUTIONS:
        for ratio in SUPPORT_RATIOS:
            for modes in mode_sets:
                for probe in PROBES:
                    amplitudes = DENSITY_AMPLITUDES if probe == "density" else VELOCITY_AMPLITUDES
                    for amplitude in amplitudes:
                        for phase_index in range(len(PHASES)):
                            if family == "F2":
                                phases = tuple(PHASES[(phase_index + index) % len(PHASES)] for index in range(len(modes)))
                            else:
                                phases = (PHASES[phase_index],)
                            candidate = base_candidate(family, resolution, ratio, modes, probe, amplitude, phases)
                            if candidate_valid(candidate):
                                output.append(candidate)
    return output


SELECTION_AXES = (
    "resolution_per_axis",
    "support_over_dx",
    "mode_signature",
    "probe",
    "active_amplitude",
    "phase_signature",
    "resolution_hdx",
    "probe_mode",
    "probe_amplitude",
)


def select_f1_f3(family: str) -> tuple[list[dict[str, Any]], int]:
    candidates = family_candidates(family)
    selected = balanced_select(candidates, FAMILY_QUOTA, SELECTION_AXES, f"DDO01D|{family}|SELECT")
    return selected, len(candidates)


def f4_base_pool() -> list[dict[str, Any]]:
    output = []
    for resolution in RESOLUTIONS:
        for mode in SINGLE_MODES:
            for probe in PROBES:
                amplitudes = DENSITY_AMPLITUDES if probe == "density" else VELOCITY_AMPLITUDES
                for amplitude in amplitudes:
                    for phase in PHASES:
                        candidate = base_candidate("F4", resolution, 4.0, (mode,), probe, amplitude, (phase,))
                        candidate["field_subtype"] = "controlled_disorder_single_mode"
                        if candidate_valid(candidate):
                            output.append(candidate)
    return output


def select_f4() -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    bases = f4_base_pool()
    base_axes = (
        "resolution_per_axis", "mode_signature", "probe", "active_amplitude",
        "phase_signature", "probe_mode", "probe_amplitude",
    )
    selected_bases = balanced_select(bases, 8, base_axes, "DDO01D|F4|BASE_SELECT")
    expanded = []
    for jitter in JITTER_FRACTIONS[1:]:
        ranked = sorted(selected_bases, key=lambda item: sha_rank(f"DDO01D|F4|SEED_ORDER|{jitter}", item))
        for index, item in enumerate(ranked):
            item.setdefault("_seed_by_jitter", {})[format(jitter, ".17g")] = JITTER_SEEDS[index % len(JITTER_SEEDS)]
    for block_index, base in enumerate(sorted(selected_bases, key=lambda item: sha_rank("DDO01D|F4|BLOCK_ORDER", item))):
        block_id = hashlib.sha256(f"DDO01D|F4|BLOCK|{canonical_json(base)}".encode("utf-8")).hexdigest()
        for ratio in SUPPORT_RATIOS:
            for jitter in JITTER_FRACTIONS:
                case = {key: value for key, value in base.items() if key != "_seed_by_jitter"}
                case["support_over_dx"] = ratio
                case["layout_class"] = "regular" if jitter == 0.0 else f"jitter_{format(jitter, '.3g')}"
                case["jitter_fraction"] = jitter
                case["jitter_seed"] = None if jitter == 0.0 else base["_seed_by_jitter"][format(jitter, ".17g")]
                case["f4_matched_block_id"] = block_id
                case["f4_block_index"] = block_index
                if not candidate_valid(case):
                    raise RuntimeError("selected F4 expansion became invalid")
                expanded.append(case)
    if len(expanded) != 128:
        raise RuntimeError("F4 exact block expansion failed")
    clean_bases = [{key: value for key, value in item.items() if key != "_seed_by_jitter"} for item in selected_bases]
    return expanded, len(bases), clean_bases


def add_derived(case: dict[str, Any], case_index: int) -> dict[str, Any]:
    item = dict(case)
    resolution = int(item["resolution_per_axis"])
    ratio = float(item["support_over_dx"])
    dx = 1.0 / resolution
    support = ratio * dx
    wave_numbers = [2.0 * math.pi * math.hypot(*mode) for mode in item["mode_indices"]]
    item.update({
        "case_index": case_index,
        "dx": dx,
        "support_h": support,
        "wave_numbers": wave_numbers,
        "kh_values": [value * support for value in wave_numbers],
        "kh_max": max(value * support for value in wave_numbers),
        "points_per_wavelength_min": min(resolution / math.hypot(*mode) for mode in item["mode_indices"]),
        "data_role": "DEVELOPMENT_ATLAS",
        "component_roles": {
            "density_rate": "PRIMARY_DYNAMIC_TARGET",
            "pressure_gradient_acceleration": "PRIMARY_DYNAMIC_TARGET",
            "viscosity_laplacian_acceleration": "PRIMARY_DYNAMIC_TARGET",
            "total_acceleration": "DERIVED_CLOSURE_DIAGNOSTIC",
            "interpolation_density": "ALGEBRAIC_DENSITY_DIAGNOSTIC",
        },
    })
    identity_payload = {key: value for key, value in item.items() if key not in ("case_index", "component_roles")}
    identity_digest = hashlib.sha256(f"DDO01D|CASE|{canonical_json(identity_payload)}".encode("utf-8")).hexdigest()
    item["canonical_case_id"] = f"DDO01D|{item['macro_family']}|{identity_digest}"
    permutation_input = f"DDO01D|NEIGHBOR_PERMUTATION|{item['canonical_case_id']}"
    permutation_digest = hashlib.sha256(permutation_input.encode("utf-8")).hexdigest()
    item["neighbor_permutation_hash_input"] = permutation_input
    item["neighbor_permutation_sha256"] = permutation_digest
    item["neighbor_permutation_seed"] = int.from_bytes(bytes.fromhex(permutation_digest)[:8], "big") & ((1 << 63) - 1)
    return item


def axis_counts(cases: list[dict[str, Any]], key: Callable[[dict[str, Any]], str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for case in cases:
        counts[key(case)] += 1
    return dict(sorted(counts.items()))


def build_registry() -> dict[str, Any]:
    selected: dict[str, list[dict[str, Any]]] = {}
    candidate_counts = {}
    for family in ("F1", "F2", "F3"):
        selected[family], candidate_counts[family] = select_f1_f3(family)
    selected["F4"], candidate_counts["F4"], f4_bases = select_f4()
    ordered = []
    for family in ("F1", "F2", "F3"):
        ordered.extend(sorted(selected[family], key=lambda item: sha_rank(f"DDO01D|{family}|FINAL_ORDER", item)))
    ordered.extend(sorted(selected["F4"], key=lambda item: (item["f4_block_index"], item["support_over_dx"], item["jitter_fraction"])))
    cases = [add_derived(case, index) for index, case in enumerate(ordered)]
    ids = [case["canonical_case_id"] for case in cases]
    if len(cases) != 512 or len(set(ids)) != 512:
        raise RuntimeError("exact atlas size or uniqueness failure")
    family_counts = axis_counts(cases, lambda item: item["macro_family"])
    if family_counts != {"F1": 128, "F2": 128, "F3": 128, "F4": 128}:
        raise RuntimeError("macro-family quota failure")
    return {
        "schema_version": "1.0",
        "project": "SPH-DDO-PoC",
        "stage": "DDO-01D",
        "registry_status": "FROZEN_BEFORE_TARGET_EVALUATION",
        "generated_date": "2026-08-11",
        "selection_is_target_free": True,
        "historical_h2_cases_count_toward_fresh_quota": False,
        "historical_ddo01cr_registry_path": "06_manifests/ddo01cr_case_registry.json",
        "historical_ddo01cr_registry_sha256": "4b4fca18e95677474319c7ea86ac1a3ccafcc11e101ba28d0817fa2281db5745",
        "fresh_case_budget": 512,
        "family_quota": 128,
        "candidate_counts": candidate_counts,
        "family_counts": family_counts,
        "selection_algorithm": "greedy marginal balance over frozen design axes with domain-separated SHA-256 tie breaks",
        "selection_axes": list(SELECTION_AXES),
        "f4_selected_base_count": 8,
        "f4_selected_base_table": f4_bases,
        "component_roles": cases[0]["component_roles"],
        "case_count": len(cases),
        "axis_balance": {
            family: {
                "resolution": axis_counts([case for case in cases if case["macro_family"] == family], lambda item: str(item["resolution_per_axis"])),
                "support_over_dx": axis_counts([case for case in cases if case["macro_family"] == family], lambda item: format(item["support_over_dx"], ".17g")),
                "probe": axis_counts([case for case in cases if case["macro_family"] == family], lambda item: item["probe"]),
                "mode_signature": axis_counts([case for case in cases if case["macro_family"] == family], lambda item: mode_signature(item["mode_indices"])),
                "active_amplitude": axis_counts([case for case in cases if case["macro_family"] == family], lambda item: format(item["active_amplitude"], ".17g")),
                "layout_class": axis_counts([case for case in cases if case["macro_family"] == family], lambda item: item["layout_class"]),
            }
            for family in ("F1", "F2", "F3", "F4")
        },
        "cases": cases,
    }


def main() -> None:
    registry = build_registry()
    rendered = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    if REGISTRY_PATH.exists():
        if REGISTRY_PATH.read_text() != rendered:
            raise RuntimeError("existing DDO-01D registry differs from deterministic replay")
    else:
        REGISTRY_PATH.write_text(rendered)
    print(json.dumps({
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "registry_sha256": hashlib.sha256(REGISTRY_PATH.read_bytes()).hexdigest(),
        "case_count": registry["case_count"],
        "family_counts": registry["family_counts"],
        "candidate_counts": registry["candidate_counts"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
