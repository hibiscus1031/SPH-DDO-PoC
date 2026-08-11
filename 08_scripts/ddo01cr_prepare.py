#!/usr/bin/env python3
"""Materialize the exact CA-03 DDO-01C-R registry before target evaluation."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))

from h2_scaling_semantics import deterministic_pool_permutation  # noqa: E402


CA03_PATH = ROOT / "06_manifests/ca03_manifest.json"
REGISTRY_PATH = ROOT / "06_manifests/ddo01cr_case_registry.json"
EXPECTED_CA03_SHA256 = "321b37f81ddd81c2407f81dd17825e64e605a603f5f70ec324d0a1663a9acd3c"
PHASE_POOL = [0.0, math.pi / 4.0, math.pi / 2.0]
SEED_POOL = [20260811, 20260817, 20260823]

TRACKS: dict[str, dict[str, Any]] = {
    "D005": {"probe": "density", "polarization": "none", "density_amplitude": 0.005, "velocity_amplitude": 0.1, "support_ratio": False},
    "D010": {"probe": "density", "polarization": "none", "density_amplitude": 0.01, "velocity_amplitude": 0.1, "support_ratio": True},
    "V050": {"probe": "longitudinal", "polarization": "longitudinal", "density_amplitude": 0.01, "velocity_amplitude": 0.05, "support_ratio": False},
    "V100": {"probe": "longitudinal", "polarization": "longitudinal", "density_amplitude": 0.01, "velocity_amplitude": 0.1, "support_ratio": True},
}

COMPONENT_TRACKS = {
    "interpolation_density": ["D005", "D010"],
    "density_rate": ["V050", "V100"],
    "pressure_gradient_acceleration": ["D005", "D010"],
    "viscosity_laplacian_acceleration": ["V050", "V100"],
    "total_acceleration": ["D005", "D010", "V050", "V100"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(value: float) -> str:
    return format(value, ".17g")


def seed63(digest: str) -> int:
    return int.from_bytes(bytes.fromhex(digest)[:8], "big") & ((1 << 63) - 1)


def pair_track_id(track: str, spec: dict[str, Any]) -> str:
    return (
        f"F1|track={track}|probe={spec['probe']}|polarization={spec['polarization']}|"
        f"direction=1,0|density_amplitude={token(spec['density_amplitude'])}|"
        f"velocity_amplitude={token(spec['velocity_amplitude'])}|rho0=1|c0=10|"
        "nu=0.01|dtype=float64"
    )


def configurations(track: str) -> list[tuple[int, float, tuple[int, int]]]:
    values = {(n, 4.0, (1, 0)) for n in (16, 24, 32, 48, 64)}
    values.update({(64, 4.0, mode) for mode in ((1, 0), (2, 0), (3, 0))})
    if TRACKS[track]["support_ratio"]:
        values.update({(64, ratio, (1, 0)) for ratio in (2.0, 3.0, 4.0, 5.0)})
    return sorted(values, key=lambda item: (item[0], item[1], item[2]))


def family_labels(track: str, resolution: int, ratio: float, mode: tuple[int, int]) -> list[str]:
    labels = []
    if ratio == 4.0 and mode == (1, 0) and resolution in (16, 24, 32, 48, 64):
        labels.append("REFINEMENT_H")
    if resolution == 64 and ratio == 4.0 and mode in ((1, 0), (2, 0), (3, 0)):
        labels.append("SPECTRAL_KH")
    if TRACKS[track]["support_ratio"] and resolution == 64 and mode == (1, 0) and ratio in (2.0, 3.0, 4.0, 5.0):
        labels.append("SUPPORT_RATIO_HDX")
    labels.append("REGULAR_VS_DISORDER")
    return labels


def build_registry() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    mapping_records: dict[str, Any] = {}
    for track, spec in TRACKS.items():
        pair_id = pair_track_id(track, spec)
        phases, phase_records = deterministic_pool_permutation(PHASE_POOL, "DDO01CR|PHASE", pair_id, 3)
        seeds, seed_records = deterministic_pool_permutation(SEED_POOL, "DDO01CR|JITTER", pair_id, 3)
        mapping_records[track] = {
            "canonical_pair_track_id": pair_id,
            "phase_mapping": phase_records,
            "jitter_seed_mapping": seed_records,
        }
        for resolution, ratio, mode in configurations(track):
            dx = 1.0 / resolution
            support = ratio * dx
            k = 2.0 * math.pi * math.hypot(*mode)
            kh = k * support
            for layout, jitter_fraction in (("regular", 0.0), ("jitter_0.05", 0.05)):
                for replicate in range(3):
                    phase = float(phases[replicate])
                    paired_seed = int(seeds[replicate])
                    actual_seed = None if layout == "regular" else paired_seed
                    canonical = (
                        f"F1|track={track}|N={resolution}|h_over_dx={token(ratio)}|"
                        f"mode={mode[0]},{mode[1]}|replicate={replicate}|phase={token(phase)}|"
                        f"layout={layout}|jitter_fraction={token(jitter_fraction)}|"
                        f"jitter_seed={actual_seed if actual_seed is not None else 'null'}|dtype=float64"
                    )
                    permutation_input = f"DDO01CR|NEIGHBOR_PERMUTATION|{canonical}"
                    permutation_digest = hashlib.sha256(permutation_input.encode("utf-8")).hexdigest()
                    pair_input = (
                        f"DDO01CR|PAIR|track={track}|N={resolution}|h_over_dx={token(ratio)}|"
                        f"mode={mode[0]},{mode[1]}|replicate={replicate}"
                    )
                    pair_digest = hashlib.sha256(pair_input.encode("utf-8")).hexdigest()
                    cases.append({
                        "case_index": len(cases),
                        "canonical_case_id": canonical,
                        "canonical_pair_track_id": pair_id,
                        "regular_disorder_pair_id": pair_digest,
                        "regular_disorder_pair_hash_input": pair_input,
                        "track_template": track,
                        "probe": spec["probe"],
                        "polarization": spec["polarization"],
                        "density_amplitude": spec["density_amplitude"],
                        "velocity_amplitude": spec["velocity_amplitude"],
                        "resolution_per_axis": resolution,
                        "dx": dx,
                        "support_over_dx": ratio,
                        "support_h": support,
                        "mode_index": list(mode),
                        "wave_number": k,
                        "kh": kh,
                        "points_per_wavelength": resolution / math.hypot(*mode),
                        "replicate_id": replicate,
                        "phase_radians": phase,
                        "phase_mapping_sha256": phase_records[replicate]["sha256"],
                        "layout_class": layout,
                        "jitter_fraction": jitter_fraction,
                        "paired_jitter_seed": paired_seed,
                        "jitter_seed": actual_seed,
                        "jitter_mapping_sha256": seed_records[replicate]["sha256"],
                        "neighbor_permutation_hash_input": permutation_input,
                        "neighbor_permutation_sha256": permutation_digest,
                        "neighbor_permutation_seed": seed63(permutation_digest),
                        "family_labels": family_labels(track, resolution, ratio, mode),
                        "formal_track_ids": {
                            "REFINEMENT_H": f"REFINEMENT_H|track={track}|layout={layout}",
                            "SPECTRAL_KH": f"SPECTRAL_KH|track={track}|layout={layout}",
                        },
                    })
    canonical_ids = [case["canonical_case_id"] for case in cases]
    if len(cases) != 204 or len(set(canonical_ids)) != 204:
        raise RuntimeError("exact CA-03 registry cardinality or uniqueness failure")
    return {
        "schema_version": "1.0",
        "project": "SPH-DDO-PoC",
        "stage": "DDO-01C-R",
        "registry_status": "FROZEN_BEFORE_TARGET_EVALUATION",
        "generated_date": "2026-08-10",
        "ca03_manifest_path": "06_manifests/ca03_manifest.json",
        "ca03_manifest_sha256": EXPECTED_CA03_SHA256,
        "generation_rule": "Exact CA-03 numeric tables and full-digest domain-separated SHA-256 pool selection",
        "target_outcomes_used": False,
        "historical_sph_target_values_used": False,
        "components": list(COMPONENT_TRACKS),
        "mandatory_component_tracks": COMPONENT_TRACKS,
        "track_templates": TRACKS,
        "replicate_mapping_records": mapping_records,
        "coordinate_tables": {
            "REFINEMENT_H": [{"resolution": n, "dx": 1.0/n, "h": 4.0/n, "h_over_dx": 4.0} for n in (16, 24, 32, 48, 64)],
            "SPECTRAL_KH": [{"mode": list(mode), "kh": 2.0*math.pi*math.hypot(*mode)*0.0625} for mode in ((1, 0), (2, 0), (3, 0))],
            "SUPPORT_RATIO_HDX": [{"h_over_dx": ratio, "h": ratio/64.0, "kh": 2.0*math.pi*ratio/64.0} for ratio in (2.0, 3.0, 4.0, 5.0)],
        },
        "case_count": len(cases),
        "cases": cases,
    }


def main() -> None:
    if REGISTRY_PATH.exists():
        raise RuntimeError("DDO-01C-R registry already exists; refusing replacement")
    if sha256(CA03_PATH) != EXPECTED_CA03_SHA256:
        raise RuntimeError("CA-03 manifest hash mismatch")
    ca03 = json.loads(CA03_PATH.read_text())
    if ca03["terminal_status"] != "DDO_CA03_H2_SCALING_SEMANTICS_AND_DESIGN_FROZEN":
        raise RuntimeError("CA-03 is not frozen")
    registry = build_registry()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "registry_sha256": sha256(REGISTRY_PATH),
        "case_count": registry["case_count"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
