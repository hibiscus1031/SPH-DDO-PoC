#!/usr/bin/env python3
"""Execute the fresh DDO-01B-R F1 signal pilot under CA-01 and CA-02."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any, TextIO

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
from h1_signal_semantics import (  # noqa: E402
    case_label,
    case_ratios,
    deterministic_seed,
    evaluate_component,
    scalar_case_rms,
    vector_case_rms,
)
from structure_preserving.neighborhood import (  # noqa: E402
    audit_periodic_neighborhood,
    build_periodic_neighborhood,
    periodic_cartesian_layout,
    tensor_sha256,
)


REGISTRY_PATH = ROOT / "06_manifests/ddo01br_case_registry.json"
MASK_PATH = ROOT / "06_manifests/ddo01br_excitation_mask.json"
CA02_MANIFEST_PATH = ROOT / "06_manifests/ca02_manifest.json"
REGISTRY_SHA256 = "ee654fffdaf966bbaa01974fd09755c5c6c65af62bc77e8240d40ede4547dd8f"
MASK_SHA256 = "d7a71824ac55525d90e8c469fd0236424fdaae5f074310f606a3113e497d3d8b"
CA02_MANIFEST_SHA256 = "2cab9c8b435d138eee2d964b81914596effb87044c8cc272c07983d0e8626a8a"

DATA_DIR = ROOT / "data/pilot_f1"
META_PATH = DATA_DIR / "ddo01br_f1_pilot_metadata.csv"
OBS_PATH = DATA_DIR / "ddo01br_f1_pilot_observables.csv"
REF_PATH = DATA_DIR / "ddo01br_f1_pilot_reference_targets.csv"
EVIDENCE_PATH = DATA_DIR / "ddo01br_f1_pilot_evidence.json"

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
UNITS = {
    "interpolation_density": "M L^-2",
    "density_rate": "M L^-2 T^-1",
    "pressure_gradient_acceleration": "L T^-2",
    "viscosity_laplacian_acceleration": "L T^-2",
    "total_acceleration": "L T^-2",
}

META_COLUMNS = [
    "case_id", "particle_id", "meta__position_x", "meta__position_y",
    "meta__resolution_per_axis", "meta__layout_class", "meta__probe",
    "meta__mode_nx", "meta__mode_ny", "meta__phase_radians",
    "meta__jitter_seed", "meta__dx", "meta__support_h", "meta__kh",
    "meta__dtype", "meta__reference_method",
]
OBS_COLUMNS = [
    "case_id", "particle_id", "obs__rho", "obs__velocity_x", "obs__velocity_y",
    "obs__density_summation", "obs__density_rate",
    "obs__pressure_acceleration_x", "obs__pressure_acceleration_y",
    "obs__viscosity_acceleration_x", "obs__viscosity_acceleration_y",
    "obs__total_acceleration_x", "obs__total_acceleration_y",
    "obs__support_h", "obs__dx", "obs__support_over_dx",
]
REF_COLUMNS = [
    "case_id", "particle_id", "target_ref__density",
    "target_ref__density_rate", "target_ref__pressure_acceleration_x",
    "target_ref__pressure_acceleration_y", "target_ref__viscosity_acceleration_x",
    "target_ref__viscosity_acceleration_y", "target_ref__total_acceleration_x",
    "target_ref__total_acceleration_y", "target_ref__defect_interpolation_density",
    "target_ref__defect_density_rate", "target_ref__defect_pressure_x",
    "target_ref__defect_pressure_y", "target_ref__defect_viscosity_x",
    "target_ref__defect_viscosity_y", "target_ref__defect_total_acceleration_x",
    "target_ref__defect_total_acceleration_y",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rms_target(value: torch.Tensor, vector: bool) -> float:
    array = value.detach().cpu().numpy()
    return vector_case_rms(array) if vector else scalar_case_rms(array)


def write_particle_rows(
    entry: dict[str, Any],
    positions: torch.Tensor,
    dx: float,
    support: float,
    kh: float,
    derivative: dict[str, torch.Tensor],
    continuum: dict[str, torch.Tensor],
    discrete: dict[str, torch.Tensor],
    target: dict[str, torch.Tensor],
    writers: tuple[csv.writer, csv.writer, csv.writer],
) -> None:
    meta_writer, obs_writer, ref_writer = writers
    arrays = {
        "positions": positions.detach().cpu().numpy(),
        "rho": derivative["rho"].detach().cpu().numpy(),
        "velocity": derivative["velocity"].detach().cpu().numpy(),
        "density_sum": discrete["density_sum"].detach().cpu().numpy(),
        "density_rate_sph": discrete["density_rate"].detach().cpu().numpy(),
        "pressure_sph": discrete["pressure_acceleration"].detach().cpu().numpy(),
        "viscosity_sph": discrete["viscosity_acceleration"].detach().cpu().numpy(),
        "acceleration_sph": discrete["acceleration"].detach().cpu().numpy(),
        "density_ref": continuum["density"].detach().cpu().numpy(),
        "density_rate_ref": continuum["density_rate"].detach().cpu().numpy(),
        "pressure_ref": continuum["pressure_acceleration"].detach().cpu().numpy(),
        "viscosity_ref": continuum["viscosity_acceleration"].detach().cpu().numpy(),
        "acceleration_ref": continuum["acceleration"].detach().cpu().numpy(),
        "interpolation_defect": target["interpolation_density"].detach().cpu().numpy(),
        "density_rate_defect": target["density_rate"].detach().cpu().numpy(),
        "pressure_defect": target["pressure"].detach().cpu().numpy(),
        "viscosity_defect": target["viscosity"].detach().cpu().numpy(),
        "acceleration_defect": target["acceleration"].detach().cpu().numpy(),
    }
    case_id = entry["canonical_case_id"]
    mode = entry["mode_index"]
    for particle in range(arrays["rho"].shape[0]):
        meta_writer.writerow([
            case_id, particle, *arrays["positions"][particle],
            entry["resolution_per_axis"], entry["layout_class"], entry["probe"],
            mode[0], mode[1], entry["phase_radians"], entry["jitter_seed"] or "",
            dx, support, kh, "float64", "closed_form_A_cross_checked_by_autodiff_B",
        ])
        obs_writer.writerow([
            case_id, particle, arrays["rho"][particle], *arrays["velocity"][particle],
            arrays["density_sum"][particle], arrays["density_rate_sph"][particle],
            *arrays["pressure_sph"][particle], *arrays["viscosity_sph"][particle],
            *arrays["acceleration_sph"][particle], support, dx, 4.0,
        ])
        ref_writer.writerow([
            case_id, particle, arrays["density_ref"][particle],
            arrays["density_rate_ref"][particle], *arrays["pressure_ref"][particle],
            *arrays["viscosity_ref"][particle], *arrays["acceleration_ref"][particle],
            arrays["interpolation_defect"][particle], arrays["density_rate_defect"][particle],
            *arrays["pressure_defect"][particle], *arrays["viscosity_defect"][particle],
            *arrays["acceleration_defect"][particle],
        ])


def run_case(
    entry: dict[str, Any],
    mask: dict[tuple[str, str], str],
    writers: tuple[csv.writer, csv.writer, csv.writer],
) -> dict[str, Any]:
    resolution = int(entry["resolution_per_axis"])
    jitter = float(entry["jitter_fraction"])
    seed = int(entry["jitter_seed"] or 0)
    mode = tuple(int(value) for value in entry["mode_index"])
    probe = str(entry["probe"])
    phase = float(entry["phase_radians"])
    positions, dx, layout_hash = periodic_cartesian_layout(
        resolution,
        jitter_fraction=jitter,
        seed=seed,
        dtype=torch.float64,
        domain_minimum=(0.0, 0.0),
        domain_maximum=(1.0, 1.0),
    )
    support = 4.0 * dx
    neighborhood = build_periodic_neighborhood(
        positions, support, domain_minimum=(0.0, 0.0), domain_maximum=(1.0, 1.0)
    )
    topology = audit_periodic_neighborhood(positions, neighborhood)
    independent_neighborhood = independent_geometry_neighborhood(positions, support)
    primary_keys = topology_keys(neighborhood)
    independent_keys = topology_keys(independent_neighborhood)
    independent_unique = int(torch.unique(independent_keys).numel()) == int(independent_keys.numel())
    independent_reciprocal = bool(torch.equal(
        independent_keys,
        torch.sort(independent_neighborhood.col * independent_neighborhood.particle_count + independent_neighborhood.row).values,
    ))
    topology_equal = bool(torch.equal(primary_keys, independent_keys))

    derivative_a = evaluator_a(positions, probe, mode, phase=phase)
    derivative_b = evaluator_b(positions, probe, mode, phase=phase)
    nu = 0.01
    mass = dx**2
    continuum_a = continuum_components(derivative_a, nu=nu)
    continuum_b = continuum_components(derivative_b, nu=nu)
    primary_discrete = discrete_components(
        neighborhood, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    primary_target = defects(continuum_a, primary_discrete)
    reference_target = defects(continuum_b, primary_discrete)

    repeat_discrete = discrete_components(
        neighborhood, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    repeat_target = defects(continuum_a, repeat_discrete)

    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(entry["neighbor_permutation_seed"]))
    permutation = torch.randperm(neighborhood.row.numel(), generator=generator)
    permuted = permute_neighborhood(neighborhood, permutation)
    permuted_discrete = discrete_components(
        permuted, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    permuted_target = defects(continuum_a, permuted_discrete)

    compensated_discrete = compensated_discrete_components(
        neighborhood, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    compensated_target = defects(continuum_a, compensated_discrete)
    geometry_discrete = discrete_components(
        independent_neighborhood, derivative_a["rho"], derivative_a["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    geometry_target = defects(continuum_a, geometry_discrete)

    positions32 = positions.to(torch.float32)
    neighborhood32 = build_periodic_neighborhood(
        positions32, support, domain_minimum=(0.0, 0.0), domain_maximum=(1.0, 1.0)
    )
    derivative32 = evaluator_a(positions32, probe, mode, phase=phase)
    continuum32 = continuum_components(derivative32, nu=nu)
    discrete32 = discrete_components(
        neighborhood32, derivative32["rho"], derivative32["velocity"],
        mass=mass, c0=10.0, rho0=1.0, nu=nu,
    )
    target32 = defects(continuum32, discrete32)

    sph_derivative = derivative_sph_channels(
        derivative_a, primary_discrete, neighborhood, mass=mass, nu=nu
    )
    derivative_gates: dict[str, Any] = {}
    for name in derivative_a:
        scale = characteristic_scale(FROZEN_SCALES[name], derivative_a[name], sph_derivative[name])
        discrepancy = linf_difference(derivative_a[name], derivative_b[name])
        gate = C_FP * EPS64 * scale
        derivative_gates[name] = {
            "absolute_discrepancy": discrepancy, "physical_scale": scale,
            "gate": gate, "gate_fraction": discrepancy / gate, "pass": discrepancy <= gate,
        }

    continuum_sph = continuum_sph_channels(primary_discrete)
    continuum_scale_keys = {
        "density": "continuum_density", "density_rate": "continuum_density_rate",
        "pressure_acceleration": "continuum_pressure_acceleration",
        "viscosity_acceleration": "continuum_viscosity_acceleration",
        "acceleration": "continuum_acceleration",
    }
    continuum_gates: dict[str, Any] = {}
    for name in continuum_a:
        scale = characteristic_scale(
            FROZEN_SCALES[continuum_scale_keys[name]], continuum_a[name], continuum_sph[name]
        )
        discrepancy = linf_difference(continuum_a[name], continuum_b[name])
        gate = C_FP * EPS64 * scale
        continuum_gates[name] = {
            "absolute_discrepancy": discrepancy, "physical_scale": scale,
            "gate": gate, "gate_fraction": discrepancy / gate, "pass": discrepancy <= gate,
        }

    frozen_target_key = {
        "interpolation_density": "interpolation_density", "density_rate": "density_rate",
        "pressure": "target_pressure", "viscosity": "target_viscosity",
        "acceleration": "target_acceleration",
    }
    identity = linf_difference(
        primary_target["acceleration"], primary_target["pressure"] + primary_target["viscosity"]
    )
    uncertainty: dict[str, Any] = {}
    for canonical, internal in COMPONENT_MAP.items():
        analytic_value, sph_value = target_analytic_and_sph(internal, continuum_a, primary_discrete)
        scale = characteristic_scale(FROZEN_SCALES[frozen_target_key[internal]], analytic_value, sph_value)
        u_round = C_FP * EPS64 * scale
        delta_ref = linf_difference(primary_target[internal], reference_target[internal])
        delta_repeat = linf_difference(primary_target[internal], repeat_target[internal])
        delta_perm = linf_difference(primary_target[internal], permuted_target[internal])
        delta_comp = linf_difference(primary_target[internal], compensated_target[internal])
        delta_accum = max(delta_perm, delta_comp)
        delta_geometry = linf_difference(primary_target[internal], geometry_target[internal])
        delta_identity = identity if internal == "acceleration" else 0.0
        u_num = u_round + delta_ref + delta_repeat + delta_accum + delta_geometry + delta_identity
        sign_residual = linf_difference(sph_value + primary_target[internal], analytic_value)
        values = [u_round, delta_ref, delta_repeat, delta_perm, delta_comp, delta_accum,
                  delta_geometry, delta_identity, u_num, sign_residual]
        uncertainty[canonical] = {
            "units": UNITS[canonical], "physical_scale": scale, "U_round": u_round,
            "Delta_ref": delta_ref, "Delta_repeat": delta_repeat,
            "Delta_perm": delta_perm, "Delta_comp": delta_comp,
            "Delta_accum": delta_accum, "Delta_geometry": delta_geometry,
            "Delta_identity": delta_identity, "U_num": u_num,
            "positive_additive_sign_residual": sign_residual,
            "positive_additive_sign_pass": sign_residual <= u_num,
            "precision_degradation_diagnostic": linf_difference(
                primary_target[internal], target32[internal].double()
            ),
            "precision_degradation_in_U_num": False,
            "all_terms_finite": bool(np.isfinite(values).all()),
        }

    closure_bound = (
        uncertainty["total_acceleration"]["U_num"]
        + uncertainty["pressure_gradient_acceleration"]["U_num"]
        + uncertainty["viscosity_laplacian_acceleration"]["U_num"]
    )
    topology_failure_fields = (
        "duplicate_edge_count", "missing_self_edge_count", "nonreciprocal_nonself_edge_count",
        "out_of_bounds_edge_count", "omitted_strict_support_edge_count", "unexpected_edge_count",
    )
    topology_pass = all(int(topology[field]) == 0 for field in topology_failure_fields)
    independent_pass = independent_unique and independent_reciprocal and topology_equal
    derivative_pass = all(item["pass"] for item in derivative_gates.values())
    continuum_pass = all(item["pass"] for item in continuum_gates.values())
    uncertainty_pass = all(
        item["all_terms_finite"] and item["positive_additive_sign_pass"]
        for item in uncertainty.values()
    )
    closure_pass = identity <= closure_bound
    mandatory_pass = (
        topology_pass and independent_pass and derivative_pass and continuum_pass
        and uncertainty_pass and closure_pass
    )
    kh = 2.0 * math.pi * math.hypot(*mode) * support
    write_particle_rows(
        entry, positions, dx, support, kh, derivative_a, continuum_a,
        primary_discrete, primary_target, writers,
    )

    components: dict[str, Any] = {}
    for canonical, internal in COMPONENT_MAP.items():
        excited = mask[(entry["canonical_case_id"], canonical)] == "ANALYTICALLY_EXCITED"
        target_rms = rms_target(primary_target[internal], canonical in VECTOR_COMPONENTS)
        u_num = uncertainty[canonical]["U_num"]
        ratio = float(case_ratios([target_rms], [u_num])[0]) if mandatory_pass else None
        components[canonical] = {
            "excitation": mask[(entry["canonical_case_id"], canonical)],
            "target_rms": target_rms,
            "U_num": u_num,
            "case_ratio": ratio if excited else None,
            "case_gate_margin": ratio / 10.0 if excited and ratio is not None else None,
            "case_label": case_label(
                analytically_excited=excited,
                mandatory_audit_valid=mandatory_pass,
                ratio=ratio,
            ),
        }

    pressure_rms = components["pressure_gradient_acceleration"]["target_rms"]
    viscosity_rms = components["viscosity_laplacian_acceleration"]["target_rms"]
    total_rms = components["total_acceleration"]["target_rms"]
    component_sum = pressure_rms + viscosity_rms
    cancellation_index = None if component_sum == 0.0 else 1.0 - total_rms / component_sum
    domination_share = None if component_sum == 0.0 else max(pressure_rms, viscosity_rms) / component_sum
    dominant = None
    if component_sum > 0.0:
        dominant = "pressure_gradient_acceleration" if pressure_rms >= viscosity_rms else "viscosity_laplacian_acceleration"

    return {
        "case_index": entry["case_index"], "canonical_case_id": entry["canonical_case_id"],
        "resolution_per_axis": resolution, "layout_class": entry["layout_class"],
        "probe": probe, "mode_index": list(mode), "particle_count": int(positions.shape[0]),
        "layout_sha256": layout_hash, "primary_edge_key_sha256": tensor_sha256(primary_keys),
        "independent_edge_key_sha256": tensor_sha256(independent_keys), "dx": dx,
        "support_h": support, "kh": kh, "points_per_wavelength": resolution / math.hypot(*mode),
        "topology": topology,
        "independent_geometry": {"unique": independent_unique, "reciprocal": independent_reciprocal,
                                 "edge_keys_equal_primary": topology_equal},
        "derivative_gates": derivative_gates, "continuum_gates": continuum_gates,
        "uncertainty": uncertainty,
        "component_closure": {"residual": identity, "bound": closure_bound, "pass": closure_pass},
        "mandatory_audit": {
            "primary_topology_pass": topology_pass, "independent_topology_pass": independent_pass,
            "derivative_pass": derivative_pass, "continuum_pass": continuum_pass,
            "uncertainty_and_sign_pass": uncertainty_pass, "component_closure_pass": closure_pass,
            "mandatory_case_pass": mandatory_pass,
        },
        "components": components,
        "total_vs_components": {
            "pressure_target_rms": pressure_rms, "viscosity_target_rms": viscosity_rms,
            "total_target_rms": total_rms, "cancellation_index_descriptive": cancellation_index,
            "domination_share_descriptive": domination_share, "dominant_component": dominant,
        },
    }


def aggregate_components(cases: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {}
    for component in COMPONENT_MAP:
        excited_cases = [case for case in cases if case["components"][component]["excitation"] == "ANALYTICALLY_EXCITED"]
        valid_cases = [case for case in excited_cases if case["mandatory_audit"]["mandatory_case_pass"]]
        targets = [case["components"][component]["target_rms"] for case in valid_cases]
        uncertainties = [case["components"][component]["U_num"] for case in valid_cases]
        strata = [(case["resolution_per_axis"], case["layout_class"]) for case in valid_cases]
        audits_valid = len(valid_cases) == len(excited_cases)
        result = evaluate_component(
            case_rms_values=targets,
            case_uncertainties=uncertainties,
            strata=strata,
            canonical_component_name=component,
            mandatory_audits_valid=audits_valid,
        )
        ratios = [case["components"][component]["case_ratio"] for case in valid_cases]
        margins = [ratio / 10.0 for ratio in ratios]
        labels = [case["components"][component]["case_label"] for case in cases]
        result.update({
            "canonical_component_name": component, "units": UNITS[component],
            "registered_case_count": len(cases), "analytically_excited_count": len(excited_cases),
            "analytically_unexcited_count": len(cases) - len(excited_cases),
            "invalid_excited_case_count": len(excited_cases) - len(valid_cases),
            "case_signal_pass_count": labels.count("CASE_SIGNAL_PASS"),
            "case_signal_low_count": labels.count("CASE_SIGNAL_LOW"),
            "case_unresolved_count": labels.count("CASE_UNRESOLVED"),
            "case_not_applicable_unexcited_count": labels.count("CASE_NOT_APPLICABLE_UNEXCITED"),
            "minimum_case_gate_margin": min(margins) if margins else None,
            "median_case_gate_margin": float(np.median(margins)) if margins else None,
            "lower_tail_case_gate_margin_p10": float(np.quantile(margins, 0.10, method="inverted_cdf")) if margins else None,
            "maximum_case_gate_margin": max(margins) if margins else None,
            "worst_eligible_case_id": valid_cases[int(np.argmin(margins))]["canonical_case_id"] if margins else None,
            "bootstrap_seed": deterministic_seed(component),
            "closed_for_learning_ddo01": result["verdict"] == "H1_SIGNAL_FAIL",
        })
        aggregate[component] = result
    return aggregate


def main() -> None:
    for path in (META_PATH, OBS_PATH, REF_PATH, EVIDENCE_PATH):
        if path.exists():
            raise RuntimeError(f"fresh output already exists; refusing replacement: {path}")
    bindings = {
        "registry": sha256(REGISTRY_PATH), "excitation_mask": sha256(MASK_PATH),
        "ca02_manifest": sha256(CA02_MANIFEST_PATH),
    }
    expected = {
        "registry": REGISTRY_SHA256, "excitation_mask": MASK_SHA256,
        "ca02_manifest": CA02_MANIFEST_SHA256,
    }
    if bindings != expected:
        raise RuntimeError(f"frozen input hash mismatch: {bindings} != {expected}")
    ca02 = json.loads(CA02_MANIFEST_PATH.read_text())
    if ca02["terminal_status"] != "DDO_CA02_H1_SIGNAL_SEMANTICS_FROZEN":
        raise RuntimeError("CA-02 is not frozen")
    registry = json.loads(REGISTRY_PATH.read_text())
    excitation_mask = json.loads(MASK_PATH.read_text())
    if registry["case_count"] != 24 or excitation_mask["pair_count"] != 120:
        raise RuntimeError("unexpected frozen registry or excitation-mask size")
    mask_lookup = {
        (item["canonical_case_id"], item["canonical_component_name"]): item["classification"]
        for item in excitation_mask["pairs"]
    }
    determinism = configure_determinism()
    source_audit = []
    for relative, expected_hash in SOURCE_EXPECTED.items():
        observed = sha256(ROOT / relative)
        source_audit.append({"path": relative, "expected_sha256": expected_hash,
                             "observed_sha256": observed, "match": observed == expected_hash})
    if not all(item["match"] for item in source_audit):
        raise RuntimeError("imported source hash audit failed")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with META_PATH.open("w", newline="") as meta_handle, OBS_PATH.open("w", newline="") as obs_handle, REF_PATH.open("w", newline="") as ref_handle:
        writers = (csv.writer(meta_handle), csv.writer(obs_handle), csv.writer(ref_handle))
        writers[0].writerow(META_COLUMNS)
        writers[1].writerow(OBS_COLUMNS)
        writers[2].writerow(REF_COLUMNS)
        cases = [run_case(entry, mask_lookup, writers) for entry in registry["cases"]]
    components = aggregate_components(cases)
    verdicts = [item["verdict"] for item in components.values()]
    any_numerical_failure = any(not case["mandatory_audit"]["mandatory_case_pass"] for case in cases)
    if any_numerical_failure:
        terminal = "DDO01BR_NUMERICAL_QUALIFICATION_FAILURE"
    elif all(verdict == "H1_SIGNAL_PASS" for verdict in verdicts):
        terminal = "DDO01BR_SPATIAL_DEFECT_SIGNAL_QUALIFIED"
    elif any(verdict == "H1_SIGNAL_PASS" for verdict in verdicts):
        terminal = "DDO01BR_COMPONENTWISE_SIGNAL_PARTIALLY_QUALIFIED"
    else:
        terminal = "DDO01BR_SPATIAL_DEFECT_SIGNAL_NOT_RESOLVED"
    observable_forbidden = [name for name in OBS_COLUMNS if "target" in name or "ref" in name or "analytic" in name]
    evidence = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01B-R",
        "generated_date": "2026-08-10", "terminal_status": terminal,
        "permanent_original_ddo01b_status": "DDO01B_H1_UNRESOLVED_CONTRACT_GAP",
        "permanent_original_ddo01b_status_changed": False,
        "frozen_input_bindings": bindings,
        "environment": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                        "torch": torch.__version__, "platform": platform.platform(), "device": "cpu",
                        "dtype": "torch.float64", "C_fp": C_FP, "eps64": EPS64,
                        "determinism": determinism},
        "source_hash_audit": source_audit, "case_count": len(cases), "cases": cases,
        "component_h1": components,
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
        },
        "dataset": {
            "metadata_path": "data/pilot_f1/ddo01br_f1_pilot_metadata.csv",
            "observables_path": "data/pilot_f1/ddo01br_f1_pilot_observables.csv",
            "reference_targets_path": "data/pilot_f1/ddo01br_f1_pilot_reference_targets.csv",
            "row_count": sum(case["particle_count"] for case in cases),
            "metadata_columns": META_COLUMNS, "observable_columns": OBS_COLUMNS,
            "reference_target_columns": REF_COLUMNS,
        },
        "firewall": {
            "reference_in_model_input": False, "observable_forbidden_columns": observable_forbidden,
            "observable_and_reference_physically_separate_files": True,
            "target_derived_features": False, "target_derived_normalization": False,
            "model_trained": False,
        },
        "controls": {
            "h2_h6_evaluated": False, "f2_f3_f4_executed": False,
            "balanced_atlas_created": False, "pca_svd_performed": False,
            "regression_performed": False, "neural_training_performed": False,
            "optimizer_created": False, "time_integration_performed": False,
            "rollout_performed": False, "solver_in_the_loop_performed": False,
            "high_resolution_sph_used_as_truth": False,
        },
    }
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal_status": terminal,
        "component_verdicts": {name: item["verdict"] for name, item in components.items()},
        "mandatory_cases_passed": evidence["aggregate_numerical"]["mandatory_cases_passed"],
        "dataset_rows": evidence["dataset"]["row_count"],
        "evidence_sha256": sha256(EVIDENCE_PATH),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
