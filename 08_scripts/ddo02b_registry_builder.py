#!/usr/bin/env python3
"""Build the target-free, fresh-lineage 384-case DDO-02B registry."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_manifests/ddo02b_case_registry.json"
OLD = ROOT / "06_manifests/ddo01d_case_registry.json"
CA06 = ROOT / "06_manifests/ca06_manifest.json"
RESOLUTIONS = (16, 24, 32, 48, 64)
RATIOS = (2.0, 3.0, 4.0, 5.0)
SINGLE = ((1, 0), (2, 0), (3, 0), (1, 1), (1, 2), (2, 1))
MULTI = (((1, 0), (0, 2)), ((1, 1), (2, -1)), ((1, 0), (2, 1), (0, 3)))
DENSITY_A = (.0025, .005, .01, .02)
VELOCITY_A = (.025, .05, .1, .2)
PHASES = (math.pi/7, 3*math.pi/7, 5*math.pi/7)
PROBES = ("density", "longitudinal", "transverse")
JITTERS = (0.0, .025, .05, .1)
SEEDS = (20260901, 20260907, 20260913)
QUOTA = 96


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def rank(domain: str, value: Any) -> str:
    return hashlib.sha256(f"{domain}|{canonical(value)}".encode()).hexdigest()


def mode_sig(value: dict[str, Any]) -> str:
    return "+".join(f"{x},{y}" for x, y in value["mode_indices"])


def axis(value: dict[str, Any], name: str) -> str:
    if name == "mode": return mode_sig(value)
    if name == "resolution_hdx": return f"{value['resolution_per_axis']}|{value['support_over_dx']}"
    if name == "probe_mode": return f"{value['probe']}|{mode_sig(value)}"
    if name == "phase": return ",".join(format(x, ".17g") for x in value["phases_radians"])
    return str(value[name])


def valid(value: dict[str, Any]) -> bool:
    n, ratio = value["resolution_per_axis"], value["support_over_dx"]
    return ratio/n < .5 and all(n/math.hypot(*m) >= 8 for m in value["mode_indices"])


def base(family: str, n: int, ratio: float, modes: tuple[tuple[int, int], ...],
         probe: str, amplitude: float, phases: tuple[float, ...]) -> dict[str, Any]:
    return {
        "macro_family": family, "field_subtype": "multi_mode" if family == "F2" else "single_mode",
        "resolution_per_axis": n, "support_over_dx": ratio, "mode_indices": [list(m) for m in modes],
        "probe": probe, "polarization": "none" if probe == "density" else probe,
        "active_amplitude": amplitude, "density_amplitude": amplitude if probe == "density" else .01,
        "velocity_amplitude": amplitude if probe != "density" else .1, "phases_radians": list(phases),
        "rho0": 1.0, "c0": 10.0, "kinematic_viscosity": .01, "dtype": "float64",
        "layout_class": "regular", "jitter_fraction": 0.0, "jitter_seed": None,
    }


def candidates(family: str) -> list[dict[str, Any]]:
    mode_sets = tuple((m,) for m in SINGLE) if family == "F1" else MULTI if family == "F2" else tuple((m,) for m in ((1,1),(1,2),(2,1)))
    out = []
    for n in RESOLUTIONS:
        for ratio in RATIOS:
            for modes in mode_sets:
                for probe in PROBES:
                    amplitudes = DENSITY_A if probe == "density" else VELOCITY_A
                    for amplitude in amplitudes:
                        for k in range(3):
                            phases = tuple(PHASES[(k+i) % 3] for i in range(len(modes))) if family == "F2" else (PHASES[k],)
                            value = base(family, n, ratio, modes, probe, amplitude, phases)
                            if valid(value): out.append(value)
    return out


def balanced(pool: list[dict[str, Any]], quota: int, axes: tuple[str, ...], domain: str) -> list[dict[str, Any]]:
    categories = {name: sorted({axis(v, name) for v in pool}) for name in axes}
    counts = {name: defaultdict(int) for name in axes}
    remaining, selected = list(pool), []
    for step in range(quota):
        after = step+1
        def score(item: dict[str, Any]) -> tuple[Any, ...]:
            normalized, deltas = [], []
            for name in axes:
                current = counts[name][axis(item, name)]
                ideal = after/len(categories[name])
                normalized.append((current+1)*len(categories[name])/after)
                deltas.append(((current+1-ideal)**2-(current-ideal)**2)/max(ideal,1))
            return max(normalized), sum(deltas), rank(domain, item)
        chosen = min(remaining, key=score)
        selected.append(chosen); remaining.remove(chosen)
        for name in axes: counts[name][axis(chosen, name)] += 1
    return selected


AXES = ("resolution_per_axis", "support_over_dx", "mode", "probe", "active_amplitude", "phase", "resolution_hdx", "probe_mode")


def f4() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pool = []
    for n in RESOLUTIONS:
        for mode in SINGLE:
            for probe in PROBES:
                for amplitude in DENSITY_A if probe == "density" else VELOCITY_A:
                    for phase in PHASES:
                        value = base("F4", n, 4.0, (mode,), probe, amplitude, (phase,))
                        value["field_subtype"] = "controlled_disorder_single_mode"
                        if valid(value): pool.append(value)
    bases = balanced(pool, 6, ("resolution_per_axis", "mode", "probe", "active_amplitude", "phase", "probe_mode"), "DDO02B|F4|BASE")
    expanded = []
    for block_index, item in enumerate(sorted(bases, key=lambda v: rank("DDO02B|F4|BLOCK", v))):
        block_id = hashlib.sha256(("DDO02B|F4|"+canonical(item)).encode()).hexdigest()
        for ratio in RATIOS:
            for ji, jitter in enumerate(JITTERS):
                value = dict(item); value["support_over_dx"] = ratio; value["jitter_fraction"] = jitter
                value["layout_class"] = "regular" if jitter == 0 else f"jitter_{jitter:.3g}"
                value["jitter_seed"] = None if jitter == 0 else SEEDS[(block_index+ji) % len(SEEDS)]
                value["f4_matched_block_id"] = block_id; value["f4_block_index"] = block_index
                if not valid(value): raise RuntimeError("invalid F4 expansion")
                expanded.append(value)
    if len(expanded) != 96: raise RuntimeError("F4 quota failure")
    return expanded, bases


def derived(value: dict[str, Any], index: int) -> dict[str, Any]:
    item = dict(value); n, ratio = int(item["resolution_per_axis"]), float(item["support_over_dx"])
    h = ratio/n; ks = [2*math.pi*math.hypot(*m) for m in item["mode_indices"]]
    item.update({
        "case_index": index, "dx": 1/n, "support_h": h, "wave_numbers": ks,
        "kh_values": [k*h for k in ks], "kh_max": max(k*h for k in ks),
        "points_per_wavelength_min": min(n/math.hypot(*m) for m in item["mode_indices"]),
        "data_role": "FRESH_FORMAL_H3_H4_QUALIFICATION_EVIDENCE",
        "component_roles": {"density_rate":"PRIMARY_DYNAMIC_TARGET", "pressure_gradient_acceleration":"PRIMARY_DYNAMIC_TARGET",
                            "viscosity_laplacian_acceleration":"PRIMARY_DYNAMIC_TARGET", "total_acceleration":"DERIVED_CLOSURE_DIAGNOSTIC",
                            "interpolation_density":"ALGEBRAIC_DENSITY_DIAGNOSTIC"},
    })
    payload = {k:v for k,v in item.items() if k not in ("case_index","component_roles")}
    digest = hashlib.sha256(("DDO02B|CASE|"+canonical(payload)).encode()).hexdigest()
    item["canonical_case_id"] = f"DDO02B|{item['macro_family']}|{digest}"
    p = hashlib.sha256(("DDO02B|NEIGHBOR_PERMUTATION|"+item["canonical_case_id"]).encode()).hexdigest()
    item["neighbor_permutation_hash_input"] = "DDO02B|NEIGHBOR_PERMUTATION|"+item["canonical_case_id"]
    item["neighbor_permutation_sha256"] = p
    item["neighbor_permutation_seed"] = int.from_bytes(bytes.fromhex(p)[:8], "big") & ((1<<63)-1)
    return item


def lineage_payload(case: dict[str, Any]) -> str:
    keys = ("macro_family","field_subtype","mode_indices","phases_radians","probe","polarization","active_amplitude")
    return canonical({key:case[key] for key in keys})


def main() -> None:
    if not CA06.exists() or json.loads(CA06.read_text()).get("terminal_status") != "DDO_CA06_EXPANDED_OBSERVABLE_CONTRACT_FROZEN":
        raise RuntimeError("CA-06 must be frozen before DDO-02B registry")
    selected = {f: balanced(candidates(f), QUOTA, AXES, f"DDO02B|{f}|SELECT") for f in ("F1","F2","F3")}
    selected["F4"], bases = f4()
    ordered = []
    for family in ("F1","F2","F3"):
        ordered.extend(sorted(selected[family], key=lambda v: rank(f"DDO02B|{family}|ORDER", v)))
    ordered.extend(sorted(selected["F4"], key=lambda v: (v["f4_block_index"],v["support_over_dx"],v["jitter_fraction"])))
    cases = [derived(value, i) for i,value in enumerate(ordered)]
    old = json.loads(OLD.read_text())
    old_payloads = {lineage_payload(c) for c in old["cases"]}
    overlap = sum(lineage_payload(c) in old_payloads for c in cases)
    family_counts = dict(Counter(c["macro_family"] for c in cases))
    if len(cases) != 384 or overlap or family_counts != {"F1":96,"F2":96,"F3":96,"F4":96}:
        raise RuntimeError("freshness or balance failure")
    registry = {
        "schema_version":"1.0", "stage":"DDO-02B", "registry_status":"FROZEN_BEFORE_FRESH_TARGET_EVALUATION",
        "selection_is_target_free":True, "fresh_case_budget":384, "family_quota":96,
        "family_counts":family_counts, "old_ddo01d_lineage_overlap_count":overlap,
        "fresh_phase_set_radians":list(PHASES), "fresh_disorder_seeds":list(SEEDS),
        "ca06_manifest_sha256":hashlib.sha256(CA06.read_bytes()).hexdigest(), "f4_selected_base_count":6,
        "case_count":384, "cases":cases,
    }
    OUT.write_text(json.dumps(registry, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"registry_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(), "family_counts":family_counts,
                      "old_lineage_overlap_count":overlap}, indent=2, sort_keys=True))


if __name__ == "__main__":
    from collections import Counter
    main()
