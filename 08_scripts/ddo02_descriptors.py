#!/usr/bin/env python3
"""Reference-free higher-order and local-reconstruction descriptors for DDO-02."""

from __future__ import annotations

from typing import Any

import numpy as np


DESCRIPTOR_NAMES = (
    "moment2_lambda_min", "moment2_lambda_max", "moment2_trace", "moment2_det",
    "moment2_anisotropy", "moment3_frobenius", "moment3_contraction_norm",
    "moment4_frobenius", "moment4_double_trace", "moment_system_log10_condition",
    "angular_harmonic_1", "angular_harmonic_2", "angular_harmonic_3", "angular_harmonic_4",
    "pressure_baseline_frame_x", "pressure_baseline_frame_y",
    "viscosity_baseline_frame_x", "viscosity_baseline_frame_y",
    "rho_hessian_trace", "rho_hessian_det", "rho_hessian_frobenius",
    "pressure_hessian_frobenius", "velocity_hessian_x_frobenius",
    "velocity_hessian_y_frobenius", "velocity_laplacian_frame_x",
    "velocity_laplacian_frame_y", "rho_quadratic_residual", "velocity_quadratic_residual",
    "quadratic_log10_condition", "quadratic_failure_flag",
)


def _summarize(values: np.ndarray) -> np.ndarray:
    return np.concatenate((values.mean(0), values.std(0), values.min(0), values.max(0)))


def descriptor_specs() -> list[dict[str, Any]]:
    behavior = {}
    for name in DESCRIPTOR_NAMES:
        if name.endswith("frame_x") or name.endswith("frame_y"):
            behavior[name] = "O2_FRAME_COMPONENT; reflection parity follows frozen frame rule"
        else:
            behavior[name] = "O2_INVARIANT_SCALAR"
    return [
        {
            "name": name,
            "source_fields": [
                "obs__relative_position_over_h", "obs__distance_over_h",
                "obs__rho_over_rho0", "obs__velocity_difference_over_U0",
                "obs__pressure_acceleration_over_A0", "obs__viscosity_acceleration_over_A0",
            ],
            "reference_free": True,
            "rotation_behavior": behavior[name],
            "normalization": "dimensionless using h, rho0, U0, A0 already frozen in observable archive",
            "scope": "particle one-hop",
            "complexity": "O(neighbors) moments plus O(neighbors*5^2+5^3) weighted quadratic solve",
        }
        for name in DESCRIPTOR_NAMES
    ]


def compute_case_descriptors(obs: Any) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Return descriptors, observable O(2) frames, and conditioning counters for every particle."""
    row = np.asarray(obs["edge_row"], dtype=np.int64)
    rel = np.asarray(obs["obs__relative_position_over_h"], dtype=np.float64)
    dist = np.asarray(obs["obs__distance_over_h"], dtype=np.float64)
    rho = np.asarray(obs["obs__rho_over_rho0"], dtype=np.float64)
    dv = np.asarray(obs["obs__velocity_difference_over_U0"], dtype=np.float64)
    pressure = np.asarray(obs["obs__pressure_acceleration_over_A0"], dtype=np.float64)
    viscosity = np.asarray(obs["obs__viscosity_acceleration_over_A0"], dtype=np.float64)
    count = rho.size
    counts = np.bincount(row, minlength=count)
    indptr = np.concatenate(([0], np.cumsum(counts)))
    output = np.zeros((count, len(DESCRIPTOR_NAMES)), dtype=np.float64)
    frames = np.zeros((count, 2, 2), dtype=np.float64)
    failures = 0
    degeneracies = 0
    eps = np.finfo(np.float64).eps
    for particle in range(count):
        start, stop = int(indptr[particle]), int(indptr[particle + 1])
        r = rel[start:stop]
        d = dist[start:stop]
        delta_v = dv[start:stop]
        nonself = d > 1.0e-14
        r, d, delta_v = r[nonself], d[nonself], delta_v[nonself]
        if r.shape[0] == 0:
            output[particle, -1] = 1.0
            frames[particle] = np.eye(2)
            failures += 1
            continue
        w = np.exp(-(d * d)); w /= w.sum()
        m2 = np.einsum("n,ni,nj->ij", w, r, r)
        eig, vec = np.linalg.eigh(m2)
        axis = vec[:, 1]
        # Deterministic sign uses only observable geometry; second axis fixes det=+1.
        if axis[0] < 0 or (axis[0] == 0 and axis[1] < 0):
            axis = -axis
        frame = np.column_stack((axis, np.array([-axis[1], axis[0]])))
        gap = abs(eig[1] - eig[0]) / max(abs(eig).sum(), eps)
        if gap < 1.0e-6:
            frame = np.eye(2)
            degeneracies += 1
        frames[particle] = frame
        m3 = np.einsum("n,ni,nj,nk->ijk", w, r, r, r)
        m4 = np.einsum("n,ni,nj,nk,nl->ijkl", w, r, r, r, r)
        contraction3 = np.einsum("ijj->i", m3)
        theta = np.arctan2(r[:, 1], r[:, 0])
        harmonics = [abs(np.sum(w * np.exp(1j * order * theta))) for order in range(1, 5)]
        design = np.column_stack((r[:, 0], r[:, 1], .5*r[:, 0]**2,
                                  r[:, 0]*r[:, 1], .5*r[:, 1]**2))
        sw = np.sqrt(w)[:, None]
        weighted = design * sw
        condition = np.linalg.cond(weighted) if weighted.shape[0] >= 5 else np.inf
        rank = np.linalg.matrix_rank(weighted)
        failed = rank < 5 or not np.isfinite(condition) or condition > 1.0e12
        if failed:
            coeff_rho = np.zeros(5)
            coeff_v = np.zeros((5, 2))
            rho_residual = float(np.sqrt(np.sum(w * (rho[particle] * 0.0) ** 2)))
            velocity_residual = float(np.sqrt(np.sum(w[:, None] * delta_v**2)))
            failures += 1
        else:
            # rho_j-rho_i is obtained through edge column order implicit in stored edge rows.
            # Reconstruct it deterministically from the edge col array.
            cols = np.asarray(obs["edge_col"], dtype=np.int64)[start:stop][nonself]
            delta_rho = rho[cols] - rho[particle]
            coeff_rho = np.linalg.lstsq(weighted, delta_rho[:, None] * sw, rcond=None)[0][:, 0]
            coeff_v = np.linalg.lstsq(weighted, delta_v * sw, rcond=None)[0]
            rho_residual = float(np.sqrt(np.sum(w * (design @ coeff_rho - delta_rho)**2)))
            velocity_residual = float(np.sqrt(np.sum(w[:, None] * (design @ coeff_v - delta_v)**2)))
        hrho = np.array([[coeff_rho[2], coeff_rho[3]], [coeff_rho[3], coeff_rho[4]]])
        hvx = np.array([[coeff_v[2, 0], coeff_v[3, 0]], [coeff_v[3, 0], coeff_v[4, 0]]])
        hvy = np.array([[coeff_v[2, 1], coeff_v[3, 1]], [coeff_v[3, 1], coeff_v[4, 1]]])
        lap_v = np.array([np.trace(hvx), np.trace(hvy)])
        pframe = pressure[particle] @ frame
        vframe = viscosity[particle] @ frame
        lapframe = lap_v @ frame
        moment_design = np.column_stack((np.ones(r.shape[0]), r, r[:, 0]**2, r[:, 0]*r[:, 1], r[:, 1]**2))
        moment_cond = np.linalg.cond(moment_design * sw) if r.shape[0] >= 6 else np.inf
        values = (
            eig[0], eig[1], np.trace(m2), np.linalg.det(m2),
            (eig[1]-eig[0]) / max(eig.sum(), eps), np.linalg.norm(m3), np.linalg.norm(contraction3),
            np.linalg.norm(m4), np.einsum("iijj", m4), np.log10(min(moment_cond, 1.0e16)),
            *harmonics, pframe[0], pframe[1], vframe[0], vframe[1],
            np.trace(hrho), np.linalg.det(hrho), np.linalg.norm(hrho), 100.0*np.linalg.norm(hrho),
            np.linalg.norm(hvx), np.linalg.norm(hvy), lapframe[0], lapframe[1],
            rho_residual, velocity_residual, np.log10(min(condition, 1.0e16)), float(failed),
        )
        output[particle] = np.nan_to_num(values, nan=0.0, posinf=16.0, neginf=-16.0)
    return output.astype(np.float32), frames.astype(np.float32), {
        "quadratic_failure_count": failures,
        "directional_degeneracy_count": degeneracies,
        "particle_count": count,
    }


def context_blocks(values: np.ndarray, row: np.ndarray, col: np.ndarray,
                   particle_ids: list[int]) -> dict[str, np.ndarray]:
    count = values.shape[0]
    counts = np.bincount(row, minlength=count)
    indptr = np.concatenate(([0], np.cumsum(counts)))
    global_summary = _summarize(values)
    blocks = {"I0": [], "I1": [], "I2": [], "I3": []}
    for particle in particle_ids:
        start, stop = int(indptr[particle]), int(indptr[particle + 1])
        one = np.unique(col[start:stop])
        parts = [one]
        for neighbor in one:
            parts.append(col[indptr[neighbor]:indptr[neighbor+1]])
        two = np.unique(np.concatenate(parts))
        blocks["I0"].append(values[particle])
        blocks["I1"].append(_summarize(values[one]))
        blocks["I2"].append(_summarize(values[two]))
        blocks["I3"].append(global_summary)
    return {key: np.asarray(value, dtype=np.float32) for key, value in blocks.items()}
