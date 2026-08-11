#!/usr/bin/env python3
"""Pure prospective semantics for DDO-01E H3 diagnostics."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any, Iterable

import numpy as np


LAYER_FIELDS = {
    "G": (
        "obs__relative_position_over_h", "obs__distance_over_h",
        "obs__neighbor_count", "obs__neighbor_count_normalized",
        "obs__support_h_over_L0", "obs__support_over_dx",
        "obs__covariance_over_h2", "obs__covariance_eigenvalues_over_h2",
        "obs__covariance_eigenvalue_ratio", "obs__anisotropy",
        "obs__neighbor_distance_cv", "obs__jitter_fraction",
    ),
    "C": (
        "obs__zeroth_moment_error", "obs__first_moment_error",
        "obs__first_moment_error_frobenius", "obs__gradient_constant_times_h",
        "obs__gradient_constant_times_h_norm", "obs__kernel_volume",
        "obs__support_count_completeness",
    ),
    "P": (
        "obs__velocity_difference_over_U0", "obs__rho_over_rho0",
        "obs__delta_rho_over_rho0", "obs__pressure_over_P0",
        "obs__sph_divergence_normalized", "obs__sph_vorticity_normalized",
        "obs__strain_trace_normalized", "obs__strain_frobenius_normalized",
        "obs__strain_determinant_normalized", "obs__pressure_acceleration_over_A0",
        "obs__viscosity_acceleration_over_A0", "obs__total_acceleration_over_A0",
    ),
    "N": (
        "obs__kh_max", "obs__kh_rms", "obs__mode_count", "obs__mach",
        "obs__reynolds", "obs__eps64",
    ),
}

CONTENT_LAYERS = {"C0": ("G",), "C1": ("G", "C"), "C2": ("G", "C", "P"), "C3": ("G", "C", "P", "N")}
CONSTANT_EXCLUDED = ("obs__eps64", "obs__mach", "obs__reynolds")
PRIMARY_COMPONENTS = ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration")
DIAGNOSTIC_COMPONENTS = ("interpolation_density", "total_acceleration")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_fields(content: str) -> tuple[str, ...]:
    return tuple(field for layer in CONTENT_LAYERS[content] for field in LAYER_FIELDS[layer])


def lineage_payload(case: dict[str, Any]) -> dict[str, Any]:
    keys = ("macro_family", "field_subtype", "mode_indices", "phases_radians", "probe", "polarization", "active_amplitude")
    return {key: case[key] for key in keys}


def field_lineage_id(case: dict[str, Any]) -> str:
    return "DDO01E|FIELD_LINEAGE|" + digest(canonical_json(lineage_payload(case)))


def assign_diagnostic_folds(cases: list[dict[str, Any]], fold_count: int = 5) -> dict[str, int]:
    family_lineages: dict[str, set[str]] = defaultdict(set)
    case_lineage = {}
    for case in cases:
        lineage = field_lineage_id(case)
        case_lineage[case["canonical_case_id"]] = lineage
        family_lineages[case["macro_family"]].add(lineage)
    lineage_fold = {}
    for family in sorted(family_lineages):
        ordered = sorted(family_lineages[family], key=lambda value: digest(f"DDO01E|FOLD|{family}|{value}"))
        lineage_fold.update({lineage: index % fold_count for index, lineage in enumerate(ordered)})
    return {case_id: lineage_fold[lineage] for case_id, lineage in case_lineage.items()}


def selected_particle_ids(canonical_case_id: str, particle_count: int, sample_count: int = 128) -> list[int]:
    if particle_count < sample_count:
        raise ValueError("case contains fewer particles than the frozen sample count")
    return sorted(
        range(particle_count),
        key=lambda particle_id: (digest(f"DDO01E|PARTICLE|{canonical_case_id}|{particle_id}"), particle_id),
    )[:sample_count]


def fit_robust_scaler(train: np.ndarray, feature_names: Iterable[str]) -> dict[str, Any]:
    train = np.asarray(train, dtype=np.float64)
    names = tuple(feature_names)
    if train.ndim != 2 or train.shape[1] != len(names):
        raise ValueError("training matrix and feature names disagree")
    median = np.median(train, axis=0)
    q25 = np.quantile(train, 0.25, axis=0, method="inverted_cdf")
    q75 = np.quantile(train, 0.75, axis=0, method="inverted_cdf")
    iqr = q75 - q25
    retain = np.isfinite(median) & np.isfinite(iqr) & (iqr > 0)
    return {
        "feature_names": names, "median": median, "iqr": iqr, "retain": retain,
        "retained_names": tuple(name for name, keep in zip(names, retain) if keep),
        "excluded_names": tuple(name for name, keep in zip(names, retain) if not keep),
    }


def transform_robust(values: np.ndarray, scaler: dict[str, Any]) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    retain = scaler["retain"]
    if not retain.any():
        raise ValueError("no nonconstant feature remains")
    return (values[:, retain] - scaler["median"][retain]) / scaler["iqr"][retain]


def target_trace_variance(target: np.ndarray, case_ids: np.ndarray) -> float:
    target = np.asarray(target, dtype=np.float64)
    if target.ndim == 1:
        target = target[:, None]
    case_ids = np.asarray(case_ids)
    case_means = []
    case_second = []
    for case in np.unique(case_ids):
        rows = target[case_ids == case]
        case_means.append(rows.mean(axis=0))
        case_second.append(np.mean(np.sum(rows * rows, axis=1)))
    mean = np.mean(case_means, axis=0)
    return float(np.mean(case_second) - np.dot(mean, mean))


def conditional_variance_ratios(neighbor_targets: np.ndarray, unconditional_trace: float) -> np.ndarray:
    values = np.asarray(neighbor_targets, dtype=np.float64)
    if values.ndim == 2:
        values = values[:, :, None]
    centered = values - values.mean(axis=1, keepdims=True)
    local_trace = np.sum(centered * centered, axis=(1, 2)) / (values.shape[1] - 1)
    return local_trace / unconditional_trace


def equal_case_nrmse(target: np.ndarray, prediction: np.ndarray, case_ids: np.ndarray) -> float:
    target = np.asarray(target, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    if target.ndim == 1:
        target, prediction = target[:, None], prediction[:, None]
    case_ids = np.asarray(case_ids)
    error_ms, target_ms = [], []
    for case in np.unique(case_ids):
        mask = case_ids == case
        error_ms.append(np.mean(np.sum((prediction[mask] - target[mask]) ** 2, axis=1)))
        target_ms.append(np.mean(np.sum(target[mask] ** 2, axis=1)))
    denominator = float(np.mean(target_ms))
    return float(np.sqrt(np.mean(error_ms) / denominator)) if denominator > 0 else math.inf


def h3_gate(metrics: dict[str, Any]) -> str:
    required = (
        "dnn_median", "dnn_p90", "cvar", "cvar_upper95", "oracle_nrmse",
        "baseline_improvement", "max_family_nrmse", "coverage",
    )
    if metrics.get("execution_complete") is not True or any(key not in metrics or not np.isfinite(metrics[key]) for key in required):
        return "H3_IDENTIFIABILITY_UNRESOLVED"
    passed = (
        metrics["dnn_median"] <= 0.25 and metrics["dnn_p90"] <= 0.60
        and metrics["cvar"] <= 0.25 and metrics["cvar_upper95"] <= 0.35
        and metrics["oracle_nrmse"] <= 0.50 and metrics["baseline_improvement"] >= 0.20
        and metrics["max_family_nrmse"] <= 0.75 and metrics["coverage"] >= 0.90
    )
    return "H3_OBSERVABLE_MAPPING_IDENTIFIABLE" if passed else "H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE"


def project_status(primary_h3: dict[str, str], primary_h4: dict[str, str]) -> str:
    statuses = [primary_h3[name] for name in PRIMARY_COMPONENTS]
    if all(status == "H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE" for status in statuses):
        return "DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE"
    if len(set(statuses)) != 1 or statuses[0] != "H3_OBSERVABLE_MAPPING_IDENTIFIABLE":
        return "DDO01E_COMPONENTWISE_IDENTIFIABILITY_MIXED"
    bounded = {"PARTICLE_LOCAL_INFORMATION_SUFFICIENT", "ONE_HOP_LOCALITY_SUPPORTED", "EXTENDED_BOUNDED_LOCALITY_SUPPORTED"}
    if all(primary_h4[name] in bounded for name in PRIMARY_COMPONENTS):
        return "DDO01E_OBSERVABLE_MAPPING_AND_LOCALITY_QUALIFIED"
    return "DDO01E_IDENTIFIABILITY_QUALIFIED_LOCALITY_PARTIAL"


import math  # kept last so pure constants above remain visually auditable

