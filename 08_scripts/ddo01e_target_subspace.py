#!/usr/bin/env python3
"""Post-verdict descriptive target covariance-subspace diagnostic for DDO-01E."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/identifiability"
VERDICTS = DATA / "ddo01e_formal_verdicts.json"
METRICS = DATA / "ddo01e_metrics.json"
TARGET = DATA / "ddo01e_reference_target_cache.npz"
FEATURE = DATA / "ddo01e_observable_feature_cache.npz"
META = ROOT / "data/atlas/ddo01d_case_metadata.json"
OUTPUT = DATA / "ddo01e_target_subspace_diagnostic.json"

VERDICTS_SHA256 = "478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e"
METRICS_SHA256 = "871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subspace_summary(matrix: np.ndarray) -> dict[str, Any]:
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    _, singular, _ = np.linalg.svd(centered, full_matrices=False)
    variance = singular**2
    ratio = variance / variance.sum() if variance.sum() > 0 else np.zeros_like(variance)
    reconstruction = []
    total = float(np.sum(centered * centered))
    for rank in range(1, matrix.shape[1] + 1):
        residual = float(variance[rank:].sum())
        reconstruction.append({"rank": rank, "relative_reconstruction_rms": math.sqrt(residual / total) if total > 0 else 0.0})
    return {
        "sample_count": int(matrix.shape[0]), "coordinate_count": int(matrix.shape[1]),
        "explained_variance_ratio": ratio.tolist(), "cumulative_explained_variance_ratio": np.cumsum(ratio).tolist(),
        "relative_reconstruction_rms": reconstruction,
    }


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("target subspace diagnostic already exists; refusing replacement")
    if sha256(VERDICTS) != VERDICTS_SHA256 or sha256(METRICS) != METRICS_SHA256:
        raise RuntimeError("formal verdicts are not the frozen pre-SVD record")
    verdicts = json.loads(VERDICTS.read_text())
    if verdicts["verdicts_frozen_before_target_subspace_diagnostic"] is not True:
        raise RuntimeError("formal verdict freeze flag is absent")
    metadata = json.loads(META.read_text())["cases"]
    resolution_by_case = np.asarray([case["resolution_per_axis"] for case in metadata])
    with np.load(TARGET, allow_pickle=False) as target, np.load(FEATURE, allow_pickle=False) as feature:
        case_index = np.asarray(feature["sample_case_index"], dtype=np.int64)
        family = np.asarray(feature["sample_family"])
        density_rate = target["target__density_rate"][:, None] / 0.1
        pressure = target["target__pressure_gradient_acceleration"] / 0.01
        viscosity = target["target__viscosity_laplacian_acceleration"] / 0.01
        combined = np.column_stack((density_rate, pressure, viscosity))
        groups = {"overall": subspace_summary(combined)}
        for name in ("F1", "F2", "F3", "F4"):
            groups[f"family_{name}"] = subspace_summary(combined[family == name])
        sample_resolution = resolution_by_case[case_index]
        for resolution in sorted(set(resolution_by_case.tolist())):
            groups[f"resolution_{resolution}"] = subspace_summary(combined[sample_resolution == resolution])
        component_views = {
            "density_rate_scalar": subspace_summary(density_rate),
            "pressure_cartesian": subspace_summary(pressure),
            "viscosity_cartesian": subspace_summary(viscosity),
        }
    output = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "label": "TARGET_SUBSPACE_DIAGNOSTIC", "generated_date": "2026-08-11",
        "formal_verdicts_sha256_before_analysis": VERDICTS_SHA256,
        "formal_metrics_sha256_before_analysis": METRICS_SHA256,
        "coordinate_definition": ["density_rate/0.1", "pressure_x/0.01", "pressure_y/0.01", "viscosity_x/0.01", "viscosity_y/0.01"],
        "centering": "group mean", "analysis": "empirical linear covariance subspace only",
        "groups": groups, "component_views": component_views,
        "controls": {
            "formal_h3_h4_verdicts_changed": False, "observable_inputs_changed": False,
            "target_coordinates_enter_model_input": False, "physical_manifold_claim": False,
            "intrinsic_dimension_proof_claim": False,
        },
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output_sha256": sha256(OUTPUT), "formal_verdicts_unchanged_sha256": sha256(VERDICTS)}, indent=2, sort_keys=True))


import math

if __name__ == "__main__":
    main()
