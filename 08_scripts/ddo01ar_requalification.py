#!/usr/bin/env python3
"""Execute prospectively registered DDO-01A-R under frozen CA-01."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from dataclasses import replace
from pathlib import Path
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
    sha256,
)
from structure_preserving.conservative_pressure import (  # noqa: E402
    conservative_pressure_pair_forces,
)
from structure_preserving.conservative_viscosity import (  # noqa: E402
    conservative_viscosity_pair_forces,
)
from structure_preserving.kernels import (  # noqa: E402
    edge_kernel_gradients,
    edge_kernel_values,
    raw_gradient,
)
from structure_preserving.neighborhood import (  # noqa: E402
    PeriodicNeighborhood,
    audit_periodic_neighborhood,
    build_periodic_neighborhood,
    periodic_cartesian_layout,
    tensor_sha256,
)


REGISTRY_PATH = ROOT / "06_manifests/ddo01ar_case_registry.json"
FROZEN_REGISTRY_SHA256 = "403aedcc4cb9c4ac194d044850e7a698d11ff8331cffa5a9041907e9a60d83e7"
C_FP = 128.0
EPS64 = float(np.finfo(np.float64).eps)

SOURCE_EXPECTED = {
    "01_imported_baseline/structure_preserving/__init__.py": "18afa8e375e06bd03ce68f17528c7a27722e1dbdab17536d1b060994446ad93a",
    "01_imported_baseline/structure_preserving/neighborhood.py": "44d61e0abbc9901472dae90f83127f5231fc3f6e8ac92a971228dfdcb230aaa8",
    "01_imported_baseline/structure_preserving/kernels.py": "bad08e0f49b308c568cd438c9981abd2c906e16c6570ebc0ca7d19d9847b333b",
    "01_imported_baseline/structure_preserving/conservative_pressure.py": "b6366666ba89cc1f367a95390a411905eee8b7f55fba28a024f5732860004064",
    "01_imported_baseline/structure_preserving/conservative_viscosity.py": "bdfbcb457f6973130f0131ec3c0a3fecc7197dd117c8256163cf3a1445307852",
}

FROZEN_SCALES = {
    "rho": 1.0,
    "grad_rho": 1.0,
    "pressure": 100.0,
    "grad_pressure": 100.0,
    "velocity": 0.1,
    "grad_velocity": 0.1,
    "divergence": 0.1,
    "vorticity": 0.1,
    "strain": 0.1,
    "lap_velocity": 0.1,
    "continuum_density": 1.0,
    "continuum_density_rate": 0.1,
    "continuum_pressure_acceleration": 0.01,
    "continuum_viscosity_acceleration": 0.01,
    "continuum_acceleration": 0.01,
    "interpolation_density": 1.0,
    "density_sum": 1.0,
    "density_rate": 0.1,
    "target_pressure": 0.01,
    "target_viscosity": 0.01,
    "target_acceleration": 0.01,
}

TARGET_NAMES = (
    "interpolation_density",
    "density_sum",
    "density_rate",
    "pressure",
    "viscosity",
    "acceleration",
)


def max_abs(value: torch.Tensor) -> float:
    return float(value.detach().abs().max()) if value.numel() else 0.0


def fsum_scatter(
    row: torch.Tensor,
    values: torch.Tensor,
    particle_count: int,
) -> torch.Tensor:
    """Independent deterministic scatter using Python math.fsum."""

    row_np = row.detach().cpu().numpy().astype(np.int64, copy=False)
    values_np = values.detach().cpu().numpy()
    order = np.argsort(row_np, kind="stable")
    sorted_row = row_np[order]
    sorted_values = values_np[order]
    flat = sorted_values.reshape(sorted_values.shape[0], -1)
    result = np.zeros((particle_count, flat.shape[1]), dtype=np.float64)
    start = 0
    while start < len(sorted_row):
        particle = int(sorted_row[start])
        stop = start + 1
        while stop < len(sorted_row) and int(sorted_row[stop]) == particle:
            stop += 1
        for component in range(flat.shape[1]):
            result[particle, component] = math.fsum(
                float(item) for item in flat[start:stop, component]
            )
        start = stop
    shaped = result.reshape((particle_count, *values.shape[1:]))
    return torch.from_numpy(shaped).to(dtype=values.dtype)


def compensated_discrete_components(
    neighborhood: PeriodicNeighborhood,
    rho: torch.Tensor,
    velocity: torch.Tensor,
    *,
    mass: float,
    c0: float,
    rho0: float,
    nu: float,
) -> dict[str, torch.Tensor]:
    row = neighborhood.row
    col = neighborhood.col
    count = neighborhood.particle_count
    masses = torch.full((count,), mass, dtype=rho.dtype)
    volumes = masses / rho
    kernel = edge_kernel_values(neighborhood)
    gradient = edge_kernel_gradients(neighborhood)
    density_sum = fsum_scatter(row, masses[col] * kernel, count)
    interpolation_density = fsum_scatter(
        row, volumes[col] * rho[col] * kernel, count
    )
    divergence_terms = volumes[col] * torch.sum(
        (velocity[col] - velocity[row]) * gradient, dim=1
    )
    divergence = fsum_scatter(row, divergence_terms, count)
    density_rate = -rho * divergence

    pressure = c0**2 * (rho - rho0)
    i_p, j_p, pressure_pair = conservative_pressure_pair_forces(
        neighborhood,
        mass=masses,
        density=rho,
        pressure=pressure,
    )
    pressure_rows = torch.cat((i_p, j_p))
    pressure_terms = torch.cat((pressure_pair, -pressure_pair), dim=0)
    pressure_acceleration = fsum_scatter(
        pressure_rows, pressure_terms, count
    ) / masses[:, None]

    i_v, j_v, viscosity_pair, _ = conservative_viscosity_pair_forces(
        neighborhood,
        mass=masses,
        density=rho,
        velocity=velocity,
        physical_viscosity=nu,
    )
    viscosity_rows = torch.cat((i_v, j_v))
    viscosity_terms = torch.cat((viscosity_pair, -viscosity_pair), dim=0)
    viscosity_acceleration = fsum_scatter(
        viscosity_rows, viscosity_terms, count
    ) / masses[:, None]
    return {
        "density_sum": density_sum,
        "interpolation_density": interpolation_density,
        "divergence": divergence,
        "density_rate": density_rate,
        "pressure_acceleration": pressure_acceleration,
        "viscosity_acceleration": viscosity_acceleration,
        "acceleration": pressure_acceleration + viscosity_acceleration,
    }


def independent_geometry_neighborhood(
    positions: torch.Tensor,
    support: float,
    *,
    chunk_size: int = 128,
) -> PeriodicNeighborhood:
    """Brute-force periodic graph without the imported minimum-image path."""

    count = int(positions.shape[0])
    domain_min = torch.tensor((0.0, 0.0), dtype=positions.dtype)
    domain_max = torch.tensor((1.0, 1.0), dtype=positions.dtype)
    extent = domain_max - domain_min
    particle_support = torch.full((count,), support, dtype=positions.dtype)
    eps = torch.finfo(positions.dtype).eps
    rows: list[torch.Tensor] = []
    cols: list[torch.Tensor] = []
    displacements: list[torch.Tensor] = []
    for start in range(0, count, chunk_size):
        stop = min(start + chunk_size, count)
        raw = positions[start:stop, None, :] - positions[None, :, :]
        displacement = raw - extent * torch.floor(raw / extent + 0.5)
        distance = torch.linalg.vector_norm(displacement, dim=-1)
        retained = distance <= support * (1.0 + 16.0 * eps)
        local = torch.nonzero(retained, as_tuple=False)
        rows.append(local[:, 0] + start)
        cols.append(local[:, 1])
        displacements.append(displacement[local[:, 0], local[:, 1]])
    row = torch.cat(rows).to(torch.int64)
    col = torch.cat(cols).to(torch.int64)
    displacement = torch.cat(displacements)
    distance = torch.linalg.vector_norm(displacement, dim=1)
    edge_support = torch.full_like(distance, support)
    return PeriodicNeighborhood(
        row=row,
        col=col,
        displacement=displacement,
        distance=distance,
        edge_support=edge_support,
        particle_support=particle_support,
        domain_min=domain_min,
        domain_max=domain_max,
        particle_count=count,
    )


def derivative_sph_channels(
    derivative: dict[str, torch.Tensor],
    discrete: dict[str, torch.Tensor],
    neighborhood: PeriodicNeighborhood,
    *,
    mass: float,
    nu: float,
) -> dict[str, torch.Tensor]:
    rho = derivative["rho"]
    velocity = derivative["velocity"]
    volumes = torch.full_like(rho, mass) / rho
    gradient_velocity = raw_gradient(neighborhood, velocity, volumes)
    gradient_rho = raw_gradient(neighborhood, rho, volumes)
    divergence = gradient_velocity[:, 0, 0] + gradient_velocity[:, 1, 1]
    vorticity = gradient_velocity[:, 1, 0] - gradient_velocity[:, 0, 1]
    strain = 0.5 * (gradient_velocity + gradient_velocity.transpose(1, 2))
    pressure = 100.0 * (rho - 1.0)
    pressure_gradient_equivalent = -rho[:, None] * discrete["pressure_acceleration"]
    lap_velocity = discrete["viscosity_acceleration"] / nu
    return {
        "rho": discrete["density_sum"],
        "grad_rho": gradient_rho,
        "pressure": pressure,
        "grad_pressure": pressure_gradient_equivalent,
        "velocity": velocity,
        "grad_velocity": gradient_velocity,
        "divergence": divergence,
        "vorticity": vorticity,
        "strain": strain,
        "lap_velocity": lap_velocity,
    }


def continuum_sph_channels(
    discrete: dict[str, torch.Tensor],
) -> dict[str, torch.Tensor]:
    return {
        "density": discrete["density_sum"],
        "density_rate": discrete["density_rate"],
        "pressure_acceleration": discrete["pressure_acceleration"],
        "viscosity_acceleration": discrete["viscosity_acceleration"],
        "acceleration": discrete["acceleration"],
    }


def characteristic_scale(
    frozen: float,
    analytic: torch.Tensor,
    sph: torch.Tensor,
) -> float:
    return max(float(frozen), max_abs(analytic), max_abs(sph))


def topology_keys(neighborhood: PeriodicNeighborhood) -> torch.Tensor:
    return torch.sort(
        neighborhood.row * neighborhood.particle_count + neighborhood.col
    ).values


def target_analytic_and_sph(
    name: str,
    continuum: dict[str, torch.Tensor],
    discrete: dict[str, torch.Tensor],
) -> tuple[torch.Tensor, torch.Tensor]:
    if name in ("interpolation_density", "density_sum"):
        return continuum["density"], discrete[name]
    if name == "density_rate":
        return continuum["density_rate"], discrete["density_rate"]
    if name == "pressure":
        return continuum["pressure_acceleration"], discrete["pressure_acceleration"]
    if name == "viscosity":
        return continuum["viscosity_acceleration"], discrete["viscosity_acceleration"]
    if name == "acceleration":
        return continuum["acceleration"], discrete["acceleration"]
    raise KeyError(name)


def case_result(entry: dict[str, Any]) -> dict[str, Any]:
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
    primary_neighborhood = build_periodic_neighborhood(
        positions,
        support,
        domain_minimum=(0.0, 0.0),
        domain_maximum=(1.0, 1.0),
    )
    primary_topology = audit_periodic_neighborhood(positions, primary_neighborhood)
    independent_neighborhood = independent_geometry_neighborhood(positions, support)
    primary_keys = topology_keys(primary_neighborhood)
    independent_keys = topology_keys(independent_neighborhood)
    independent_key_unique = int(torch.unique(independent_keys).numel()) == int(independent_keys.numel())
    independent_reciprocal = bool(
        torch.equal(
            independent_keys,
            torch.sort(
                independent_neighborhood.col * independent_neighborhood.particle_count
                + independent_neighborhood.row
            ).values,
        )
    )
    topology_key_equal = bool(torch.equal(primary_keys, independent_keys))

    derivative_a = evaluator_a(positions, probe, mode, phase=phase)
    derivative_b = evaluator_b(positions, probe, mode, phase=phase)
    nu = 0.01
    mass = dx**2
    continuum_a = continuum_components(derivative_a, nu=nu)
    continuum_b = continuum_components(derivative_b, nu=nu)
    primary_discrete = discrete_components(
        primary_neighborhood,
        derivative_a["rho"],
        derivative_a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    primary_target = defects(continuum_a, primary_discrete)
    reference_target = defects(continuum_b, primary_discrete)

    repeat_discrete = discrete_components(
        primary_neighborhood,
        derivative_a["rho"],
        derivative_a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    repeat_target = defects(continuum_a, repeat_discrete)

    permutation_digest = hashlib.sha256(
        f"DDO01A-R|{entry['canonical_case_id']}|neighbor_permutation".encode()
    ).digest()
    permutation_seed = int.from_bytes(permutation_digest[:8], "big") & ((1 << 63) - 1)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(permutation_seed)
    permutation = torch.randperm(primary_neighborhood.row.numel(), generator=generator)
    permuted_neighborhood = permute_neighborhood(primary_neighborhood, permutation)
    permuted_discrete = discrete_components(
        permuted_neighborhood,
        derivative_a["rho"],
        derivative_a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    permuted_target = defects(continuum_a, permuted_discrete)

    compensated_discrete = compensated_discrete_components(
        primary_neighborhood,
        derivative_a["rho"],
        derivative_a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    compensated_target = defects(continuum_a, compensated_discrete)

    geometry_discrete = discrete_components(
        independent_neighborhood,
        derivative_a["rho"],
        derivative_a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    geometry_target = defects(continuum_a, geometry_discrete)

    positions32 = positions.to(torch.float32)
    neighborhood32 = build_periodic_neighborhood(
        positions32,
        support,
        domain_minimum=(0.0, 0.0),
        domain_maximum=(1.0, 1.0),
    )
    derivative32 = evaluator_a(positions32, probe, mode, phase=phase)
    continuum32 = continuum_components(derivative32, nu=nu)
    discrete32 = discrete_components(
        neighborhood32,
        derivative32["rho"],
        derivative32["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    target32 = defects(continuum32, discrete32)

    sph_derivative = derivative_sph_channels(
        derivative_a, primary_discrete, primary_neighborhood, mass=mass, nu=nu
    )
    derivative_gates: dict[str, Any] = {}
    for name in derivative_a:
        scale = characteristic_scale(
            FROZEN_SCALES[name], derivative_a[name], sph_derivative[name]
        )
        discrepancy = linf_difference(derivative_a[name], derivative_b[name])
        gate = C_FP * EPS64 * scale
        derivative_gates[name] = {
            "physical_scale": scale,
            "absolute_discrepancy": discrepancy,
            "scale_normalized_discrepancy": discrepancy / scale,
            "gate": gate,
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
    continuum_gates: dict[str, Any] = {}
    for name in continuum_a:
        scale = characteristic_scale(
            FROZEN_SCALES[continuum_scale_keys[name]],
            continuum_a[name],
            continuum_sph[name],
        )
        discrepancy = linf_difference(continuum_a[name], continuum_b[name])
        gate = C_FP * EPS64 * scale
        continuum_gates[name] = {
            "physical_scale": scale,
            "absolute_discrepancy": discrepancy,
            "scale_normalized_discrepancy": discrepancy / scale,
            "gate": gate,
            "pass": discrepancy <= gate,
        }

    frozen_target_key = {
        "interpolation_density": "interpolation_density",
        "density_sum": "density_sum",
        "density_rate": "density_rate",
        "pressure": "target_pressure",
        "viscosity": "target_viscosity",
        "acceleration": "target_acceleration",
    }
    component_identity = linf_difference(
        primary_target["acceleration"],
        primary_target["pressure"] + primary_target["viscosity"],
    )
    target_uncertainty: dict[str, Any] = {}
    for name in TARGET_NAMES:
        analytic_value, sph_value = target_analytic_and_sph(
            name, continuum_a, primary_discrete
        )
        scale = characteristic_scale(
            FROZEN_SCALES[frozen_target_key[name]], analytic_value, sph_value
        )
        u_round = C_FP * EPS64 * scale
        delta_ref = linf_difference(primary_target[name], reference_target[name])
        delta_repeat = linf_difference(primary_target[name], repeat_target[name])
        delta_perm = linf_difference(primary_target[name], permuted_target[name])
        delta_comp = linf_difference(primary_target[name], compensated_target[name])
        delta_accum = max(delta_perm, delta_comp)
        delta_geometry = linf_difference(primary_target[name], geometry_target[name])
        delta_identity = component_identity if name == "acceleration" else 0.0
        u_num = (
            u_round
            + delta_ref
            + delta_repeat
            + delta_accum
            + delta_geometry
            + delta_identity
        )
        sign_residual = linf_difference(sph_value + primary_target[name], analytic_value)
        precision_degradation = linf_difference(primary_target[name], target32[name].double())
        target_uncertainty[name] = {
            "physical_scale": scale,
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
            "precision_degradation_diagnostic": precision_degradation,
            "precision_degradation_in_U_num": False,
            "all_terms_finite": bool(
                np.isfinite(
                    [
                        scale,
                        u_round,
                        delta_ref,
                        delta_repeat,
                        delta_perm,
                        delta_comp,
                        delta_geometry,
                        delta_identity,
                        u_num,
                    ]
                ).all()
            ),
        }

    closure_bound = (
        target_uncertainty["acceleration"]["U_num"]
        + target_uncertainty["pressure"]["U_num"]
        + target_uncertainty["viscosity"]["U_num"]
    )
    closure_pass = component_identity <= closure_bound
    topology_failure_fields = (
        "duplicate_edge_count",
        "missing_self_edge_count",
        "nonreciprocal_nonself_edge_count",
        "out_of_bounds_edge_count",
        "omitted_strict_support_edge_count",
        "unexpected_edge_count",
    )
    primary_topology_pass = all(
        int(primary_topology[field]) == 0 for field in topology_failure_fields
    )
    independent_topology_pass = (
        independent_key_unique
        and independent_reciprocal
        and topology_key_equal
        and bool((independent_neighborhood.row >= 0).all())
        and bool((independent_neighborhood.row < independent_neighborhood.particle_count).all())
        and bool((independent_neighborhood.col >= 0).all())
        and bool((independent_neighborhood.col < independent_neighborhood.particle_count).all())
    )
    derivative_pass = all(item["pass"] for item in derivative_gates.values())
    continuum_pass = all(item["pass"] for item in continuum_gates.values())
    uncertainty_pass = all(
        item["all_terms_finite"] and item["positive_additive_sign_pass"]
        for item in target_uncertainty.values()
    )
    mandatory_pass = (
        primary_topology_pass
        and independent_topology_pass
        and derivative_pass
        and continuum_pass
        and uncertainty_pass
        and closure_pass
    )
    return {
        "case_index": entry["case_index"],
        "canonical_case_id": entry["canonical_case_id"],
        "phase_radians": phase,
        "jitter_seed": entry["jitter_seed"],
        "layout_sha256": layout_hash,
        "primary_edge_key_sha256": tensor_sha256(primary_keys),
        "independent_edge_key_sha256": tensor_sha256(independent_keys),
        "particle_count": int(positions.shape[0]),
        "dx": dx,
        "support_h": support,
        "kh": 2.0 * math.pi * math.hypot(*mode) * support,
        "points_per_wavelength": resolution / math.hypot(*mode),
        "primary_topology": primary_topology,
        "independent_geometry": {
            "edge_count": int(independent_keys.numel()),
            "unique": independent_key_unique,
            "reciprocal": independent_reciprocal,
            "edge_keys_equal_primary": topology_key_equal,
            "target_output_path_executed": True,
        },
        "neighbor_permutation_seed": permutation_seed,
        "derivative_gates": derivative_gates,
        "continuum_gates": continuum_gates,
        "target_uncertainty": target_uncertainty,
        "component_closure": {
            "residual": component_identity,
            "bound_U_acc_plus_U_pressure_plus_U_viscosity": closure_bound,
            "pass": closure_pass,
        },
        "case_gate_summary": {
            "primary_topology_pass": primary_topology_pass,
            "independent_topology_pass": independent_topology_pass,
            "derivative_pass": derivative_pass,
            "continuum_pass": continuum_pass,
            "uncertainty_and_sign_pass": uncertainty_pass,
            "component_closure_pass": closure_pass,
            "mandatory_case_pass": mandatory_pass,
        },
    }


def nested_max(cases: list[dict[str, Any]], *keys: str) -> float:
    values: list[float] = []
    for case in cases:
        node: Any = case
        for key in keys:
            node = node[key]
        if isinstance(node, dict):
            values.extend(float(value) for value in node.values())
        else:
            values.append(float(node))
    return max(values, default=0.0)


def main() -> None:
    registry_hash = sha256(REGISTRY_PATH)
    if registry_hash != FROZEN_REGISTRY_SHA256:
        raise RuntimeError(
            f"registry hash mismatch: {registry_hash} != {FROZEN_REGISTRY_SHA256}"
        )
    registry = json.loads(REGISTRY_PATH.read_text())
    if registry.get("case_count") != 24 or len(registry.get("cases", [])) != 24:
        raise RuntimeError("frozen registry must contain exactly 24 cases")
    determinism = configure_determinism()
    source_audit = []
    for path, expected in SOURCE_EXPECTED.items():
        observed = sha256(ROOT / path)
        source_audit.append(
            {
                "path": path,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "match": observed == expected,
            }
        )
    if not all(item["match"] for item in source_audit):
        raise RuntimeError("imported source hash audit failed")
    cases = [case_result(entry) for entry in registry["cases"]]
    every_case_pass = all(
        case["case_gate_summary"]["mandatory_case_pass"] for case in cases
    )
    status = (
        "DDO01_ANALYTICAL_PREFLIGHT_REQUALIFIED"
        if every_case_pass
        else "DDO01_ANALYTICAL_PREFLIGHT_NUMERICAL_FAILURE"
    )
    derivative_absolute = [
        item["absolute_discrepancy"]
        for case in cases
        for item in case["derivative_gates"].values()
    ]
    derivative_ratios = [
        item["absolute_discrepancy"] / item["gate"]
        for case in cases
        for item in case["derivative_gates"].values()
    ]
    continuum_absolute = [
        item["absolute_discrepancy"]
        for case in cases
        for item in case["continuum_gates"].values()
    ]
    uncertainty_values = [
        item["U_num"]
        for case in cases
        for item in case["target_uncertainty"].values()
    ]
    precision_values = [
        item["precision_degradation_diagnostic"]
        for case in cases
        for item in case["target_uncertainty"].values()
    ]
    output = {
        "schema_version": "1.0",
        "project": "SPH-DDO-PoC",
        "stage": "DDO-01A-R",
        "generated_date": "2026-08-10",
        "terminal_status": status,
        "original_ddo01a_status": "DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP",
        "original_status_retroactively_changed": False,
        "ca01_status": "DDO_CA01_NUMERICAL_QUALIFICATION_CONTRACT_FROZEN",
        "registry_path": "06_manifests/ddo01ar_case_registry.json",
        "registry_sha256": registry_hash,
        "case_count": len(cases),
        "environment": {
            "python": sys.version,
            "python_executable": sys.executable,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "device": "cpu",
            "dtype": "torch.float64",
            "eps64": EPS64,
            "C_fp": C_FP,
            "determinism": determinism,
        },
        "source_hash_audit": source_audit,
        "ca01_bindings": {
            "ca01_contract_sha256": sha256(
                ROOT / "00_project_contract/amendments/ca01_numerical_qualification_contract.md"
            ),
            "ca01_change_record_sha256": sha256(
                ROOT / "00_project_contract/amendments/ca01_change_record.md"
            ),
            "ca01_manifest_sha256": sha256(ROOT / "06_manifests/ca01_manifest.json"),
            "ca01_final_report_sha256": sha256(ROOT / "07_reports/ca01_final_report.md"),
            "ddo01a_report_preserved_sha256": sha256(
                ROOT / "07_reports/ddo01a_preflight_report.md"
            ),
            "ddo01a_manifest_preserved_sha256": sha256(
                ROOT / "06_manifests/ddo01a_manifest.json"
            ),
        },
        "aggregate": {
            "mandatory_cases_passed": sum(
                case["case_gate_summary"]["mandatory_case_pass"] for case in cases
            ),
            "mandatory_cases_failed": sum(
                not case["case_gate_summary"]["mandatory_case_pass"] for case in cases
            ),
            "derivative_absolute_discrepancy_max": max(derivative_absolute),
            "derivative_gate_fraction_max": max(derivative_ratios),
            "continuum_absolute_discrepancy_max": max(continuum_absolute),
            "deterministic_repeat_target_discrepancy_max": max(
                item["Delta_repeat"]
                for case in cases
                for item in case["target_uncertainty"].values()
            ),
            "neighbor_permutation_target_discrepancy_max": max(
                item["Delta_perm"]
                for case in cases
                for item in case["target_uncertainty"].values()
            ),
            "compensated_accumulation_target_discrepancy_max": max(
                item["Delta_comp"]
                for case in cases
                for item in case["target_uncertainty"].values()
            ),
            "independent_geometry_target_discrepancy_max": max(
                item["Delta_geometry"]
                for case in cases
                for item in case["target_uncertainty"].values()
            ),
            "component_closure_residual_max": max(
                case["component_closure"]["residual"] for case in cases
            ),
            "component_closure_bound_min": min(
                case["component_closure"]["bound_U_acc_plus_U_pressure_plus_U_viscosity"]
                for case in cases
            ),
            "U_num_min": min(uncertainty_values),
            "U_num_max": max(uncertainty_values),
            "precision_degradation_diagnostic_max": max(precision_values),
            "precision_degradation_in_primary_uncertainty": False,
            "all_primary_topology_pass": all(
                case["case_gate_summary"]["primary_topology_pass"] for case in cases
            ),
            "all_independent_topology_pass": all(
                case["case_gate_summary"]["independent_topology_pass"] for case in cases
            ),
            "all_derivative_gates_pass": all(
                case["case_gate_summary"]["derivative_pass"] for case in cases
            ),
            "all_continuum_gates_pass": all(
                case["case_gate_summary"]["continuum_pass"] for case in cases
            ),
            "all_uncertainty_and_sign_gates_pass": all(
                case["case_gate_summary"]["uncertainty_and_sign_pass"] for case in cases
            ),
            "all_component_closure_gates_pass": all(
                case["case_gate_summary"]["component_closure_pass"] for case in cases
            ),
        },
        "cases": cases,
        "controls": {
            "ddo01b_executed": False,
            "h1_evaluated": False,
            "pilot_dataset_created": False,
            "atlas_created": False,
            "reference_in_model_input": False,
            "float32_in_primary_uncertainty": False,
            "neural_training_performed": False,
            "optimizer_created": False,
            "time_integration_performed": False,
            "rollout_performed": False,
            "high_resolution_sph_used_as_truth": False,
            "lcdf_03_accessed": False,
            "lcdf_10_accessed": False,
        },
        "authorization": {
            "ddo01b_authorized": status == "DDO01_ANALYTICAL_PREFLIGHT_REQUALIFIED",
            "h1_status": "NOT_EVALUATED",
            "atlas_authorized": False,
            "architecture_selection_authorized": False,
            "neural_training_authorized": False,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
