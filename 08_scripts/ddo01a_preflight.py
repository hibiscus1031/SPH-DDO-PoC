#!/usr/bin/env python3
"""DDO-01A analytical, topology, and numerical preflight.

This script performs only the frozen F1 static preflight. It writes no data and
does not assign a gate status; machine-readable diagnostics are printed as JSON
so that the frozen contracts, rather than this implementation, determine status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_imported_baseline"))

from structure_preserving.conservative_pressure import (  # noqa: E402
    conservative_pressure_forces,
)
from structure_preserving.conservative_viscosity import (  # noqa: E402
    conservative_viscosity_acceleration,
)
from structure_preserving.kernels import (  # noqa: E402
    edge_kernel_gradients,
    edge_kernel_values,
    scatter_sum,
)
from structure_preserving.neighborhood import (  # noqa: E402
    PeriodicNeighborhood,
    audit_periodic_neighborhood,
    build_periodic_neighborhood,
    periodic_cartesian_layout,
    tensor_sha256,
)


CONTRACT_PATHS = [
    "00_project_contract/ddo_project_charter.md",
    "02_defect_definitions/spatial_defect_definition.md",
    "02_defect_definitions/operator_decomposition.md",
    "02_defect_definitions/dimensional_analysis.md",
    "03_field_design/analytical_field_family_spec.md",
    "03_field_design/prospective_parameter_axes.json",
    "04_identifiability_contract/identifiability_metrics.md",
    "04_identifiability_contract/locality_ladder.md",
    "04_identifiability_contract/prospective_gates.md",
    "05_representation_contract/representation_hypotheses.md",
    "05_representation_contract/conservation_claim_boundary.md",
    "06_manifests/inherited_artifact_manifest.csv",
    "06_manifests/ddo00_manifest.json",
    "06_manifests/project_status_ledger.json",
]

SOURCE_PATHS = [
    "01_imported_baseline/structure_preserving/__init__.py",
    "01_imported_baseline/structure_preserving/neighborhood.py",
    "01_imported_baseline/structure_preserving/kernels.py",
    "01_imported_baseline/structure_preserving/conservative_pressure.py",
    "01_imported_baseline/structure_preserving/conservative_viscosity.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def configure_determinism() -> dict[str, Any]:
    before = {
        "torch_num_threads": torch.get_num_threads(),
        "torch_num_interop_threads": torch.get_num_interop_threads(),
        "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "torch_default_dtype": str(torch.get_default_dtype()),
    }
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_default_dtype(torch.float64)
    after = {
        "torch_num_threads": torch.get_num_threads(),
        "torch_num_interop_threads": torch.get_num_interop_threads(),
        "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "torch_default_dtype": str(torch.get_default_dtype()),
    }
    return {"before": before, "during_preflight": after}


def field_values(
    x: torch.Tensor,
    probe: str,
    mode: tuple[int, int],
    *,
    rho0: float = 1.0,
    density_amplitude: float = 0.01,
    velocity_amplitude: float = 0.1,
    phase: float = 0.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    kappa = 2.0 * math.pi * torch.tensor(mode, dtype=x.dtype, device=x.device)
    k = torch.linalg.vector_norm(kappa)
    wave = x @ kappa + phase
    if probe == "density":
        rho = rho0 * (1.0 + density_amplitude * torch.sin(wave))
        velocity = x * 0.0
    else:
        rho = x[:, 0] * 0.0 + rho0
        direction = kappa / k
        if probe == "transverse":
            direction = torch.stack((-direction[1], direction[0]))
        velocity = velocity_amplitude * torch.sin(wave)[:, None] * direction[None, :]
    return rho, velocity


def evaluator_a(
    x: torch.Tensor,
    probe: str,
    mode: tuple[int, int],
    *,
    rho0: float = 1.0,
    c0: float = 10.0,
    density_amplitude: float = 0.01,
    velocity_amplitude: float = 0.1,
    phase: float = 0.0,
) -> dict[str, torch.Tensor]:
    """Frozen closed-form formula path."""

    kappa = 2.0 * math.pi * torch.tensor(mode, dtype=x.dtype, device=x.device)
    k2 = torch.dot(kappa, kappa)
    k = torch.sqrt(k2)
    wave = x @ kappa + phase
    sine = torch.sin(wave)
    cosine = torch.cos(wave)
    zero_scalar = torch.zeros(x.shape[0], dtype=x.dtype, device=x.device)
    zero_vector = torch.zeros_like(x)
    zero_matrix = torch.zeros((x.shape[0], 2, 2), dtype=x.dtype, device=x.device)
    if probe == "density":
        rho = rho0 * (1.0 + density_amplitude * sine)
        grad_rho = rho0 * density_amplitude * cosine[:, None] * kappa[None, :]
        velocity = zero_vector
        grad_velocity = zero_matrix
        lap_velocity = zero_vector
    else:
        rho = torch.full_like(zero_scalar, rho0)
        grad_rho = zero_vector
        direction = kappa / k
        if probe == "transverse":
            direction = torch.stack((-direction[1], direction[0]))
        velocity = velocity_amplitude * sine[:, None] * direction[None, :]
        grad_velocity = (
            velocity_amplitude
            * cosine[:, None, None]
            * direction[None, :, None]
            * kappa[None, None, :]
        )
        lap_velocity = -k2 * velocity
    pressure = c0**2 * (rho - rho0)
    grad_pressure = c0**2 * grad_rho
    divergence = grad_velocity[:, 0, 0] + grad_velocity[:, 1, 1]
    vorticity = grad_velocity[:, 1, 0] - grad_velocity[:, 0, 1]
    strain = 0.5 * (grad_velocity + grad_velocity.transpose(1, 2))
    return {
        "rho": rho,
        "grad_rho": grad_rho,
        "pressure": pressure,
        "grad_pressure": grad_pressure,
        "velocity": velocity,
        "grad_velocity": grad_velocity,
        "divergence": divergence,
        "vorticity": vorticity,
        "strain": strain,
        "lap_velocity": lap_velocity,
    }


def evaluator_b(
    x_input: torch.Tensor,
    probe: str,
    mode: tuple[int, int],
    *,
    rho0: float = 1.0,
    c0: float = 10.0,
    density_amplitude: float = 0.01,
    velocity_amplitude: float = 0.1,
    phase: float = 0.0,
) -> dict[str, torch.Tensor]:
    """Independent automatic-differentiation path from field values only."""

    x = x_input.detach().clone().requires_grad_(True)
    rho, velocity = field_values(
        x,
        probe,
        mode,
        rho0=rho0,
        density_amplitude=density_amplitude,
        velocity_amplitude=velocity_amplitude,
        phase=phase,
    )
    pressure = c0**2 * (rho - rho0)
    grad_rho = torch.autograd.grad(rho.sum(), x, create_graph=True)[0]
    grad_pressure = torch.autograd.grad(pressure.sum(), x, create_graph=True)[0]
    grad_components = []
    lap_components = []
    for component in range(2):
        grad_component = torch.autograd.grad(
            velocity[:, component].sum(), x, create_graph=True
        )[0]
        grad_components.append(grad_component)
        lap_component = torch.zeros(x.shape[0], dtype=x.dtype, device=x.device)
        for axis in range(2):
            if grad_component[:, axis].requires_grad:
                second = torch.autograd.grad(
                    grad_component[:, axis].sum(),
                    x,
                    retain_graph=True,
                    allow_unused=True,
                )[0]
            else:
                second = None
            if second is not None:
                lap_component = lap_component + second[:, axis]
        lap_components.append(lap_component)
    grad_velocity = torch.stack(grad_components, dim=1)
    lap_velocity = torch.stack(lap_components, dim=1)
    divergence = grad_velocity[:, 0, 0] + grad_velocity[:, 1, 1]
    vorticity = grad_velocity[:, 1, 0] - grad_velocity[:, 0, 1]
    strain = 0.5 * (grad_velocity + grad_velocity.transpose(1, 2))
    return {
        "rho": rho.detach(),
        "grad_rho": grad_rho.detach(),
        "pressure": pressure.detach(),
        "grad_pressure": grad_pressure.detach(),
        "velocity": velocity.detach(),
        "grad_velocity": grad_velocity.detach(),
        "divergence": divergence.detach(),
        "vorticity": vorticity.detach(),
        "strain": strain.detach(),
        "lap_velocity": lap_velocity.detach(),
    }


def linf_difference(left: torch.Tensor, right: torch.Tensor) -> float:
    if left.numel() == 0:
        return 0.0
    return float(torch.max(torch.abs(left.detach().cpu() - right.detach().cpu())))


def rms(value: torch.Tensor) -> float:
    return float(torch.sqrt(torch.mean(value.detach().double().square())))


def discrete_components(
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
    kernel = edge_kernel_values(neighborhood)
    gradient = edge_kernel_gradients(neighborhood)
    masses = torch.full((count,), mass, dtype=rho.dtype, device=rho.device)
    volumes = masses / rho
    density_sum = scatter_sum(row, masses[col] * kernel, count)
    interpolation_density = scatter_sum(
        row, volumes[col] * rho[col] * kernel, count
    )
    velocity_difference = velocity[col] - velocity[row]
    divergence = scatter_sum(
        row,
        volumes[col] * torch.sum(velocity_difference * gradient, dim=1),
        count,
    )
    density_rate = -rho * divergence
    pressure = c0**2 * (rho - rho0)
    pressure_acceleration = conservative_pressure_forces(
        neighborhood,
        mass=masses,
        density=rho,
        pressure=pressure,
    ) / masses[:, None]
    viscosity_acceleration = conservative_viscosity_acceleration(
        neighborhood,
        mass=masses,
        density=rho,
        velocity=velocity,
        physical_viscosity=nu,
    )
    acceleration = pressure_acceleration + viscosity_acceleration
    return {
        "density_sum": density_sum,
        "interpolation_density": interpolation_density,
        "divergence": divergence,
        "density_rate": density_rate,
        "pressure_acceleration": pressure_acceleration,
        "viscosity_acceleration": viscosity_acceleration,
        "acceleration": acceleration,
    }


def continuum_components(
    derivative: dict[str, torch.Tensor],
    *,
    nu: float,
) -> dict[str, torch.Tensor]:
    rho = derivative["rho"]
    pressure_acceleration = -derivative["grad_pressure"] / rho[:, None]
    viscosity_acceleration = nu * derivative["lap_velocity"]
    return {
        "density": rho,
        "density_rate": -rho * derivative["divergence"],
        "pressure_acceleration": pressure_acceleration,
        "viscosity_acceleration": viscosity_acceleration,
        "acceleration": pressure_acceleration + viscosity_acceleration,
    }


def defects(
    continuum: dict[str, torch.Tensor],
    discrete: dict[str, torch.Tensor],
) -> dict[str, torch.Tensor]:
    pressure = continuum["pressure_acceleration"] - discrete["pressure_acceleration"]
    viscosity = continuum["viscosity_acceleration"] - discrete["viscosity_acceleration"]
    return {
        "interpolation_density": continuum["density"] - discrete["interpolation_density"],
        "density_sum": continuum["density"] - discrete["density_sum"],
        "density_rate": continuum["density_rate"] - discrete["density_rate"],
        "pressure": pressure,
        "viscosity": viscosity,
        "acceleration": continuum["acceleration"] - discrete["acceleration"],
        "component_acceleration_sum": pressure + viscosity,
    }


def permute_neighborhood(
    neighborhood: PeriodicNeighborhood,
    permutation: torch.Tensor,
) -> PeriodicNeighborhood:
    return replace(
        neighborhood,
        row=neighborhood.row[permutation],
        col=neighborhood.col[permutation],
        displacement=neighborhood.displacement[permutation],
        distance=neighborhood.distance[permutation],
        edge_support=neighborhood.edge_support[permutation],
    )


def case_diagnostics(
    *,
    resolution: int,
    probe: str,
    mode: tuple[int, int],
    jitter: float,
    seed: int,
    dtype: torch.dtype,
) -> dict[str, Any]:
    positions, dx, layout_hash = periodic_cartesian_layout(
        resolution,
        jitter_fraction=jitter,
        seed=seed,
        dtype=dtype,
        domain_minimum=(0.0, 0.0),
        domain_maximum=(1.0, 1.0),
    )
    support = 4.0 * dx
    neighborhood = build_periodic_neighborhood(
        positions,
        support,
        domain_minimum=(0.0, 0.0),
        domain_maximum=(1.0, 1.0),
    )
    topology = audit_periodic_neighborhood(positions, neighborhood)
    a = evaluator_a(positions, probe, mode)
    b = evaluator_b(positions, probe, mode)
    derivative_errors = {name: linf_difference(a[name], b[name]) for name in a}
    nu = 0.01
    mass = dx**2
    continuum_a = continuum_components(a, nu=nu)
    continuum_b = continuum_components(b, nu=nu)
    discrete = discrete_components(
        neighborhood,
        a["rho"],
        a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    defect = defects(continuum_a, discrete)
    repeat = discrete_components(
        neighborhood,
        a["rho"],
        a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed + 1000 * resolution + mode[0] * 31 + mode[1] * 17)
    permutation = torch.randperm(neighborhood.row.numel(), generator=generator)
    permuted = permute_neighborhood(neighborhood, permutation)
    reordered = discrete_components(
        permuted,
        a["rho"],
        a["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    positions32 = positions.to(torch.float32)
    neighborhood32 = build_periodic_neighborhood(
        positions32,
        support,
        domain_minimum=(0.0, 0.0),
        domain_maximum=(1.0, 1.0),
    )
    a32 = evaluator_a(positions32, probe, mode)
    continuum32 = continuum_components(a32, nu=nu)
    discrete32 = discrete_components(
        neighborhood32,
        a32["rho"],
        a32["velocity"],
        mass=mass,
        c0=10.0,
        rho0=1.0,
        nu=nu,
    )
    defect32 = defects(continuum32, discrete32)
    operator_names = [
        "density_sum",
        "interpolation_density",
        "divergence",
        "density_rate",
        "pressure_acceleration",
        "viscosity_acceleration",
        "acceleration",
    ]
    repeat_errors = {name: linf_difference(discrete[name], repeat[name]) for name in operator_names}
    order_errors = {name: linf_difference(discrete[name], reordered[name]) for name in operator_names}
    dtype_operator_errors = {
        name: linf_difference(discrete[name], discrete32[name].double())
        for name in operator_names
    }
    dtype_target_errors = {
        name: linf_difference(defect[name], defect32[name].double())
        for name in defect
        if name != "component_acceleration_sum"
    }
    reference_errors = {
        name: linf_difference(continuum_a[name], continuum_b[name])
        for name in continuum_a
    }
    component_closure = linf_difference(defect["acceleration"], defect["component_acceleration_sum"])
    acceleration_sign_closure = linf_difference(
        discrete["acceleration"] + defect["acceleration"], continuum_a["acceleration"]
    )
    density_rate_sign_closure = linf_difference(
        discrete["density_rate"] + defect["density_rate"], continuum_a["density_rate"]
    )
    correction_sign_closure = max(acceleration_sign_closure, density_rate_sign_closure)
    edge_keys = torch.sort(neighborhood.row * neighborhood.particle_count + neighborhood.col).values
    permuted_edge_keys = torch.sort(permuted.row * permuted.particle_count + permuted.col).values
    edge_keys32 = torch.sort(neighborhood32.row * neighborhood32.particle_count + neighborhood32.col).values
    return {
        "case_id": f"F1_{probe}_n{resolution}_m{mode[0]}_{mode[1]}_j{jitter:.2f}",
        "resolution": resolution,
        "particle_count": int(positions.shape[0]),
        "probe": probe,
        "mode": list(mode),
        "jitter_fraction": jitter,
        "seed": seed,
        "dtype": str(dtype),
        "dx": dx,
        "support_h": support,
        "support_over_dx": support / dx,
        "kh": 2.0 * math.pi * math.hypot(*mode) * support,
        "points_per_wavelength": resolution / math.hypot(*mode),
        "layout_sha256": layout_hash,
        "edge_key_sha256": tensor_sha256(edge_keys),
        "topology": topology,
        "permuted_topology_key_equal": bool(torch.equal(edge_keys, permuted_edge_keys)),
        "derivative_a_vs_b_linf": derivative_errors,
        "continuum_a_vs_b_linf": reference_errors,
        "deterministic_repeat_linf": repeat_errors,
        "neighbor_order_linf": order_errors,
        "float32_vs_float64_operator_linf": dtype_operator_errors,
        "float32_vs_float64_target_linf": dtype_target_errors,
        "float32_topology_key_equal": bool(torch.equal(edge_keys, edge_keys32)),
        "component_closure_linf": component_closure,
        "positive_correction_identity_linf": correction_sign_closure,
        "positive_correction_acceleration_identity_linf": acceleration_sign_closure,
        "positive_correction_density_rate_identity_linf": density_rate_sign_closure,
        "target_rms": {name: rms(value) for name, value in defect.items() if name != "component_acceleration_sum"},
    }


def aggregate_max(cases: list[dict[str, Any]], path: tuple[str, ...]) -> float:
    values: list[float] = []
    for case in cases:
        node: Any = case
        for key in path:
            node = node[key]
        if isinstance(node, dict):
            values.extend(float(value) for value in node.values())
        else:
            values.append(float(node))
    return max(values, default=0.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="run both resolutions and regular/jitter layouts")
    args = parser.parse_args()
    determinism = configure_determinism()
    contract_hashes = {path: sha256(ROOT / path) for path in CONTRACT_PATHS}
    source_hashes = {path: sha256(ROOT / path) for path in SOURCE_PATHS}
    axes = json.loads((ROOT / "03_field_design/prospective_parameter_axes.json").read_text())
    seed = int(axes["pilot"]["seeds"][0])
    resolutions = axes["pilot"]["resolutions_per_axis"] if args.full else [16]
    jitters = axes["pilot"]["jitter_fractions"] if args.full else [0.0]
    modes = [tuple(mode) for mode in axes["pilot"]["mode_indices"]]
    cases = []
    for resolution in resolutions:
        for jitter in jitters:
            for mode in modes:
                for probe in ("density", "longitudinal", "transverse"):
                    cases.append(
                        case_diagnostics(
                            resolution=resolution,
                            probe=probe,
                            mode=mode,
                            jitter=float(jitter),
                            seed=seed,
                            dtype=torch.float64,
                        )
                    )
    topology_failure_fields = [
        "duplicate_edge_count",
        "missing_self_edge_count",
        "nonreciprocal_nonself_edge_count",
        "out_of_bounds_edge_count",
        "omitted_strict_support_edge_count",
        "unexpected_edge_count",
    ]
    topology_failures = {
        field: max(int(case["topology"][field]) for case in cases)
        for field in topology_failure_fields
    }
    output = {
        "schema_version": "1.0",
        "stage": "DDO-01A",
        "root": str(ROOT),
        "environment": {
            "python": sys.version,
            "python_executable": sys.executable,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "device": "cpu",
            "dtype": "torch.float64",
            "thread_environment": {
                key: os.environ.get(key)
                for key in (
                    "OMP_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS",
                    "NUMEXPR_NUM_THREADS",
                    "PYTHONHASHSEED",
                )
            },
            "determinism": determinism,
        },
        "contract_hashes": contract_hashes,
        "source_hashes": source_hashes,
        "case_count": len(cases),
        "cases": cases,
        "aggregate": {
            "derivative_a_vs_b_linf_max": aggregate_max(cases, ("derivative_a_vs_b_linf",)),
            "continuum_a_vs_b_linf_max": aggregate_max(cases, ("continuum_a_vs_b_linf",)),
            "deterministic_repeat_linf_max": aggregate_max(cases, ("deterministic_repeat_linf",)),
            "neighbor_order_linf_max": aggregate_max(cases, ("neighbor_order_linf",)),
            "float32_vs_float64_operator_linf_max": aggregate_max(cases, ("float32_vs_float64_operator_linf",)),
            "float32_vs_float64_target_linf_max": aggregate_max(cases, ("float32_vs_float64_target_linf",)),
            "component_closure_linf_max": aggregate_max(cases, ("component_closure_linf",)),
            "positive_correction_identity_linf_max": aggregate_max(cases, ("positive_correction_identity_linf",)),
            "minimum_image_linf_max": max(float(case["topology"]["minimum_image_linf"]) for case in cases),
            "topology_failure_counts_max": topology_failures,
            "all_permuted_topology_keys_equal": all(case["permuted_topology_key_equal"] for case in cases),
            "all_float32_topology_keys_equal": all(case["float32_topology_key_equal"] for case in cases),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
