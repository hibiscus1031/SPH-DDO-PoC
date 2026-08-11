#!/usr/bin/env python3
"""Build the fresh CA-04 DDO-01D observable/reference analytical atlas."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import platform
import sys
import zipfile
from collections import defaultdict
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
from structure_preserving.kernels import edge_kernel_gradients, edge_kernel_values, raw_gradient  # noqa: E402
from structure_preserving.neighborhood import (  # noqa: E402
    PeriodicNeighborhood,
    audit_periodic_neighborhood,
    build_periodic_neighborhood,
    tensor_sha256,
)


CA04_PATH = ROOT / "06_manifests/ca04_manifest.json"
REGISTRY_PATH = ROOT / "06_manifests/ddo01d_case_registry.json"
CA04_SHA256 = "a070527afdf604babf3401f665e9b53faed6f4ce77087583d879afd05e580a0f"
REGISTRY_SHA256 = "b4365cd02cd56d917282a490712247a3a287ce405261c4e80c474cc09739d1df"
DATA_DIR = ROOT / "data/atlas"
OBS_DIR = DATA_DIR / "observable_cases"
REF_DIR = DATA_DIR / "reference_cases"
CHECKPOINT_PATH = DATA_DIR / "ddo01d_case_checkpoint.jsonl"
OBS_INDEX_PATH = DATA_DIR / "ddo01d_observable_atlas.json"
REF_INDEX_PATH = DATA_DIR / "ddo01d_reference_target_atlas.json"
META_JSON_PATH = DATA_DIR / "ddo01d_case_metadata.json"
META_CSV_PATH = DATA_DIR / "ddo01d_case_metadata.csv"

COMPONENT_MAP = {
    "interpolation_density": "interpolation_density",
    "density_rate": "density_rate",
    "pressure_gradient_acceleration": "pressure",
    "viscosity_laplacian_acceleration": "viscosity",
    "total_acceleration": "acceleration",
}
VECTOR_COMPONENTS = {
    "pressure_gradient_acceleration", "viscosity_laplacian_acceleration", "total_acceleration",
}
COMPONENT_SCALES = {
    "interpolation_density": 1.0, "density_rate": 0.1,
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
H1_STATUS = {component: "H1_SIGNAL_PASS" for component in COMPONENT_MAP}
H2_STATUS = {
    "interpolation_density": "H2_SCALING_FAIL_REGULAR_SCOPE",
    "density_rate": "H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT",
    "pressure_gradient_acceleration": "H2_SCALING_PASS_REGULAR_SCOPE_ONLY",
    "viscosity_laplacian_acceleration": "H2_SCALING_PASS_REGULAR_SCOPE_ONLY",
    "total_acceleration": "H2_SCALING_PASS_REGULAR_SCOPE_ONLY",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tensor_max_abs(value: torch.Tensor) -> float:
    return float(value.detach().abs().max()) if value.numel() else 0.0


def case_rms(value: torch.Tensor, vector: bool) -> float:
    array = value.detach().cpu().numpy()
    return vector_case_rms(array) if vector else scalar_case_rms(array)


def periodic_layout(entry: dict[str, Any], dtype: torch.dtype = torch.float64) -> tuple[torch.Tensor, float, str]:
    resolution = int(entry["resolution_per_axis"])
    jitter_fraction = float(entry["jitter_fraction"])
    seed = int(entry["jitter_seed"] or 0)
    dx = 1.0 / resolution
    axis = (torch.arange(resolution, dtype=dtype) + 0.5) * dx
    gx, gy = torch.meshgrid(axis, axis, indexing="ij")
    positions = torch.stack((gx.reshape(-1), gy.reshape(-1)), dim=-1)
    if jitter_fraction:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        jitter = 2.0 * torch.rand(positions.shape, dtype=dtype, generator=generator) - 1.0
        positions = torch.remainder(positions + jitter_fraction * dx * jitter, 1.0)
    return positions, dx, tensor_sha256(positions)


def field_values_general(x: torch.Tensor, entry: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    modes = [tuple(value) for value in entry["mode_indices"]]
    phases = [float(value) for value in entry["phases_radians"]]
    probe = entry["probe"]
    count = len(modes)
    active = float(entry["active_amplitude"])
    amplitude = active / count if entry["macro_family"] == "F2" else active
    rho = x[:, 0] * 0.0 + 1.0
    velocity = x * 0.0
    for mode, phase in zip(modes, phases):
        kappa = 2.0 * math.pi * torch.tensor(mode, dtype=x.dtype, device=x.device)
        wave = x @ kappa + phase
        if probe == "density":
            rho = rho + amplitude * torch.sin(wave)
        else:
            direction = kappa / torch.linalg.vector_norm(kappa)
            if probe == "transverse":
                direction = torch.stack((-direction[1], direction[0]))
            velocity = velocity + amplitude * torch.sin(wave)[:, None] * direction[None, :]
    return rho, velocity


def evaluator_a_general(x: torch.Tensor, entry: dict[str, Any]) -> dict[str, torch.Tensor]:
    modes = [tuple(value) for value in entry["mode_indices"]]
    phases = [float(value) for value in entry["phases_radians"]]
    probe = entry["probe"]
    count = len(modes)
    active = float(entry["active_amplitude"])
    amplitude = active / count if entry["macro_family"] == "F2" else active
    rho = torch.ones(x.shape[0], dtype=x.dtype, device=x.device)
    grad_rho = torch.zeros_like(x)
    velocity = torch.zeros_like(x)
    grad_velocity = torch.zeros((x.shape[0], 2, 2), dtype=x.dtype, device=x.device)
    lap_velocity = torch.zeros_like(x)
    for mode, phase in zip(modes, phases):
        kappa = 2.0 * math.pi * torch.tensor(mode, dtype=x.dtype, device=x.device)
        k2 = torch.dot(kappa, kappa)
        wave = x @ kappa + phase
        sine, cosine = torch.sin(wave), torch.cos(wave)
        if probe == "density":
            rho = rho + amplitude * sine
            grad_rho = grad_rho + amplitude * cosine[:, None] * kappa[None, :]
        else:
            direction = kappa / torch.sqrt(k2)
            if probe == "transverse":
                direction = torch.stack((-direction[1], direction[0]))
            contribution = amplitude * sine[:, None] * direction[None, :]
            velocity = velocity + contribution
            grad_velocity = grad_velocity + amplitude * cosine[:, None, None] * direction[None, :, None] * kappa[None, None, :]
            lap_velocity = lap_velocity - k2 * contribution
    pressure = 100.0 * (rho - 1.0)
    grad_pressure = 100.0 * grad_rho
    divergence = grad_velocity[:, 0, 0] + grad_velocity[:, 1, 1]
    vorticity = grad_velocity[:, 1, 0] - grad_velocity[:, 0, 1]
    strain = 0.5 * (grad_velocity + grad_velocity.transpose(1, 2))
    return {
        "rho": rho, "grad_rho": grad_rho, "pressure": pressure,
        "grad_pressure": grad_pressure, "velocity": velocity,
        "grad_velocity": grad_velocity, "divergence": divergence,
        "vorticity": vorticity, "strain": strain, "lap_velocity": lap_velocity,
    }


def evaluator_b_general(x_input: torch.Tensor, entry: dict[str, Any]) -> dict[str, torch.Tensor]:
    x = x_input.detach().clone().requires_grad_(True)
    rho, velocity = field_values_general(x, entry)
    pressure = 100.0 * (rho - 1.0)
    grad_rho = torch.autograd.grad(rho.sum(), x, create_graph=True)[0]
    grad_pressure = torch.autograd.grad(pressure.sum(), x, create_graph=True)[0]
    gradients, laps = [], []
    for component in range(2):
        grad = torch.autograd.grad(velocity[:, component].sum(), x, create_graph=True)[0]
        gradients.append(grad)
        lap = torch.zeros(x.shape[0], dtype=x.dtype, device=x.device)
        for axis in range(2):
            if grad[:, axis].requires_grad:
                second = torch.autograd.grad(grad[:, axis].sum(), x, retain_graph=True, create_graph=True)[0][:, axis]
                lap = lap + second
        laps.append(lap)
    grad_velocity = torch.stack(gradients, dim=1)
    lap_velocity = torch.stack(laps, dim=1)
    divergence = grad_velocity[:, 0, 0] + grad_velocity[:, 1, 1]
    vorticity = grad_velocity[:, 1, 0] - grad_velocity[:, 0, 1]
    strain = 0.5 * (grad_velocity + grad_velocity.transpose(1, 2))
    return {
        "rho": rho.detach(), "grad_rho": grad_rho.detach(), "pressure": pressure.detach(),
        "grad_pressure": grad_pressure.detach(), "velocity": velocity.detach(),
        "grad_velocity": grad_velocity.detach(), "divergence": divergence.detach(),
        "vorticity": vorticity.detach(), "strain": strain.detach(), "lap_velocity": lap_velocity.detach(),
    }


def nominal_neighbor_count(ratio: float) -> int:
    extent = math.ceil(ratio)
    return sum(
        1 for i in range(-extent, extent + 1) for j in range(-extent, extent + 1)
        if (i != 0 or j != 0) and i * i + j * j <= ratio * ratio + 1.0e-12
    )


def scatter_sum(row: torch.Tensor, value: torch.Tensor, count: int) -> torch.Tensor:
    shape = (count, *value.shape[1:])
    return torch.zeros(shape, dtype=value.dtype).index_add_(0, row, value)


def observable_arrays(
    entry: dict[str, Any], neighborhood: PeriodicNeighborhood,
    derivative: dict[str, torch.Tensor], discrete: dict[str, torch.Tensor], mass: float,
) -> dict[str, np.ndarray]:
    row, col = neighborhood.row, neighborhood.col
    count = neighborhood.particle_count
    rho, velocity = derivative["rho"], derivative["velocity"]
    volumes = torch.full_like(rho, mass) / rho
    kernel = edge_kernel_values(neighborhood)
    gradient = edge_kernel_gradients(neighborhood)
    weights = volumes[col] * kernel
    weight_sum = scatter_sum(row, weights, count)
    rel_j_minus_i = -neighborhood.displacement
    covariance_terms = weights[:, None, None] * rel_j_minus_i[:, :, None] * rel_j_minus_i[:, None, :]
    covariance = scatter_sum(row, covariance_terms, count) / weight_sum.clamp_min(torch.finfo(rho.dtype).eps)[:, None, None]
    h = float(entry["support_h"])
    covariance_n = covariance / (h * h)
    eigen = torch.linalg.eigvalsh(covariance_n)
    eigen_min, eigen_max = eigen[:, 0], eigen[:, 1]
    eigen_ratio = eigen_min / (eigen_max + torch.finfo(rho.dtype).eps)
    anisotropy = (eigen_max - eigen_min) / (eigen_max + eigen_min + torch.finfo(rho.dtype).eps)

    nonself = row != col
    ns_row = row[nonself]
    ns_dist = neighborhood.distance[nonself]
    ns_one = torch.ones_like(ns_dist)
    neighbor_count = scatter_sum(ns_row, ns_one, count)
    sum_dist = scatter_sum(ns_row, ns_dist, count)
    sum_dist2 = scatter_sum(ns_row, ns_dist * ns_dist, count)
    safe_count = neighbor_count.clamp_min(1.0)
    mean_dist = sum_dist / safe_count
    distance_cv = torch.sqrt(torch.clamp(sum_dist2 / safe_count - mean_dist**2, min=0.0)) / (mean_dist + torch.finfo(rho.dtype).eps)
    nominal = nominal_neighbor_count(float(entry["support_over_dx"]))

    s0 = scatter_sum(row, weights, count)
    moment_terms = volumes[col, None, None] * rel_j_minus_i[:, :, None] * gradient[:, None, :]
    first_moment = scatter_sum(row, moment_terms, count)
    first_error = first_moment - torch.eye(2, dtype=rho.dtype)[None, :, :]
    first_frob = torch.linalg.matrix_norm(first_error, ord="fro", dim=(1, 2))
    grad_constant = scatter_sum(row, volumes[col, None] * gradient, count) * h

    grad_velocity = raw_gradient(neighborhood, velocity, volumes)
    divergence = grad_velocity[:, 0, 0] + grad_velocity[:, 1, 1]
    vorticity = grad_velocity[:, 1, 0] - grad_velocity[:, 0, 1]
    strain = 0.5 * (grad_velocity + grad_velocity.transpose(1, 2))
    strain_n = strain * h / 0.1
    strain_trace = strain_n[:, 0, 0] + strain_n[:, 1, 1]
    strain_det = strain_n[:, 0, 0] * strain_n[:, 1, 1] - strain_n[:, 0, 1] * strain_n[:, 1, 0]
    strain_frob = torch.linalg.matrix_norm(strain_n, ord="fro", dim=(1, 2))

    kh_values = torch.tensor(entry["kh_values"], dtype=rho.dtype)
    kh_rms = float(torch.sqrt(torch.mean(kh_values**2)))
    particle_id = torch.arange(count, dtype=torch.int64)
    arrays = {
        "particle_id": particle_id.numpy(),
        "edge_row": row.to(torch.int32).numpy(),
        "edge_col": col.to(torch.int32).numpy(),
        "obs__relative_position_over_h": (neighborhood.displacement / h).to(torch.float32).numpy(),
        "obs__distance_over_h": (neighborhood.distance / h).to(torch.float32).numpy(),
        "obs__velocity_difference_over_U0": ((velocity[col] - velocity[row]) / 0.1).to(torch.float32).numpy(),
        "obs__neighbor_count": neighbor_count.numpy(),
        "obs__neighbor_count_normalized": ((neighbor_count - nominal) / max(nominal, 1)).numpy(),
        "obs__support_h_over_L0": np.full(count, h, dtype=np.float64),
        "obs__support_over_dx": np.full(count, entry["support_over_dx"], dtype=np.float64),
        "obs__covariance_over_h2": covariance_n.numpy(),
        "obs__covariance_eigenvalues_over_h2": eigen.numpy(),
        "obs__covariance_eigenvalue_ratio": eigen_ratio.numpy(),
        "obs__anisotropy": anisotropy.numpy(),
        "obs__neighbor_distance_cv": distance_cv.numpy(),
        "obs__jitter_fraction": np.full(count, entry["jitter_fraction"], dtype=np.float64),
        "obs__zeroth_moment_error": (s0 - 1.0).numpy(),
        "obs__first_moment_error": first_error.numpy(),
        "obs__first_moment_error_frobenius": first_frob.numpy(),
        "obs__gradient_constant_times_h": grad_constant.numpy(),
        "obs__gradient_constant_times_h_norm": torch.linalg.vector_norm(grad_constant, dim=1).numpy(),
        "obs__kernel_volume": s0.numpy(),
        "obs__support_count_completeness": (neighbor_count / max(nominal, 1)).numpy(),
        "obs__rho_over_rho0": rho.numpy(),
        "obs__delta_rho_over_rho0": (rho - 1.0).numpy(),
        "obs__pressure_over_P0": ((100.0 * (rho - 1.0)) / 100.0).numpy(),
        "obs__sph_divergence_normalized": (h * divergence / 0.1).numpy(),
        "obs__sph_vorticity_normalized": (h * vorticity / 0.1).numpy(),
        "obs__strain_trace_normalized": strain_trace.numpy(),
        "obs__strain_frobenius_normalized": strain_frob.numpy(),
        "obs__strain_determinant_normalized": strain_det.numpy(),
        "obs__pressure_acceleration_over_A0": (discrete["pressure_acceleration"] / 0.01).numpy(),
        "obs__viscosity_acceleration_over_A0": (discrete["viscosity_acceleration"] / 0.01).numpy(),
        "obs__total_acceleration_over_A0": (discrete["acceleration"] / 0.01).numpy(),
        "obs__kh_max": np.full(count, entry["kh_max"], dtype=np.float64),
        "obs__kh_rms": np.full(count, kh_rms, dtype=np.float64),
        "obs__mode_count": np.full(count, len(entry["mode_indices"]), dtype=np.int16),
        "obs__mach": np.full(count, 0.01, dtype=np.float64),
        "obs__reynolds": np.full(count, 10.0, dtype=np.float64),
        "obs__eps64": np.full(count, EPS64, dtype=np.float64),
    }
    return arrays


def reference_arrays(
    continuum: dict[str, torch.Tensor], discrete: dict[str, torch.Tensor],
    target: dict[str, torch.Tensor], count: int,
) -> dict[str, np.ndarray]:
    return {
        "particle_id": np.arange(count, dtype=np.int64),
        "target_ref__continuum_density": continuum["density"].numpy(),
        "target_ref__continuum_density_rate": continuum["density_rate"].numpy(),
        "target_ref__continuum_pressure_acceleration": continuum["pressure_acceleration"].numpy(),
        "target_ref__continuum_viscosity_acceleration": continuum["viscosity_acceleration"].numpy(),
        "target_ref__continuum_total_acceleration": continuum["acceleration"].numpy(),
        "target_ref__sph_interpolation_density": discrete["interpolation_density"].numpy(),
        "target_ref__sph_density_rate": discrete["density_rate"].numpy(),
        "target_ref__sph_pressure_acceleration": discrete["pressure_acceleration"].numpy(),
        "target_ref__sph_viscosity_acceleration": discrete["viscosity_acceleration"].numpy(),
        "target_ref__sph_total_acceleration": discrete["acceleration"].numpy(),
        "target_ref__defect_interpolation_density": target["interpolation_density"].numpy(),
        "target_ref__defect_density_rate": target["density_rate"].numpy(),
        "target_ref__defect_pressure_acceleration": target["pressure"].numpy(),
        "target_ref__defect_viscosity_acceleration": target["viscosity"].numpy(),
        "target_ref__defect_total_acceleration": target["acceleration"].numpy(),
        "target_ref__normalized_defect_interpolation_density": (target["interpolation_density"] / 1.0).numpy(),
        "target_ref__normalized_defect_density_rate": (target["density_rate"] / 0.1).numpy(),
        "target_ref__normalized_defect_pressure_acceleration": (target["pressure"] / 0.01).numpy(),
        "target_ref__normalized_defect_viscosity_acceleration": (target["viscosity"] / 0.01).numpy(),
        "target_ref__normalized_defect_total_acceleration": (target["acceleration"] / 0.01).numpy(),
    }


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> str:
    temp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sorted(arrays):
            array = np.asarray(arrays[name])
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, array, allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    digest = sha256(temp)
    if path.exists():
        if sha256(path) != digest:
            raise RuntimeError(f"existing deterministic archive mismatch: {path}")
        temp.unlink()
    else:
        os.replace(temp, path)
    return digest


def archive_schema(arrays: dict[str, np.ndarray]) -> dict[str, Any]:
    return {
        name: {"dtype": str(np.asarray(value).dtype), "rank": np.asarray(value).ndim, "trailing_shape": list(np.asarray(value).shape[1:])}
        for name, value in sorted(arrays.items())
    }


class GeometryCache:
    def __init__(self) -> None:
        self.cache: dict[tuple[Any, ...], dict[str, Any]] = {}

    def get(self, entry: dict[str, Any]) -> dict[str, Any]:
        key = (entry["resolution_per_axis"], entry["support_over_dx"], entry["jitter_fraction"], entry["jitter_seed"] or 0)
        if key in self.cache:
            return self.cache[key]
        positions, dx, layout_hash = periodic_layout(entry)
        support = float(entry["support_h"])
        primary = build_periodic_neighborhood(positions, support, domain_minimum=(0.0, 0.0), domain_maximum=(1.0, 1.0))
        topology = audit_periodic_neighborhood(positions, primary)
        independent = independent_geometry_neighborhood(positions, support)
        primary_keys, independent_keys = topology_keys(primary), topology_keys(independent)
        independent_unique = int(torch.unique(independent_keys).numel()) == int(independent_keys.numel())
        independent_reciprocal = bool(torch.equal(independent_keys, torch.sort(independent.col * independent.particle_count + independent.row).values))
        positions32 = positions.to(torch.float32)
        precision_mode = "INDEPENDENT_FLOAT32_REBUILD"
        precision_error = None
        try:
            primary32 = build_periodic_neighborhood(positions32, support, domain_minimum=(0.0, 0.0), domain_maximum=(1.0, 1.0))
        except RuntimeError as exc:
            precision_mode = "PRIMARY_TOPOLOGY_CAST_FLOAT32"
            precision_error = str(exc)
            primary32 = PeriodicNeighborhood(
                row=primary.row, col=primary.col,
                displacement=primary.displacement.to(torch.float32), distance=primary.distance.to(torch.float32),
                edge_support=primary.edge_support.to(torch.float32), particle_support=primary.particle_support.to(torch.float32),
                domain_min=primary.domain_min.to(torch.float32), domain_max=primary.domain_max.to(torch.float32),
                particle_count=primary.particle_count,
            )
        result = {
            "positions": positions, "positions32": positions32, "dx": dx, "support": support,
            "layout_sha256": layout_hash, "primary": primary, "primary32": primary32,
            "independent": independent, "topology": topology,
            "primary_keys": primary_keys, "independent_keys": independent_keys,
            "independent_unique": independent_unique, "independent_reciprocal": independent_reciprocal,
            "topology_equal": bool(torch.equal(primary_keys, independent_keys)),
            "precision_mode": precision_mode, "precision_error": precision_error,
        }
        self.cache[key] = result
        print(f"geometry_ready N={entry['resolution_per_axis']} hdx={entry['support_over_dx']:g} jitter={entry['jitter_fraction']:g} seed={entry['jitter_seed'] or 0}", flush=True)
        return result


def run_case(entry: dict[str, Any], geometry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, np.ndarray], dict[str, np.ndarray]]:
    positions = geometry["positions"]
    primary, independent = geometry["primary"], geometry["independent"]
    dx = float(geometry["dx"])
    mass, nu = dx**2, 0.01
    derivative_a = evaluator_a_general(positions, entry)
    derivative_b = evaluator_b_general(positions, entry)
    continuum_a = continuum_components(derivative_a, nu=nu)
    continuum_b = continuum_components(derivative_b, nu=nu)
    discrete = discrete_components(primary, derivative_a["rho"], derivative_a["velocity"], mass=mass, c0=10.0, rho0=1.0, nu=nu)
    target = defects(continuum_a, discrete)
    reference_target = defects(continuum_b, discrete)
    repeat_discrete = discrete_components(primary, derivative_a["rho"], derivative_a["velocity"], mass=mass, c0=10.0, rho0=1.0, nu=nu)
    repeat_target = defects(continuum_a, repeat_discrete)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(entry["neighbor_permutation_seed"]))
    permuted = permute_neighborhood(primary, torch.randperm(primary.row.numel(), generator=generator))
    permuted_target = defects(continuum_a, discrete_components(permuted, derivative_a["rho"], derivative_a["velocity"], mass=mass, c0=10.0, rho0=1.0, nu=nu))
    compensated_target = defects(continuum_a, compensated_discrete_components(primary, derivative_a["rho"], derivative_a["velocity"], mass=mass, c0=10.0, rho0=1.0, nu=nu))
    geometry_target = defects(continuum_a, discrete_components(independent, derivative_a["rho"], derivative_a["velocity"], mass=mass, c0=10.0, rho0=1.0, nu=nu))
    derivative32 = evaluator_a_general(geometry["positions32"], entry)
    continuum32 = continuum_components(derivative32, nu=nu)
    discrete32 = discrete_components(geometry["primary32"], derivative32["rho"], derivative32["velocity"], mass=mass, c0=10.0, rho0=1.0, nu=nu)
    target32 = defects(continuum32, discrete32)

    sph_derivative = derivative_sph_channels(derivative_a, discrete, primary, mass=mass, nu=nu)
    derivative_gates = {}
    for name in derivative_a:
        scale = characteristic_scale(FROZEN_SCALES[name], derivative_a[name], sph_derivative[name])
        discrepancy = linf_difference(derivative_a[name], derivative_b[name])
        gate = C_FP * EPS64 * scale
        derivative_gates[name] = {"discrepancy": discrepancy, "gate": gate, "gate_fraction": discrepancy / gate, "pass": discrepancy <= gate}
    continuum_sph = continuum_sph_channels(discrete)
    scale_keys = {
        "density": "continuum_density", "density_rate": "continuum_density_rate",
        "pressure_acceleration": "continuum_pressure_acceleration",
        "viscosity_acceleration": "continuum_viscosity_acceleration", "acceleration": "continuum_acceleration",
    }
    continuum_gates = {}
    for name in continuum_a:
        scale = characteristic_scale(FROZEN_SCALES[scale_keys[name]], continuum_a[name], continuum_sph[name])
        discrepancy = linf_difference(continuum_a[name], continuum_b[name])
        gate = C_FP * EPS64 * scale
        continuum_gates[name] = {"discrepancy": discrepancy, "gate": gate, "gate_fraction": discrepancy / gate, "pass": discrepancy <= gate}

    identity = linf_difference(target["acceleration"], target["pressure"] + target["viscosity"])
    frozen_keys = {"interpolation_density": "interpolation_density", "density_rate": "density_rate", "pressure": "target_pressure", "viscosity": "target_viscosity", "acceleration": "target_acceleration"}
    uncertainties, components = {}, {}
    for canonical, internal in COMPONENT_MAP.items():
        analytic, sph = target_analytic_and_sph(internal, continuum_a, discrete)
        physical_scale = characteristic_scale(FROZEN_SCALES[frozen_keys[internal]], analytic, sph)
        u_round = C_FP * EPS64 * physical_scale
        delta_ref = linf_difference(target[internal], reference_target[internal])
        delta_repeat = linf_difference(target[internal], repeat_target[internal])
        delta_perm = linf_difference(target[internal], permuted_target[internal])
        delta_comp = linf_difference(target[internal], compensated_target[internal])
        delta_accum = max(delta_perm, delta_comp)
        delta_geometry = linf_difference(target[internal], geometry_target[internal])
        delta_identity = identity if internal == "acceleration" else 0.0
        u_num = u_round + delta_ref + delta_repeat + delta_accum + delta_geometry + delta_identity
        sign_residual = linf_difference(sph + target[internal], analytic)
        target_rms = case_rms(target[internal], canonical in VECTOR_COMPONENTS)
        continuum_rms = case_rms(analytic, canonical in VECTOR_COMPONENTS)
        uncertainties[canonical] = {
            "U_round": u_round, "Delta_ref": delta_ref, "Delta_repeat": delta_repeat,
            "Delta_perm": delta_perm, "Delta_comp": delta_comp, "Delta_accum": delta_accum,
            "Delta_geometry": delta_geometry, "Delta_identity": delta_identity, "U_num": u_num,
            "positive_additive_sign_residual": sign_residual, "positive_additive_sign_pass": sign_residual <= u_num,
            "precision_degradation_diagnostic": linf_difference(target[internal], target32[internal].double()),
            "all_terms_finite": bool(np.isfinite([u_round, delta_ref, delta_repeat, delta_perm, delta_comp, delta_geometry, delta_identity, u_num, sign_residual]).all()),
        }
        components[canonical] = {
            "role": entry["component_roles"][canonical], "units": UNITS[canonical],
            "H1_historical_status": H1_STATUS[canonical], "H2_historical_scope": H2_STATUS[canonical],
            "target_rms": target_rms, "component_scale": COMPONENT_SCALES[canonical],
            "normalized_target_rms": target_rms / COMPONENT_SCALES[canonical],
            "continuum_counterpart_rms": continuum_rms, "U_num": u_num, "U_round": u_round,
            "relative_effect_E_rel": target_rms / max(continuum_rms, u_round),
            "relative_effect_label": "DESCRIPTIVE_NOT_H2_GATE",
        }

    failure_fields = ("duplicate_edge_count", "missing_self_edge_count", "nonreciprocal_nonself_edge_count", "out_of_bounds_edge_count", "omitted_strict_support_edge_count", "unexpected_edge_count")
    primary_topology_pass = all(int(geometry["topology"][name]) == 0 for name in failure_fields)
    independent_pass = geometry["independent_unique"] and geometry["independent_reciprocal"] and geometry["topology_equal"]
    derivative_pass = all(item["pass"] for item in derivative_gates.values())
    continuum_pass = all(item["pass"] for item in continuum_gates.values())
    uncertainty_pass = all(item["all_terms_finite"] and item["positive_additive_sign_pass"] for item in uncertainties.values())
    closure_bound = uncertainties["total_acceleration"]["U_num"] + uncertainties["pressure_gradient_acceleration"]["U_num"] + uncertainties["viscosity_laplacian_acceleration"]["U_num"]
    closure_pass = identity <= closure_bound
    mandatory_pass = primary_topology_pass and independent_pass and derivative_pass and continuum_pass and uncertainty_pass and closure_pass

    obs = observable_arrays(entry, primary, derivative_a, discrete, mass)
    ref = reference_arrays(continuum_a, discrete, target, primary.particle_count)
    descriptor_nonfinite = {name: int(np.size(value) - np.isfinite(value).sum()) for name, value in obs.items() if np.issubdtype(np.asarray(value).dtype, np.number)}
    descriptor_nonfinite = {name: count for name, count in descriptor_nonfinite.items() if count}
    metadata = {
        "case_index": entry["case_index"], "canonical_case_id": entry["canonical_case_id"],
        "macro_family": entry["macro_family"], "data_role": "DEVELOPMENT_ATLAS",
        "resolution_per_axis": entry["resolution_per_axis"], "particle_count": primary.particle_count,
        "edge_count": int(primary.row.numel()), "dx": entry["dx"], "support_h": entry["support_h"],
        "support_over_dx": entry["support_over_dx"], "mode_indices": entry["mode_indices"],
        "kh_values": entry["kh_values"], "probe": entry["probe"], "polarization": entry["polarization"],
        "active_amplitude": entry["active_amplitude"], "phases_radians": entry["phases_radians"],
        "layout_class": entry["layout_class"], "jitter_fraction": entry["jitter_fraction"], "jitter_seed": entry["jitter_seed"],
        "f4_matched_block_id": entry.get("f4_matched_block_id"), "layout_sha256": geometry["layout_sha256"],
        "position_hash": geometry["layout_sha256"], "primary_edge_key_sha256": tensor_sha256(geometry["primary_keys"]),
        "independent_edge_key_sha256": tensor_sha256(geometry["independent_keys"]),
        "precision_diagnostic_topology_mode": geometry["precision_mode"],
        "precision_diagnostic_topology_error": geometry["precision_error"],
        "topology": geometry["topology"], "derivative_gates": derivative_gates,
        "continuum_gates": continuum_gates, "uncertainty": uncertainties,
        "components": components,
        "component_closure": {"residual": identity, "bound": closure_bound, "pass": closure_pass, "exact_particlewise_identity": identity == 0.0},
        "mandatory_audit": {
            "primary_topology_pass": primary_topology_pass, "independent_topology_pass": independent_pass,
            "derivative_pass": derivative_pass, "continuum_pass": continuum_pass,
            "uncertainty_and_sign_pass": uncertainty_pass, "component_closure_pass": closure_pass,
            "mandatory_case_pass": mandatory_pass,
            "release_label": "NUMERICAL_VALID" if mandatory_pass else "NUMERICAL_INVALID",
        },
        "descriptor_nonfinite_counts": descriptor_nonfinite,
        "reference_in_model_input": False,
    }
    return metadata, obs, ref


def load_checkpoint(registry: dict[str, Any]) -> list[dict[str, Any]]:
    if not CHECKPOINT_PATH.exists():
        return []
    rows = [json.loads(line) for line in CHECKPOINT_PATH.read_text().splitlines() if line.strip()]
    for index, row in enumerate(rows):
        if row["case_index"] != index or row["canonical_case_id"] != registry["cases"][index]["canonical_case_id"]:
            raise RuntimeError("checkpoint is not a canonical registry prefix")
        if sha256(ROOT / row["observable_archive_path"]) != row["observable_archive_sha256"]:
            raise RuntimeError("checkpoint observable hash mismatch")
        if sha256(ROOT / row["reference_archive_path"]) != row["reference_archive_sha256"]:
            raise RuntimeError("checkpoint reference hash mismatch")
    return rows


def write_indexes(cases: list[dict[str, Any]], obs_schema: dict[str, Any], ref_schema: dict[str, Any], source_audit: list[dict[str, Any]], environment: dict[str, Any]) -> None:
    obs_index = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01D",
        "side": "OBSERVABLE_SIDE", "reference_in_model_input": False,
        "case_count": len(cases), "particle_count": sum(case["particle_count"] for case in cases),
        "edge_count": sum(case["edge_count"] for case in cases), "schema": obs_schema,
        "normalization_source": "frozen_dimensional_scales_and_prescribed_case_parameters_only",
        "dataset_fitted_standardization_created": False,
        "cases": [{"case_index": case["case_index"], "canonical_case_id": case["canonical_case_id"], "path": case["observable_archive_path"], "sha256": case["observable_archive_sha256"]} for case in cases],
    }
    ref_index = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01D",
        "side": "REFERENCE_TARGET_SIDE", "eligible_as_model_input": False,
        "case_count": len(cases), "particle_count": sum(case["particle_count"] for case in cases),
        "schema": ref_schema,
        "cases": [{"case_index": case["case_index"], "canonical_case_id": case["canonical_case_id"], "path": case["reference_archive_path"], "sha256": case["reference_archive_sha256"]} for case in cases],
    }
    OBS_INDEX_PATH.write_text(json.dumps(obs_index, indent=2, sort_keys=True) + "\n")
    REF_INDEX_PATH.write_text(json.dumps(ref_index, indent=2, sort_keys=True) + "\n")
    metadata = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01D",
        "generated_date": "2026-08-11", "registry_sha256": REGISTRY_SHA256,
        "ca04_manifest_sha256": CA04_SHA256, "environment": environment,
        "source_hash_audit": source_audit, "case_count": len(cases), "cases": cases,
        "controls": {
            "h3_h4_evaluated": False, "target_pca_svd_performed": False,
            "nearest_neighbor_target_disagreement_performed": False,
            "conditional_target_variance_performed": False, "regression_performed": False,
            "predictive_score_computed": False, "model_fit": False, "neural_training": False,
            "time_integration": False, "rollout": False,
        },
    }
    META_JSON_PATH.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    columns = [
        "case_index", "canonical_case_id", "macro_family", "data_role", "resolution_per_axis",
        "particle_count", "edge_count", "dx", "support_h", "support_over_dx", "probe", "polarization",
        "active_amplitude", "layout_class", "jitter_fraction", "jitter_seed", "f4_matched_block_id",
        "precision_diagnostic_topology_mode", "mandatory_case_pass", "release_label",
        "component_closure_residual", "observable_archive_path", "observable_archive_sha256",
        "reference_archive_path", "reference_archive_sha256",
    ]
    with META_CSV_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for case in cases:
            writer.writerow({
                **{key: case.get(key) for key in columns},
                "mandatory_case_pass": case["mandatory_audit"]["mandatory_case_pass"],
                "release_label": case["mandatory_audit"]["release_label"],
                "component_closure_residual": case["component_closure"]["residual"],
            })


def main() -> None:
    final_paths = (OBS_INDEX_PATH, REF_INDEX_PATH, META_JSON_PATH, META_CSV_PATH)
    if any(path.exists() for path in final_paths):
        raise RuntimeError("final DDO-01D atlas indexes already exist; refusing replacement")
    if sha256(CA04_PATH) != CA04_SHA256 or sha256(REGISTRY_PATH) != REGISTRY_SHA256:
        raise RuntimeError("frozen CA-04 or DDO-01D registry hash mismatch")
    ca04 = json.loads(CA04_PATH.read_text())
    registry = json.loads(REGISTRY_PATH.read_text())
    if ca04["terminal_status"] != "DDO_CA04_ATLAS_DESIGN_AND_DESCRIPTOR_SCHEMA_FROZEN" or registry["case_count"] != 512:
        raise RuntimeError("CA-04 execution prerequisite failed")
    determinism = configure_determinism()
    source_audit = []
    for relative, expected in SOURCE_EXPECTED.items():
        observed = sha256(ROOT / relative)
        source_audit.append({"path": relative, "expected_sha256": expected, "observed_sha256": observed, "match": observed == expected})
    if not all(item["match"] for item in source_audit):
        raise RuntimeError("imported source hash audit failed")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OBS_DIR.mkdir(parents=True, exist_ok=True)
    REF_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_checkpoint(registry)
    cache = GeometryCache()
    obs_schema = None
    ref_schema = None
    mode = "a" if cases else "w"
    with CHECKPOINT_PATH.open(mode) as handle:
        for entry in registry["cases"][len(cases):]:
            geometry = cache.get(entry)
            metadata, obs, ref = run_case(entry, geometry)
            obs_path = OBS_DIR / f"case_{entry['case_index']:04d}.npz"
            ref_path = REF_DIR / f"case_{entry['case_index']:04d}.npz"
            metadata["observable_archive_path"] = str(obs_path.relative_to(ROOT))
            metadata["observable_archive_sha256"] = deterministic_npz(obs_path, obs)
            metadata["reference_archive_path"] = str(ref_path.relative_to(ROOT))
            metadata["reference_archive_sha256"] = deterministic_npz(ref_path, ref)
            if obs_schema is None:
                obs_schema = archive_schema(obs)
                ref_schema = archive_schema(ref)
            handle.write(json.dumps(metadata, sort_keys=True) + "\n")
            handle.flush()
            cases.append(metadata)
            print(f"case_complete {len(cases)}/512 {entry['macro_family']} {entry['canonical_case_id']}", flush=True)
    if obs_schema is None:
        with np.load(ROOT / cases[0]["observable_archive_path"]) as archive:
            obs_schema = archive_schema({key: archive[key] for key in archive.files})
        with np.load(ROOT / cases[0]["reference_archive_path"]) as archive:
            ref_schema = archive_schema({key: archive[key] for key in archive.files})
    environment = {
        "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "torch": torch.__version__,
        "platform": platform.platform(), "device": "cpu", "primary_dtype": "torch.float64",
        "C_fp": C_FP, "eps64": EPS64, "determinism": determinism,
    }
    write_indexes(cases, obs_schema, ref_schema, source_audit, environment)
    print(json.dumps({
        "case_count": len(cases),
        "mandatory_valid": sum(case["mandatory_audit"]["mandatory_case_pass"] for case in cases),
        "mandatory_invalid": sum(not case["mandatory_audit"]["mandatory_case_pass"] for case in cases),
        "observable_index_sha256": sha256(OBS_INDEX_PATH),
        "reference_index_sha256": sha256(REF_INDEX_PATH),
        "metadata_json_sha256": sha256(META_JSON_PATH),
        "metadata_csv_sha256": sha256(META_CSV_PATH),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
