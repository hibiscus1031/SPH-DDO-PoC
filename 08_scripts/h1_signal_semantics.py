#!/usr/bin/env python3
"""Pure deterministic CA-02 H1 signal-qualification semantics."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np


BOOTSTRAP_REPLICATES = 10_000
POINT_THRESHOLD = 10.0
BOOTSTRAP_LOWER_THRESHOLD = 5.0
MINIMUM_ELIGIBLE_CASES = 8
SEED_PREFIX = "DDO01B-H1-BOOTSTRAP|"


def scalar_case_rms(values: Sequence[float] | np.ndarray) -> float:
    """RMS over particles for one scalar target; Cartesian pooling is absent."""

    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.isfinite(array).all():
        raise ValueError("scalar target must be a nonempty finite one-dimensional array")
    return float(np.sqrt(np.mean(np.square(array), dtype=np.float64)))


def vector_case_rms(values: Sequence[Sequence[float]] | np.ndarray) -> float:
    """RMS of per-particle Euclidean magnitudes without division by dimension."""

    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError("vector target must be a nonempty two-dimensional array")
    if not np.isfinite(array).all():
        raise ValueError("vector target must be finite")
    squared_norm = np.sum(np.square(array), axis=1, dtype=np.float64)
    return float(np.sqrt(np.mean(squared_norm, dtype=np.float64)))


def equal_case_component_rms(case_rms_values: Sequence[float] | np.ndarray) -> float:
    """Equal-case-weighted component RMS over analytically excited valid cases."""

    values = _positive_or_zero_vector(case_rms_values, "case RMS")
    if values.size == 0:
        raise ValueError("at least one eligible case RMS is required")
    return float(np.sqrt(np.mean(np.square(values), dtype=np.float64)))


def max_case_uncertainty(case_uncertainties: Sequence[float] | np.ndarray) -> float:
    """Conservative CA-02 component uncertainty U_c."""

    values = _positive_or_zero_vector(case_uncertainties, "case uncertainty")
    if values.size == 0 or np.any(values <= 0.0):
        raise ValueError("eligible case uncertainties must be finite and positive")
    return float(np.max(values))


def case_ratios(
    case_rms_values: Sequence[float] | np.ndarray,
    case_uncertainties: Sequence[float] | np.ndarray,
) -> np.ndarray:
    targets = _positive_or_zero_vector(case_rms_values, "case RMS")
    uncertainties = _positive_or_zero_vector(case_uncertainties, "case uncertainty")
    if targets.shape != uncertainties.shape or np.any(uncertainties <= 0.0):
        raise ValueError("case RMS and positive uncertainty arrays must have equal shape")
    return targets / uncertainties


def component_point_ratio(component_rms: float, component_uncertainty: float) -> float:
    if not math.isfinite(component_rms) or component_rms < 0.0:
        raise ValueError("component RMS must be finite and nonnegative")
    if not math.isfinite(component_uncertainty) or component_uncertainty <= 0.0:
        raise ValueError("component uncertainty must be finite and positive")
    return float(component_rms / component_uncertainty)


def deterministic_seed(canonical_component_name: str) -> dict[str, Any]:
    """Map the full SHA-256 digest, big-endian, to a PCG64 seed integer."""

    if not canonical_component_name:
        raise ValueError("canonical component name must be nonempty")
    hash_input = SEED_PREFIX + canonical_component_name
    digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    return {
        "hash_input": hash_input,
        "sha256": digest,
        "seed_integer": int(digest, 16),
        "mapping": "full SHA-256 digest interpreted as an unsigned big-endian integer",
        "bit_generator": "numpy.random.PCG64",
    }


def stratified_group_bootstrap(
    case_rms_values: Sequence[float] | np.ndarray,
    case_uncertainties: Sequence[float] | np.ndarray,
    strata: Sequence[tuple[Any, Any]],
    canonical_component_name: str,
    *,
    replicates: int = BOOTSTRAP_REPLICATES,
) -> np.ndarray:
    """Return R_c^(b), stratifying complete eligible cases by resolution/layout."""

    targets = _positive_or_zero_vector(case_rms_values, "case RMS")
    uncertainties = _positive_or_zero_vector(case_uncertainties, "case uncertainty")
    if targets.size == 0 or targets.shape != uncertainties.shape:
        raise ValueError("eligible target and uncertainty arrays must be nonempty and aligned")
    if np.any(uncertainties <= 0.0) or len(strata) != targets.size:
        raise ValueError("positive uncertainties and one stratum per eligible case are required")
    if not isinstance(replicates, int) or replicates <= 0:
        raise ValueError("replicates must be a positive integer")

    groups: dict[tuple[Any, Any], list[int]] = defaultdict(list)
    for index, stratum in enumerate(strata):
        if not isinstance(stratum, tuple) or len(stratum) != 2:
            raise ValueError("each stratum must be a (resolution, layout_class) tuple")
        groups[stratum].append(index)

    ordered_groups = [np.asarray(groups[key], dtype=np.int64) for key in sorted(groups)]
    fixed_uncertainty = max_case_uncertainty(uncertainties)
    seed = deterministic_seed(canonical_component_name)["seed_integer"]
    generator = np.random.Generator(np.random.PCG64(seed))
    bootstrap_ratios = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        sampled_parts = [
            generator.choice(indices, size=indices.size, replace=True)
            for indices in ordered_groups
        ]
        sampled = np.concatenate(sampled_parts)
        target = equal_case_component_rms(targets[sampled])
        bootstrap_ratios[replicate] = target / fixed_uncertainty
    return bootstrap_ratios


def inverted_cdf_lower_bound(bootstrap_ratios: Sequence[float] | np.ndarray) -> float:
    values = _positive_or_zero_vector(bootstrap_ratios, "bootstrap ratio")
    if values.size == 0:
        raise ValueError("bootstrap ratio array must be nonempty")
    return float(np.quantile(values, 0.05, method="inverted_cdf"))


def case_label(*, analytically_excited: bool, mandatory_audit_valid: bool, ratio: float | None) -> str:
    if not analytically_excited:
        return "CASE_NOT_APPLICABLE_UNEXCITED"
    if not mandatory_audit_valid or ratio is None or not math.isfinite(ratio):
        return "CASE_UNRESOLVED"
    return "CASE_SIGNAL_PASS" if ratio >= POINT_THRESHOLD else "CASE_SIGNAL_LOW"


def component_verdict(
    *,
    eligible_case_count: int,
    mandatory_audits_valid: bool,
    point_ratio: float | None,
    bootstrap_lower_bound: float | None,
) -> str:
    if eligible_case_count < MINIMUM_ELIGIBLE_CASES or not mandatory_audits_valid:
        return "H1_SIGNAL_UNRESOLVED"
    if (
        point_ratio is None
        or bootstrap_lower_bound is None
        or not math.isfinite(point_ratio)
        or not math.isfinite(bootstrap_lower_bound)
    ):
        return "H1_SIGNAL_UNRESOLVED"
    if point_ratio >= POINT_THRESHOLD and bootstrap_lower_bound > BOOTSTRAP_LOWER_THRESHOLD:
        return "H1_SIGNAL_PASS"
    return "H1_SIGNAL_FAIL"


def evaluate_component(
    *,
    case_rms_values: Sequence[float] | np.ndarray,
    case_uncertainties: Sequence[float] | np.ndarray,
    strata: Sequence[tuple[Any, Any]],
    canonical_component_name: str,
    mandatory_audits_valid: bool,
    replicates: int = BOOTSTRAP_REPLICATES,
) -> dict[str, Any]:
    """Construct every CA-02 component statistic from eligible valid cases."""

    targets = _positive_or_zero_vector(case_rms_values, "case RMS")
    uncertainties = _positive_or_zero_vector(case_uncertainties, "case uncertainty")
    if targets.size < MINIMUM_ELIGIBLE_CASES or not mandatory_audits_valid:
        return {
            "eligible_case_count": int(targets.size),
            "verdict": "H1_SIGNAL_UNRESOLVED",
            "T_c": None,
            "U_c": None,
            "R_c": None,
            "M_point": None,
            "L95_c": None,
            "M_boot": None,
        }
    target = equal_case_component_rms(targets)
    uncertainty = max_case_uncertainty(uncertainties)
    ratio = component_point_ratio(target, uncertainty)
    boot = stratified_group_bootstrap(
        targets,
        uncertainties,
        strata,
        canonical_component_name,
        replicates=replicates,
    )
    lower = inverted_cdf_lower_bound(boot)
    return {
        "eligible_case_count": int(targets.size),
        "verdict": component_verdict(
            eligible_case_count=int(targets.size),
            mandatory_audits_valid=mandatory_audits_valid,
            point_ratio=ratio,
            bootstrap_lower_bound=lower,
        ),
        "T_c": target,
        "U_c": uncertainty,
        "R_c": ratio,
        "M_point": ratio / POINT_THRESHOLD,
        "L95_c": lower,
        "M_boot": lower / BOOTSTRAP_LOWER_THRESHOLD,
    }


def _positive_or_zero_vector(values: Iterable[float] | np.ndarray, label: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or not np.isfinite(array).all() or np.any(array < 0.0):
        raise ValueError(f"{label} must be a finite nonnegative one-dimensional array")
    return array


__all__ = [
    "BOOTSTRAP_REPLICATES",
    "BOOTSTRAP_LOWER_THRESHOLD",
    "MINIMUM_ELIGIBLE_CASES",
    "POINT_THRESHOLD",
    "case_label",
    "case_ratios",
    "component_point_ratio",
    "component_verdict",
    "deterministic_seed",
    "equal_case_component_rms",
    "evaluate_component",
    "inverted_cdf_lower_bound",
    "max_case_uncertainty",
    "scalar_case_rms",
    "stratified_group_bootstrap",
    "vector_case_rms",
]
