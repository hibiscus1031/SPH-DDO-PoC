#!/usr/bin/env python3
"""Prepare and freeze prospective DDO-01B-R registry and excitation mask."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "06_manifests/ddo01br_case_registry.json"
MASK_PATH = ROOT / "06_manifests/ddo01br_excitation_mask.json"
STAGE_PREFIX = "DDO01B-R"
COMPONENTS = (
    "interpolation_density",
    "density_rate",
    "pressure_gradient_acceleration",
    "viscosity_laplacian_acceleration",
    "total_acceleration",
)


def digest_value(canonical_case_id: str, field_name: str) -> tuple[str, str]:
    hash_input = f"{STAGE_PREFIX}|{canonical_case_id}|{field_name}"
    return hash_input, hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


def seed_from_digest(digest: str) -> int:
    return int.from_bytes(bytes.fromhex(digest)[:8], "big") & ((1 << 63) - 1)


def excitation(probe: str, component: str) -> tuple[str, str]:
    if component == "interpolation_density":
        if probe == "density":
            return (
                "ANALYTICALLY_EXCITED",
                "rho*=rho0*(1+A_rho*sin(theta)) is nonconstant and the frozen density interpolation/state-reconstruction channel is not identically zero",
            )
        return (
            "ANALYTICALLY_EXCITED",
            "rho*=rho0 is nonzero; the frozen density interpolation/state-reconstruction channel is active and is not a zero operator",
        )
    if component == "density_rate":
        if probe == "longitudinal":
            return (
                "ANALYTICALLY_EXCITED",
                "div(v*)=A_v*k*cos(theta) is not identically zero, hence -rho*div(v*) is active",
            )
        if probe == "density":
            return (
                "ANALYTICALLY_UNEXCITED",
                "v*=0 implies div(v*)=0 and the frozen continuity operator -rho*div(v*) is identically zero",
            )
        return (
            "ANALYTICALLY_UNEXCITED",
            "v*=A_v*e_perp*sin(theta) with e_perp dot kappa=0 implies div(v*)=0 identically",
        )
    if component == "pressure_gradient_acceleration":
        if probe == "density":
            return (
                "ANALYTICALLY_EXCITED",
                "grad(p*)=c0^2*rho0*A_rho*kappa*cos(theta) is not identically zero",
            )
        return (
            "ANALYTICALLY_UNEXCITED",
            "rho*=rho0 implies p*=c0^2*(rho-rho0)=0 and grad(p*)=0 identically",
        )
    if component == "viscosity_laplacian_acceleration":
        if probe == "density":
            return (
                "ANALYTICALLY_UNEXCITED",
                "v*=0 implies nu*Laplacian(v*)=0 identically",
            )
        return (
            "ANALYTICALLY_EXCITED",
            "Laplacian(v*)=-|kappa|^2*v* is not identically zero for the nonzero velocity probe",
        )
    if component == "total_acceleration":
        if probe == "density":
            return (
                "ANALYTICALLY_EXCITED",
                "the pressure acceleration is not identically zero, so the total acceleration/RHS channel is active",
            )
        return (
            "ANALYTICALLY_EXCITED",
            "the viscous acceleration is not identically zero, so the total acceleration/RHS channel is active",
        )
    raise KeyError(component)


def build_registry() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for resolution in (16, 32):
        for mode in ((1, 0), (1, 1)):
            for probe in ("density", "longitudinal", "transverse"):
                for layout, jitter in (("regular", 0.0), ("jitter_0.05", 0.05)):
                    canonical = (
                        f"F1|N={resolution}|h_over_dx=4|mode={mode[0]},{mode[1]}|"
                        f"probe={probe}|layout={layout}"
                    )
                    phase_input, phase_digest = digest_value(canonical, "phase")
                    phase = 2.0 * math.pi * int(phase_digest, 16) / float(1 << 256)
                    jitter_input: str | None = None
                    jitter_digest: str | None = None
                    jitter_seed: int | None = None
                    if jitter > 0.0:
                        jitter_input, jitter_digest = digest_value(canonical, "jitter_seed")
                        jitter_seed = seed_from_digest(jitter_digest)
                    permutation_input, permutation_digest = digest_value(
                        canonical, "neighbor_permutation"
                    )
                    cases.append(
                        {
                            "case_index": len(cases),
                            "canonical_case_id": canonical,
                            "resolution_per_axis": resolution,
                            "support_over_dx": 4.0,
                            "mode_index": list(mode),
                            "probe": probe,
                            "layout_class": layout,
                            "jitter_fraction": jitter,
                            "phase_hash_input": phase_input,
                            "phase_sha256": phase_digest,
                            "phase_radians": phase,
                            "jitter_seed_hash_input": jitter_input,
                            "jitter_seed_sha256": jitter_digest,
                            "jitter_seed": jitter_seed,
                            "neighbor_permutation_hash_input": permutation_input,
                            "neighbor_permutation_sha256": permutation_digest,
                            "neighbor_permutation_seed": seed_from_digest(permutation_digest),
                        }
                    )
    return {
        "schema_version": "1.0",
        "project": "SPH-DDO-PoC",
        "stage": "DDO-01B-R",
        "registry_status": "FROZEN_BEFORE_TARGET_EVALUATION",
        "generation_rule": "SHA-256 of DDO01B-R|canonical_case_id|field_name",
        "scientific_axes": {
            "family": "F1",
            "resolutions_per_axis": [16, 32],
            "support_over_dx": [4.0],
            "mode_indices": [[1, 0], [1, 1]],
            "probes": ["density", "longitudinal", "transverse"],
            "layout_classes": ["regular", "jitter_0.05"],
            "density_amplitude": 0.01,
            "velocity_amplitude": 0.1,
            "kinematic_viscosity": 0.01,
        },
        "case_count": len(cases),
        "cases": cases,
        "historical_ddo01a_cases_used": False,
        "historical_ddo01ar_cases_used": False,
    }


def build_mask(registry_sha256: str, registry: dict[str, Any]) -> dict[str, Any]:
    pairs: list[dict[str, Any]] = []
    for case in registry["cases"]:
        for component in COMPONENTS:
            label, reason = excitation(case["probe"], component)
            pairs.append(
                {
                    "case_index": case["case_index"],
                    "canonical_case_id": case["canonical_case_id"],
                    "canonical_component_name": component,
                    "classification": label,
                    "analytical_reason": reason,
                }
            )
    return {
        "schema_version": "1.0",
        "project": "SPH-DDO-PoC",
        "stage": "DDO-01B-R",
        "mask_status": "FROZEN_BEFORE_TARGET_EVALUATION",
        "classification_basis": "frozen F1 analytical continuum field/operator identities only",
        "observed_sph_defect_used": False,
        "target_rms_used": False,
        "signal_uncertainty_ratio_used": False,
        "registry_path": "06_manifests/ddo01br_case_registry.json",
        "registry_sha256": registry_sha256,
        "components": list(COMPONENTS),
        "pair_count": len(pairs),
        "pairs": pairs,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if MASK_PATH.exists():
        raise RuntimeError("prospective excitation mask already exists; refusing replacement")
    registry = build_registry()
    rendered_registry = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    if REGISTRY_PATH.exists():
        if REGISTRY_PATH.read_text() != rendered_registry:
            raise RuntimeError("existing prospective registry differs from deterministic build")
    else:
        REGISTRY_PATH.write_text(rendered_registry)
    registry_hash = sha256(REGISTRY_PATH)
    mask = build_mask(registry_hash, registry)
    MASK_PATH.write_text(json.dumps(mask, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "registry_sha256": registry_hash,
        "mask_sha256": sha256(MASK_PATH),
        "case_count": registry["case_count"],
        "pair_count": mask["pair_count"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
