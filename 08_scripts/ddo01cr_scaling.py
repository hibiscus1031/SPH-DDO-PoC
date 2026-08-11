#!/usr/bin/env python3
"""Execute fresh DDO-01C-R CA-01 audits and CA-03 H2-only analysis."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
import scipy
import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))
sys.path.insert(0, str(ROOT / "01_imported_baseline"))

from ddo01a_preflight import (  # noqa: E402
    configure_determinism,
    continuum_components,
    defects,
    discrete_components,
    evaluator_a,
    evaluator_b,
    linf_difference,
    permute_neighborhood,
)
from ddo01ar_requalification import (  # noqa: E402
    C_FP,
    EPS64,
    FROZEN_SCALES,
    SOURCE_EXPECTED,
    characteristic_scale,
    compensated_discrete_components,
    continuum_sph_channels,
    derivative_sph_channels,
    independent_geometry_neighborhood,
    target_analytic_and_sph,
    topology_keys,
)
from h1_signal_semantics import scalar_case_rms, vector_case_rms  # noqa: E402
from h2_scaling_semantics import (  # noqa: E402
    evaluate_family,
    local_log_slope,
    map_component_verdict,
    project_summary,
)
from structure_preserving.neighborhood import (  # noqa: E402
    PeriodicNeighborhood,
    audit_periodic_neighborhood,
    build_periodic_neighborhood,
    periodic_cartesian_layout,
    tensor_sha256,
)


REGISTRY_PATH = ROOT / "06_manifests/ddo01cr_case_registry.json"
CA03_PATH = ROOT / "06_manifests/ca03_manifest.json"
REGISTRY_SHA256 = "4b4fca18e95677474319c7ea86ac1a3ccafcc11e101ba28d0817fa2281db5745"
CA03_SHA256 = "321b37f81ddd81c2407f81dd17825e64e605a603f5f70ec324d0a1663a9acd3c"

DATA_DIR = ROOT / "data/scaling_f1"
CHECKPOINT_PATH = DATA_DIR / "ddo01cr_case_checkpoint.jsonl"
EVIDENCE_JSON = DATA_DIR / "ddo01cr_scaling_evidence.json"
EVIDENCE_CSV = DATA_DIR / "ddo01cr_scaling_evidence.csv"

COMPONENT_MAP = {
    "interpolation_density": "interpolation_density",
    "density_rate": "density_rate",
    "pressure_gradient_acceleration": "pressure",
    "viscosity_laplacian_acceleration": "viscosity",
    "total_acceleration": "acceleration",
}
VECTOR_COMPONENTS = {
    "pressure_gradient_acceleration",
    "viscosity_laplacian_acceleration",
    "total_acceleration",
}
COMPONENT_SCALES = {
    "interpolation_density": 1.0,
    "density_rate": 0.1,
    "pressure_gradient_acceleration": 0.01,
    "viscosity_laplacian_acceleration": 0.01,
    "total_acceleration": 0.01,
}
UNITS = {
    "interpolation_density": "M L^-2",
    "density_rate": "M L^-2 T^-1",
    "pressure_gradient_acceleration": "L T^-2",
    "viscosity_laplacian_acceleration": "L T^-2",
    "total_acceleration": "L T^-2",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rms(value: torch.Tensor, vector: bool) -> float:
    array = value.detach().cpu().numpy()
    return vector_case_rms(array) if vector else scalar_case_rms(array)


def geometry_descriptors(positions: torch.Tensor, dx: float, neighborhood: Any) -> dict[str, Any]:
    nonself = neighborhood.row != neighborhood.col
    row = neighborhood.row[nonself]
    disp = neighborhood.displacement[nonself]
    dist = neighborhood.distance[nonself]
    count = neighborhood.particle_count
    ones = torch.ones_like(dist)
    counts = torch.zeros(count, dtype=positions.dtype).index_add_(0, row, ones)
    sx = torch.zeros(count, dtype=positions.dtype).index_add_(0, row, disp[:, 0] * disp[:, 0])
    sy = torch.zeros(count, dtype=positions.dtype).index_add_(0, row, disp[:, 1] * disp[:, 1])
    sxy = torch.zeros(count, dtype=positions.dtype).index_add_(0, row, disp[:, 0] * disp[:, 1])
    safe = counts.clamp_min(1.0)
    a, d, b = sx / safe, sy / safe, sxy / safe
    trace = a + d
    radical = torch.sqrt(torch.clamp((a - d) ** 2 + 4.0 * b**2, min=0.0))
    anisotropy = radical / (trace + torch.finfo(positions.dtype).eps)
    sum_d = torch.zeros(count, dtype=positions.dtype).index_add_(0, row, dist)
    sum_d2 = torch.zeros(count, dtype=positions.dtype).index_add_(0, row, dist * dist)
    mean_d = sum_d / safe
    var_d = torch.clamp(sum_d2 / safe - mean_d**2, min=0.0)
    cv = torch.sqrt(var_d) / (mean_d + torch.finfo(positions.dtype).eps)
    resolution = round(math.sqrt(count))
    axis = (torch.arange(resolution, dtype=positions.dtype) + 0.5) * dx
    gx, gy = torch.meshgrid(axis, axis, indexing="ij")
    nominal = torch.stack((gx.reshape(-1), gy.reshape(-1)), dim=-1)
    displacement = torch.remainder(positions - nominal + 0.5, 1.0) - 0.5
    jitter_rms = float(torch.sqrt(torch.mean(torch.sum(displacement**2, dim=1))) / dx)
    return {
        "neighbor_count_min": int(counts.min()),
        "neighbor_count_median": float(torch.median(counts)),
        "neighbor_count_mean": float(torch.mean(counts)),
        "neighbor_count_max": int(counts.max()),
        "covariance_anisotropy_median": float(torch.median(anisotropy)),
        "covariance_anisotropy_max": float(torch.max(anisotropy)),
        "neighbor_distance_cv_median": float(torch.median(cv)),
        "jitter_displacement_rms_over_dx": jitter_rms,
    }


class GeometryCache:
    def __init__(self) -> None:
        self.values: dict[tuple[Any, ...], dict[str, Any]] = {}

    def get(self, entry: dict[str, Any]) -> dict[str, Any]:
        key = (
            int(entry["resolution_per_axis"]),
            float(entry["support_over_dx"]),
            str(entry["layout_class"]),
            int(entry["jitter_seed"] or 0),
        )
        if key in self.values:
            return self.values[key]
        resolution, ratio, _layout, seed = key
        jitter = float(entry["jitter_fraction"])
        positions, dx, layout_hash = periodic_cartesian_layout(
            resolution,
            jitter_fraction=jitter,
            seed=seed,
            dtype=torch.float64,
            domain_minimum=(0.0, 0.0),
            domain_maximum=(1.0, 1.0),
        )
        support = ratio * dx
        primary = build_periodic_neighborhood(
            positions, support, domain_minimum=(0.0, 0.0), domain_maximum=(1.0, 1.0)
        )
        topology = audit_periodic_neighborhood(positions, primary)
        independent = independent_geometry_neighborhood(positions, support)
        primary_keys = topology_keys(primary)
        independent_keys = topology_keys(independent)
        independent_unique = int(torch.unique(independent_keys).numel()) == int(independent_keys.numel())
        independent_reciprocal = bool(torch.equal(
            independent_keys,
            torch.sort(independent.col * independent.particle_count + independent.row).values,
        ))
        positions32 = positions.to(torch.float32)
        float32_topology_method = "independent_float32_rebuild"
        float32_topology_rebuild_error = None
        try:
            primary32 = build_periodic_neighborhood(
                positions32, support, domain_minimum=(0.0, 0.0), domain_maximum=(1.0, 1.0)
            )
        except RuntimeError as exc:
            # CA-01 makes float32 degradation explicitly diagnostic and
            # non-gating. Preserve the valid primary edge set to isolate the
            # arithmetic precision change when a float32 graph rebuild loses
            # reciprocity at a support-boundary rounding case.
            float32_topology_method = "primary_float64_topology_cast_to_float32"
            float32_topology_rebuild_error = str(exc)
            primary32 = PeriodicNeighborhood(
                row=primary.row,
                col=primary.col,
                displacement=primary.displacement.to(torch.float32),
                distance=primary.distance.to(torch.float32),
                edge_support=primary.edge_support.to(torch.float32),
                particle_support=primary.particle_support.to(torch.float32),
                domain_min=primary.domain_min.to(torch.float32),
                domain_max=primary.domain_max.to(torch.float32),
                particle_count=primary.particle_count,
            )
        result = {
            "positions": positions,
            "dx": dx,
            "support": support,
            "layout_sha256": layout_hash,
            "primary": primary,
            "independent": independent,
            "primary32": primary32,
            "positions32": positions32,
            "float32_topology_method": float32_topology_method,
            "float32_topology_rebuild_error": float32_topology_rebuild_error,
            "topology": topology,
            "primary_keys": primary_keys,
            "independent_keys": independent_keys,
            "independent_unique": independent_unique,
            "independent_reciprocal": independent_reciprocal,
            "topology_equal": bool(torch.equal(primary_keys, independent_keys)),
            "descriptors": geometry_descriptors(positions, dx, primary),
        }
        self.values[key] = result
        print(f"geometry_ready N={resolution} hdx={ratio:g} layout={entry['layout_class']} seed={seed}", flush=True)
        return result


def run_case(entry: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any]:
    positions = geometry["positions"]
    dx = float(geometry["dx"])
    support = float(geometry["support"])
    primary = geometry["primary"]
    independent = geometry["independent"]
    mode = tuple(int(value) for value in entry["mode_index"])
    probe = str(entry["probe"])
    phase = float(entry["phase_radians"])
    density_amplitude = float(entry["density_amplitude"])
    velocity_amplitude = float(entry["velocity_amplitude"])
    kwargs = {
        "density_amplitude": density_amplitude,
        "velocity_amplitude": velocity_amplitude,
        "phase": phase,
    }
    derivative_a = evaluator_a(positions, probe, mode, **kwargs)
    derivative_b = evaluator_b(positions, probe, mode, **kwargs)
    nu = 0.01
    mass = dx**2
    continuum_a = continuum_components(derivative_a, nu=nu)
    continuum_b = continuum_components(derivative_b, nu=nu)
    primary_discrete = discrete_components(
        primary, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    primary_target = defects(continuum_a, primary_discrete)
    reference_target = defects(continuum_b, primary_discrete)
    repeat_discrete = discrete_components(
        primary, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    repeat_target = defects(continuum_a, repeat_discrete)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(entry["neighbor_permutation_seed"]))
    permutation = torch.randperm(primary.row.numel(), generator=generator)
    permuted = permute_neighborhood(primary, permutation)
    permuted_discrete = discrete_components(
        permuted, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    permuted_target = defects(continuum_a, permuted_discrete)
    compensated_discrete = compensated_discrete_components(
        primary, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    compensated_target = defects(continuum_a, compensated_discrete)
    geometry_discrete = discrete_components(
        independent, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    geometry_target = defects(continuum_a, geometry_discrete)
    derivative32 = evaluator_a(geometry["positions32"], probe, mode, **kwargs)
    continuum32 = continuum_components(derivative32, nu=nu)
    discrete32 = discrete_components(
        geometry["primary32"], derivative32["rho"], derivative32["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    target32 = defects(continuum32, discrete32)

    sph_derivative = derivative_sph_channels(derivative_a, primary_discrete, primary, mass=mass, nu=nu)
    derivative_gates = {}
    for name in derivative_a:
        scale = characteristic_scale(FROZEN_SCALES[name], derivative_a[name], sph_derivative[name])
        discrepancy = linf_difference(derivative_a[name], derivative_b[name])
        gate = C_FP * EPS64 * scale
        derivative_gates[name] = {
            "absolute_discrepancy": discrepancy,
            "physical_scale": scale,
            "gate": gate,
            "gate_fraction": discrepancy / gate,
            "pass": discrepancy <= gate,
        }
    continuum_sph = continuum_sph_channels(primary_discrete)
    continuum_scale_keys = {
        "density": "continuum_density",
        "density_rate": "continuum_density_rate",
        "pressure_acceleration": "continuum_pressure_acceleration",
        "viscosity_acceleration": "continuum_viscosity_acceleration",
        "acceleration": "continuum_acceleration",
    }
    continuum_gates = {}
    for name in continuum_a:
        scale = characteristic_scale(FROZEN_SCALES[continuum_scale_keys[name]], continuum_a[name], continuum_sph[name])
        discrepancy = linf_difference(continuum_a[name], continuum_b[name])
        gate = C_FP * EPS64 * scale
        continuum_gates[name] = {
            "absolute_discrepancy": discrepancy,
            "physical_scale": scale,
            "gate": gate,
            "gate_fraction": discrepancy / gate,
            "pass": discrepancy <= gate,
        }

    identity = linf_difference(primary_target["acceleration"], primary_target["pressure"] + primary_target["viscosity"])
    frozen_target_key = {
        "interpolation_density": "interpolation_density",
        "density_rate": "density_rate",
        "pressure": "target_pressure",
        "viscosity": "target_viscosity",
        "acceleration": "target_acceleration",
    }
    uncertainties = {}
    components = {}
    for canonical, internal in COMPONENT_MAP.items():
        analytic_value, sph_value = target_analytic_and_sph(internal, continuum_a, primary_discrete)
        physical_scale = characteristic_scale(FROZEN_SCALES[frozen_target_key[internal]], analytic_value, sph_value)
        u_round = C_FP * EPS64 * physical_scale
        delta_ref = linf_difference(primary_target[internal], reference_target[internal])
        delta_repeat = linf_difference(primary_target[internal], repeat_target[internal])
        delta_perm = linf_difference(primary_target[internal], permuted_target[internal])
        delta_comp = linf_difference(primary_target[internal], compensated_target[internal])
        delta_accum = max(delta_perm, delta_comp)
        delta_geometry = linf_difference(primary_target[internal], geometry_target[internal])
        delta_identity = identity if internal == "acceleration" else 0.0
        u_num = u_round + delta_ref + delta_repeat + delta_accum + delta_geometry + delta_identity
        sign_residual = linf_difference(sph_value + primary_target[internal], analytic_value)
        target_rms = rms(primary_target[internal], canonical in VECTOR_COMPONENTS)
        continuum_rms = rms(analytic_value, canonical in VECTOR_COMPONENTS)
        component_scale = COMPONENT_SCALES[canonical]
        e_rel = target_rms / max(continuum_rms, u_round)
        uncertainties[canonical] = {
            "units": UNITS[canonical],
            "physical_scale": physical_scale,
            "U_round": u_round,
            "Delta_ref": delta_ref,
            "Delta_repeat": delta_repeat,
            "Delta_perm": delta_perm,
            "Delta_comp": delta_comp,
            "Delta_accum": delta_accum,
            "Delta_geometry": delta_geometry,
            "Delta_identity": delta_identity,
            "U_num": u_num,
            "positive_additive_sign_residual": sign_residual,
            "positive_additive_sign_pass": sign_residual <= u_num,
            "precision_degradation_diagnostic": linf_difference(primary_target[internal], target32[internal].double()),
            "precision_degradation_in_U_num": False,
            "all_terms_finite": bool(np.isfinite([
                u_round, delta_ref, delta_repeat, delta_perm, delta_comp,
                delta_accum, delta_geometry, delta_identity, u_num, sign_residual,
            ]).all()),
        }
        components[canonical] = {
            "target_rms": target_rms,
            "component_scale": component_scale,
            "normalized_target_Y": target_rms / component_scale,
            "U_num": u_num,
            "normalized_uncertainty_u": u_num / component_scale,
            "Y_minus": (target_rms - u_num) / component_scale,
            "Y_plus": (target_rms + u_num) / component_scale,
            "log_response_admissible": target_rms - u_num > 0.0,
            "continuum_operator_rms": continuum_rms,
            "relative_effect_E_rel": e_rel,
            "relative_effect_label": "DESCRIPTIVE_NOT_H2_GATE",
        }

    topology_failure_fields = (
        "duplicate_edge_count", "missing_self_edge_count", "nonreciprocal_nonself_edge_count",
        "out_of_bounds_edge_count", "omitted_strict_support_edge_count", "unexpected_edge_count",
    )
    topology_pass = all(int(geometry["topology"][name]) == 0 for name in topology_failure_fields)
    independent_pass = geometry["independent_unique"] and geometry["independent_reciprocal"] and geometry["topology_equal"]
    derivative_pass = all(item["pass"] for item in derivative_gates.values())
    continuum_pass = all(item["pass"] for item in continuum_gates.values())
    uncertainty_pass = all(item["all_terms_finite"] and item["positive_additive_sign_pass"] for item in uncertainties.values())
    closure_bound = (
        uncertainties["total_acceleration"]["U_num"]
        + uncertainties["pressure_gradient_acceleration"]["U_num"]
        + uncertainties["viscosity_laplacian_acceleration"]["U_num"]
    )
    closure_pass = identity <= closure_bound
    mandatory_pass = topology_pass and independent_pass and derivative_pass and continuum_pass and uncertainty_pass and closure_pass
    return {
        "case_index": entry["case_index"],
        "canonical_case_id": entry["canonical_case_id"],
        "regular_disorder_pair_id": entry["regular_disorder_pair_id"],
        "track_template": entry["track_template"],
        "probe": probe,
        "polarization": entry["polarization"],
        "density_amplitude": density_amplitude,
        "velocity_amplitude": velocity_amplitude,
        "resolution_per_axis": entry["resolution_per_axis"],
        "particle_count": int(positions.shape[0]),
        "dx": dx,
        "support_h": support,
        "support_over_dx": entry["support_over_dx"],
        "mode_index": entry["mode_index"],
        "kh": entry["kh"],
        "points_per_wavelength": entry["points_per_wavelength"],
        "replicate_id": entry["replicate_id"],
        "phase_radians": phase,
        "layout_class": entry["layout_class"],
        "jitter_fraction": entry["jitter_fraction"],
        "jitter_seed": entry["jitter_seed"],
        "family_labels": entry["family_labels"],
        "layout_sha256": geometry["layout_sha256"],
        "primary_edge_key_sha256": tensor_sha256(geometry["primary_keys"]),
        "independent_edge_key_sha256": tensor_sha256(geometry["independent_keys"]),
        "geometry_descriptors": geometry["descriptors"],
        "precision_degradation_topology_method": geometry["float32_topology_method"],
        "precision_degradation_topology_rebuild_error": geometry["float32_topology_rebuild_error"],
        "topology": geometry["topology"],
        "independent_geometry": {
            "unique": geometry["independent_unique"],
            "reciprocal": geometry["independent_reciprocal"],
            "edge_keys_equal_primary": geometry["topology_equal"],
        },
        "derivative_gates": derivative_gates,
        "continuum_gates": continuum_gates,
        "uncertainty": uncertainties,
        "component_closure": {"residual": identity, "bound": closure_bound, "pass": closure_pass},
        "mandatory_audit": {
            "primary_topology_pass": topology_pass,
            "independent_topology_pass": independent_pass,
            "derivative_pass": derivative_pass,
            "continuum_pass": continuum_pass,
            "uncertainty_and_sign_pass": uncertainty_pass,
            "component_closure_pass": closure_pass,
            "mandatory_case_pass": mandatory_pass,
        },
        "components": components,
    }


def load_checkpoint(registry: dict[str, Any]) -> list[dict[str, Any]]:
    if not CHECKPOINT_PATH.exists():
        return []
    rows = [json.loads(line) for line in CHECKPOINT_PATH.read_text().splitlines() if line.strip()]
    for index, row in enumerate(rows):
        if row["case_index"] != index or row["canonical_case_id"] != registry["cases"][index]["canonical_case_id"]:
            raise RuntimeError("checkpoint is not a canonical registry prefix")
    return rows


def formal_analysis(cases: list[dict[str, Any]], registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    by_component: dict[str, Any] = {}
    verdicts: dict[str, str] = {}
    for component, mandatory_tracks in registry["mandatory_component_tracks"].items():
        family_layout = {}
        for family in ("REFINEMENT_H", "SPECTRAL_KH"):
            for layout in ("regular", "jitter_0.05"):
                tracks: dict[str, list[dict[str, Any]]] = {}
                for track in mandatory_tracks:
                    selected = [
                        case for case in cases
                        if family in case["family_labels"]
                        and case["layout_class"] == layout
                        and case["track_template"] == track
                    ]
                    points = []
                    for case in selected:
                        comp = case["components"][component]
                        points.append({
                            "x": case["support_h"] if family == "REFINEMENT_H" else case["kh"],
                            "replicate_id": case["replicate_id"],
                            "T": comp["target_rms"],
                            "U": comp["U_num"],
                            "S": comp["component_scale"],
                            "audit_valid": case["mandatory_audit"]["mandatory_case_pass"],
                            "case_id": case["canonical_case_id"],
                        })
                    tracks[track] = points
                family_layout[f"{family}|{layout}"] = evaluate_family(tracks)
        mapped = map_component_verdict(
            family_layout["REFINEMENT_H|regular"]["verdict"],
            family_layout["SPECTRAL_KH|regular"]["verdict"],
            family_layout["REFINEMENT_H|jitter_0.05"]["verdict"],
            family_layout["SPECTRAL_KH|jitter_0.05"]["verdict"],
        )
        by_component[component] = {"formal_families": family_layout, **mapped}
        verdicts[component] = mapped["component_verdict"]
    return by_component, verdicts


def support_ratio_analysis(cases: list[dict[str, Any]], registry: dict[str, Any]) -> dict[str, Any]:
    relevant = {
        "interpolation_density": ["D010"],
        "density_rate": ["V100"],
        "pressure_gradient_acceleration": ["D010"],
        "viscosity_laplacian_acceleration": ["V100"],
        "total_acceleration": ["D010", "V100"],
    }
    output = {"label": "DESCRIPTIVE_SCOPE_DIAGNOSTIC", "components": {}}
    for component, tracks in relevant.items():
        groups = {}
        for track in tracks:
            for layout in ("regular", "jitter_0.05"):
                slopes = []
                for replicate in range(3):
                    selected = sorted([
                        case for case in cases
                        if "SUPPORT_RATIO_HDX" in case["family_labels"]
                        and case["track_template"] == track
                        and case["layout_class"] == layout
                        and case["replicate_id"] == replicate
                    ], key=lambda case: case["support_over_dx"])
                    for a, b in zip(selected[:-1], selected[1:]):
                        ca, cb = a["components"][component], b["components"][component]
                        try:
                            slope = local_log_slope(
                                {"x": a["support_over_dx"], "replicate_id": replicate, "T": ca["target_rms"], "U": ca["U_num"], "S": ca["component_scale"], "audit_valid": a["mandatory_audit"]["mandatory_case_pass"]},
                                {"x": b["support_over_dx"], "replicate_id": replicate, "T": cb["target_rms"], "U": cb["U_num"], "S": cb["component_scale"], "audit_valid": b["mandatory_audit"]["mandatory_case_pass"]},
                            )
                            slope["interpretation"] = "DESCRIPTIVE_SCOPE_DIAGNOSTIC_NO_EXPECTED_SIGN"
                        except ValueError as exc:
                            slope = {"status": "UNRESOLVED", "reason": str(exc)}
                        slopes.append(slope)
                groups[f"{track}|{layout}"] = {"local_descriptive_slopes": slopes}
        output["components"][component] = groups
    return output


def disorder_analysis(cases: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        grouped[case["regular_disorder_pair_id"]].append(case)
    result = {"pair_count": len(grouped), "components": {}}
    for component in COMPONENT_MAP:
        ratios = []
        records = []
        for pair_id, pair in grouped.items():
            if len(pair) != 2:
                records.append({"pair_id": pair_id, "status": "PAIRING_UNRESOLVED"})
                continue
            regular = next(case for case in pair if case["layout_class"] == "regular")
            jitter = next(case for case in pair if case["layout_class"] == "jitter_0.05")
            yr = regular["components"][component]["normalized_target_Y"]
            yj = jitter["components"][component]["normalized_target_Y"]
            ratio = yj / yr if yr > 0.0 else None
            if ratio is not None and math.isfinite(ratio):
                ratios.append(ratio)
            records.append({
                "pair_id": pair_id,
                "regular_case_id": regular["canonical_case_id"],
                "jitter_case_id": jitter["canonical_case_id"],
                "regular_Y": yr,
                "jitter_Y": yj,
                "jitter_to_regular_ratio": ratio,
            })
        result["components"][component] = {
            "pair_records": records,
            "median_jitter_to_regular_ratio": float(median(ratios)) if ratios else None,
            "minimum_jitter_to_regular_ratio": min(ratios) if ratios else None,
            "maximum_jitter_to_regular_ratio": max(ratios) if ratios else None,
        }
    return result


def write_case_component_csv(cases: list[dict[str, Any]]) -> None:
    columns = [
        "case_id", "component", "track", "layout", "replicate", "resolution", "dx", "h",
        "h_over_dx", "mode_nx", "mode_ny", "kh", "neighbor_count_mean",
        "anisotropy_median", "distance_cv_median", "target_rms", "component_scale",
        "normalized_Y", "U_num", "normalized_u", "Y_minus", "Y_plus",
        "continuum_operator_rms", "relative_effect_E_rel", "mandatory_audit_pass",
        "log_response_admissible", "families",
    ]
    with EVIDENCE_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for case in cases:
            g = case["geometry_descriptors"]
            for component, value in case["components"].items():
                writer.writerow({
                    "case_id": case["canonical_case_id"], "component": component,
                    "track": case["track_template"], "layout": case["layout_class"],
                    "replicate": case["replicate_id"], "resolution": case["resolution_per_axis"],
                    "dx": case["dx"], "h": case["support_h"], "h_over_dx": case["support_over_dx"],
                    "mode_nx": case["mode_index"][0], "mode_ny": case["mode_index"][1], "kh": case["kh"],
                    "neighbor_count_mean": g["neighbor_count_mean"],
                    "anisotropy_median": g["covariance_anisotropy_median"],
                    "distance_cv_median": g["neighbor_distance_cv_median"],
                    "target_rms": value["target_rms"], "component_scale": value["component_scale"],
                    "normalized_Y": value["normalized_target_Y"], "U_num": value["U_num"],
                    "normalized_u": value["normalized_uncertainty_u"], "Y_minus": value["Y_minus"],
                    "Y_plus": value["Y_plus"], "continuum_operator_rms": value["continuum_operator_rms"],
                    "relative_effect_E_rel": value["relative_effect_E_rel"],
                    "mandatory_audit_pass": case["mandatory_audit"]["mandatory_case_pass"],
                    "log_response_admissible": value["log_response_admissible"],
                    "families": ";".join(case["family_labels"]),
                })


def main() -> None:
    if EVIDENCE_JSON.exists() or EVIDENCE_CSV.exists():
        raise RuntimeError("final DDO-01C-R evidence already exists; refusing replacement")
    if sha256(REGISTRY_PATH) != REGISTRY_SHA256 or sha256(CA03_PATH) != CA03_SHA256:
        raise RuntimeError("frozen CA-03 or DDO-01C-R registry hash mismatch")
    registry = json.loads(REGISTRY_PATH.read_text())
    ca03 = json.loads(CA03_PATH.read_text())
    if registry["case_count"] != 204 or ca03["terminal_status"] != "DDO_CA03_H2_SCALING_SEMANTICS_AND_DESIGN_FROZEN":
        raise RuntimeError("frozen design prerequisite failed")
    determinism = configure_determinism()
    source_audit = []
    for relative, expected in SOURCE_EXPECTED.items():
        observed = sha256(ROOT / relative)
        source_audit.append({"path": relative, "expected_sha256": expected, "observed_sha256": observed, "match": observed == expected})
    if not all(item["match"] for item in source_audit):
        raise RuntimeError("imported source hash audit failed")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_checkpoint(registry)
    cache = GeometryCache()
    mode = "a" if cases else "w"
    with CHECKPOINT_PATH.open(mode) as handle:
        for entry in registry["cases"][len(cases):]:
            geometry = cache.get(entry)
            result = run_case(entry, geometry)
            handle.write(json.dumps(result, sort_keys=True) + "\n")
            handle.flush()
            cases.append(result)
            print(f"case_complete {len(cases)}/204 {entry['canonical_case_id']}", flush=True)
    formal, component_verdicts = formal_analysis(cases, registry)
    support = support_ratio_analysis(cases, registry)
    disorder = disorder_analysis(cases)
    terminal = project_summary(list(component_verdicts.values()))
    evidence = {
        "schema_version": "1.0",
        "project": "SPH-DDO-PoC",
        "stage": "DDO-01C-R",
        "generated_date": "2026-08-10",
        "terminal_status": terminal,
        "permanent_original_ddo01c_status": "DDO01C_H2_UNRESOLVED_CONTRACT_GAP",
        "permanent_original_ddo01c_status_changed": False,
        "frozen_input_bindings": {"ca03_manifest": CA03_SHA256, "ddo01cr_registry": REGISTRY_SHA256},
        "environment": {
            "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
            "torch": torch.__version__, "platform": platform.platform(), "device": "cpu",
            "dtype": "torch.float64", "C_fp": C_FP, "eps64": EPS64, "determinism": determinism,
        },
        "source_hash_audit": source_audit,
        "case_count": len(cases),
        "cases": cases,
        "formal_h2": formal,
        "component_verdicts": component_verdicts,
        "support_ratio_diagnostic": support,
        "regular_vs_disorder": disorder,
        "aggregate_numerical": {
            "mandatory_cases_passed": sum(case["mandatory_audit"]["mandatory_case_pass"] for case in cases),
            "mandatory_cases_failed": sum(not case["mandatory_audit"]["mandatory_case_pass"] for case in cases),
            "derivative_discrepancy_max": max(item["absolute_discrepancy"] for case in cases for item in case["derivative_gates"].values()),
            "derivative_gate_fraction_max": max(item["gate_fraction"] for case in cases for item in case["derivative_gates"].values()),
            "U_num_min": min(item["U_num"] for case in cases for item in case["uncertainty"].values()),
            "U_num_max": max(item["U_num"] for case in cases for item in case["uncertainty"].values()),
            "precision_degradation_diagnostic_max": max(item["precision_degradation_diagnostic"] for case in cases for item in case["uncertainty"].values()),
            "precision_degradation_in_primary_uncertainty": False,
            "component_closure_residual_max": max(case["component_closure"]["residual"] for case in cases),
            "all_formal_log_responses_admissible": all(
                case["components"][component]["log_response_admissible"]
                for component, tracks in registry["mandatory_component_tracks"].items()
                for case in cases
                if case["track_template"] in tracks and ("REFINEMENT_H" in case["family_labels"] or "SPECTRAL_KH" in case["family_labels"])
            ),
        },
        "controls": {
            "h3_h6_evaluated": False, "f2_f3_f4_balanced_atlas_created": False,
            "pca_svd_performed": False, "nearest_neighbor_prediction_performed": False,
            "regression_performed": False, "neural_training_performed": False,
            "optimizer_created": False, "time_integration_performed": False,
            "rollout_performed": False, "solver_in_the_loop_performed": False,
            "high_resolution_sph_used_as_truth": False, "lcdf_03_accessed": False,
            "lcdf_10_accessed": False,
        },
    }
    EVIDENCE_JSON.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    write_case_component_csv(cases)
    print(json.dumps({
        "terminal_status": terminal,
        "component_verdicts": component_verdicts,
        "mandatory_cases_passed": evidence["aggregate_numerical"]["mandatory_cases_passed"],
        "evidence_json_sha256": sha256(EVIDENCE_JSON),
        "evidence_csv_sha256": sha256(EVIDENCE_CSV),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
