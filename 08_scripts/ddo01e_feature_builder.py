#!/usr/bin/env python3
"""Build the physically isolated observable-only DDO-01E feature cache."""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OBS_INDEX_PATH = ROOT / "data/atlas/ddo01d_observable_atlas.json"
PARTITION_PATH = ROOT / "06_manifests/ddo01e_diagnostic_partition.json"
SAMPLE_PATH = ROOT / "06_manifests/ddo01e_particle_sample_registry.json"
OUT_DIR = ROOT / "data/identifiability"
CACHE_PATH = OUT_DIR / "ddo01e_observable_feature_cache.npz"
SCHEMA_PATH = OUT_DIR / "ddo01e_observable_feature_schema.json"

OBS_INDEX_SHA256 = "99fdf8115e1c2d6280756bcc46edbefc7d52b5f245cc32e308d9100cc4290e53"
PARTITION_SHA256 = "9b2de0b66b28b8912e2563cbf59317cd338904c441a4696768eb9c8d3dec57ce"
SAMPLE_SHA256 = "79daafacbbd3707889bf093a2e679220c6dcbd56e489fd025163e8e4b73bf160"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scalar_blocks(obs: Any) -> tuple[dict[str, np.ndarray], dict[str, list[dict[str, str]]]]:
    covariance = np.asarray(obs["obs__covariance_over_h2"], dtype=np.float64)
    first = np.asarray(obs["obs__first_moment_error"], dtype=np.float64)
    grad_constant = np.asarray(obs["obs__gradient_constant_times_h"], dtype=np.float64)
    blocks: dict[str, list[np.ndarray]] = defaultdict(list)
    specs: dict[str, list[dict[str, str]]] = defaultdict(list)

    def add(layer: str, source: str, transform: str, value: np.ndarray) -> None:
        array = np.asarray(value, dtype=np.float64)
        if array.ndim != 1:
            raise ValueError(f"derived particle scalar is not rank one: {source}/{transform}")
        blocks[layer].append(array)
        specs[layer].append({"name": f"{source}::{transform}", "source_field": source, "transform": transform})

    for source in ("obs__neighbor_count", "obs__neighbor_count_normalized", "obs__support_h_over_L0",
                   "obs__support_over_dx", "obs__covariance_eigenvalue_ratio", "obs__anisotropy",
                   "obs__neighbor_distance_cv", "obs__jitter_fraction"):
        add("G", source, "identity", obs[source])
    add("G", "obs__covariance_over_h2", "trace", np.trace(covariance, axis1=1, axis2=2))
    add("G", "obs__covariance_over_h2", "determinant", np.linalg.det(covariance))
    add("G", "obs__covariance_over_h2", "frobenius", np.linalg.norm(covariance, axis=(1, 2)))
    eigen = np.asarray(obs["obs__covariance_eigenvalues_over_h2"], dtype=np.float64)
    add("G", "obs__covariance_eigenvalues_over_h2", "eigenvalue_0", eigen[:, 0])
    add("G", "obs__covariance_eigenvalues_over_h2", "eigenvalue_1", eigen[:, 1])

    add("C", "obs__zeroth_moment_error", "identity", obs["obs__zeroth_moment_error"])
    add("C", "obs__first_moment_error", "trace", np.trace(first, axis1=1, axis2=2))
    add("C", "obs__first_moment_error", "determinant", np.linalg.det(first))
    add("C", "obs__first_moment_error", "frobenius", np.linalg.norm(first, axis=(1, 2)))
    add("C", "obs__first_moment_error_frobenius", "identity", obs["obs__first_moment_error_frobenius"])
    add("C", "obs__gradient_constant_times_h", "norm", np.linalg.norm(grad_constant, axis=1))
    add("C", "obs__gradient_constant_times_h_norm", "identity", obs["obs__gradient_constant_times_h_norm"])
    add("C", "obs__kernel_volume", "identity", obs["obs__kernel_volume"])
    add("C", "obs__support_count_completeness", "identity", obs["obs__support_count_completeness"])

    for source in ("obs__rho_over_rho0", "obs__delta_rho_over_rho0", "obs__pressure_over_P0",
                   "obs__sph_divergence_normalized", "obs__sph_vorticity_normalized",
                   "obs__strain_trace_normalized", "obs__strain_frobenius_normalized",
                   "obs__strain_determinant_normalized"):
        add("P", source, "identity", obs[source])
    for source in ("obs__pressure_acceleration_over_A0", "obs__viscosity_acceleration_over_A0",
                   "obs__total_acceleration_over_A0"):
        add("P", source, "norm", np.linalg.norm(obs[source], axis=1))

    for source in ("obs__kh_max", "obs__kh_rms", "obs__mode_count", "obs__mach", "obs__reynolds", "obs__eps64"):
        add("N", source, "identity", obs[source])
    return {layer: np.column_stack(values) for layer, values in blocks.items()}, specs


def summarize(values: np.ndarray) -> np.ndarray:
    return np.concatenate((values.mean(axis=0), values.std(axis=0), values.min(axis=0), values.max(axis=0)))


def edge_invariants(obs: Any, start: int, stop: int, layer: str) -> tuple[np.ndarray, list[dict[str, str]]]:
    if layer == "G":
        distance = np.asarray(obs["obs__distance_over_h"][start:stop], dtype=np.float64)
        relative = np.asarray(obs["obs__relative_position_over_h"][start:stop], dtype=np.float64)
        raw = np.column_stack((distance, np.linalg.norm(relative, axis=1)))
        fields = (("obs__distance_over_h", "identity"), ("obs__relative_position_over_h", "norm"))
    elif layer == "P":
        relative = np.asarray(obs["obs__relative_position_over_h"][start:stop], dtype=np.float64)
        delta_v = np.asarray(obs["obs__velocity_difference_over_U0"][start:stop], dtype=np.float64)
        radius = np.linalg.norm(relative, axis=1)
        unit = np.divide(relative, radius[:, None], out=np.zeros_like(relative), where=radius[:, None] > 0)
        norm = np.linalg.norm(delta_v, axis=1)
        radial = np.sum(delta_v * unit, axis=1)
        cross = unit[:, 0] * delta_v[:, 1] - unit[:, 1] * delta_v[:, 0]
        raw = np.column_stack((norm, radial, cross))
        fields = (("obs__velocity_difference_over_U0", "norm"),
                  ("obs__velocity_difference_over_U0", "radial_dot"),
                  ("obs__velocity_difference_over_U0", "cross_pseudoscalar"))
    else:
        return np.empty(0, dtype=np.float64), []
    result = summarize(raw)
    specs = []
    for aggregate in ("mean", "std", "min", "max"):
        for source, transform in fields:
            specs.append({"name": f"{source}::{transform}::edge_{aggregate}", "source_field": source, "transform": f"{transform};edge_{aggregate}"})
    return result, specs


def build_case(obs: Any, particle_ids: list[int]) -> tuple[dict[tuple[str, str], np.ndarray], dict[tuple[str, str], list[dict[str, str]]]]:
    row = np.asarray(obs["edge_row"], dtype=np.int64)
    col = np.asarray(obs["edge_col"], dtype=np.int64)
    particle_count = int(obs["particle_id"].size)
    counts = np.bincount(row, minlength=particle_count)
    indptr = np.concatenate(([0], np.cumsum(counts)))
    base, base_specs = scalar_blocks(obs)
    arrays: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    specs: dict[tuple[str, str], list[dict[str, str]]] = {}
    for layer in ("G", "C", "P", "N"):
        specs[(layer, "I0")] = base_specs[layer]
        node_names = []
        for aggregate in ("mean", "std", "min", "max"):
            for item in base_specs[layer]:
                node_names.append({"name": f"{item['name']}::node_{aggregate}", "source_field": item["source_field"], "transform": f"{item['transform']};node_{aggregate}"})
        edge_spec = edge_invariants(obs, 0, int(counts[0]), layer)[1]
        specs[(layer, "I1")] = node_names + edge_spec
        specs[(layer, "I2")] = [{"name": item["name"].replace("node_", "twohop_"), "source_field": item["source_field"], "transform": item["transform"].replace("node_", "twohop_")} for item in node_names]
        global_specs = [{"name": item["name"].replace("node_", "global_"), "source_field": item["source_field"], "transform": item["transform"].replace("node_", "global_")} for item in node_names]
        if layer == "G":
            global_specs += [
                {"name": "case_metadata::particle_count", "source_field": "particle_id", "transform": "observable_count"},
                {"name": "case_metadata::edges_per_particle", "source_field": "edge_row", "transform": "observable_count_ratio"},
            ]
        specs[(layer, "I3")] = global_specs

    global_summary = {layer: summarize(base[layer]) for layer in base}
    for particle_id in particle_ids:
        start, stop = int(indptr[particle_id]), int(indptr[particle_id + 1])
        onehop = np.unique(col[start:stop])
        second_parts = [onehop]
        for neighbor in onehop:
            second_parts.append(col[indptr[neighbor]:indptr[neighbor + 1]])
        twohop = np.unique(np.concatenate(second_parts))
        for layer in ("G", "C", "P", "N"):
            arrays[(layer, "I0")].append(base[layer][particle_id])
            edge_values, _ = edge_invariants(obs, start, stop, layer)
            arrays[(layer, "I1")].append(np.concatenate((summarize(base[layer][onehop]), edge_values)))
            arrays[(layer, "I2")].append(summarize(base[layer][twohop]))
            extra = global_summary[layer]
            if layer == "G":
                extra = np.concatenate((extra, [particle_count, row.size / particle_count]))
            arrays[(layer, "I3")].append(extra)
    return {key: np.asarray(value, dtype=np.float32) for key, value in arrays.items()}, specs


def main() -> None:
    if CACHE_PATH.exists() or SCHEMA_PATH.exists():
        raise RuntimeError("observable feature cache already exists; refusing replacement")
    for path, expected in ((OBS_INDEX_PATH, OBS_INDEX_SHA256), (PARTITION_PATH, PARTITION_SHA256), (SAMPLE_PATH, SAMPLE_SHA256)):
        if sha256(path) != expected:
            raise RuntimeError(f"frozen target-free binding mismatch: {path}")
    obs_index = json.loads(OBS_INDEX_PATH.read_text())
    partition = json.loads(PARTITION_PATH.read_text())
    samples = json.loads(SAMPLE_PATH.read_text())
    partition_by_id = {case["canonical_case_id"]: case for case in partition["cases"]}
    blocks: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    schema: dict[tuple[str, str], list[dict[str, str]]] = {}
    sample_case_index, sample_particle_id, sample_fold = [], [], []
    sample_family, sample_lineage, sample_key = [], [], []
    for case_number, (obs_entry, sample_entry) in enumerate(zip(obs_index["cases"], samples["cases"], strict=True)):
        case_id = obs_entry["canonical_case_id"]
        if case_id != sample_entry["canonical_case_id"]:
            raise RuntimeError("observable/sample case alignment failure")
        if sha256(ROOT / obs_entry["path"]) != obs_entry["sha256"]:
            raise RuntimeError("observable archive hash failure")
        with np.load(ROOT / obs_entry["path"], allow_pickle=False) as obs:
            if any(name.startswith("target_ref__") for name in obs.files):
                raise RuntimeError("reference field encountered on observable side")
            case_blocks, case_schema = build_case(obs, sample_entry["particle_ids"])
        for key, value in case_blocks.items():
            blocks[key].append(value)
            if key in schema and schema[key] != case_schema[key]:
                raise RuntimeError(f"derived schema drift: {key}")
            schema[key] = case_schema[key]
        meta = partition_by_id[case_id]
        for particle_id in sample_entry["particle_ids"]:
            sample_case_index.append(obs_entry["case_index"])
            sample_particle_id.append(particle_id)
            sample_fold.append(int(meta["diagnostic_fold"].rsplit("_", 1)[1]))
            sample_family.append(meta["macro_family"])
            sample_lineage.append(meta["field_lineage_id"])
            sample_key.append(f"{case_id}|{particle_id}")
        if (case_number + 1) % 32 == 0:
            print(f"observable_case_complete {case_number + 1}/512", flush=True)
    output = {
        "sample_case_index": np.asarray(sample_case_index, dtype=np.int16),
        "sample_particle_id": np.asarray(sample_particle_id, dtype=np.int32),
        "sample_fold": np.asarray(sample_fold, dtype=np.int8),
        "sample_family": np.asarray(sample_family, dtype="U2"),
        "sample_lineage": np.asarray(sample_lineage, dtype="U88"),
        "sample_key": np.asarray(sample_key, dtype="U160"),
    }
    for (layer, increment), values in blocks.items():
        output[f"feature__{layer}__{increment}"] = np.concatenate(values, axis=0)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    temp = CACHE_PATH.with_suffix(".npz.tmp")
    with temp.open("wb") as handle:
        np.savez_compressed(handle, **output)
    os.replace(temp, CACHE_PATH)
    schema_json = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "side": "OBSERVABLE_SIDE_DERIVED_FEATURE_CACHE", "reference_in_model_input": False,
        "source_observable_index_sha256": OBS_INDEX_SHA256,
        "diagnostic_partition_sha256": PARTITION_SHA256, "particle_sample_registry_sha256": SAMPLE_SHA256,
        "sample_count": len(sample_key), "case_count": 512,
        "metric_constant_source_fields_excluded": ["obs__eps64", "obs__mach", "obs__reynolds"],
        "blocks": {
            f"feature__{layer}__{increment}": {
                "layer": layer, "locality_increment": increment,
                "feature_count": len(items), "features": items,
            } for (layer, increment), items in sorted(schema.items())
        },
        "controls": {"reference_archives_opened": False, "target_fields_used": False, "target_derived_standardization": False},
    }
    SCHEMA_PATH.write_text(json.dumps(schema_json, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "cache_sha256": sha256(CACHE_PATH), "schema_sha256": sha256(SCHEMA_PATH),
        "sample_count": len(sample_key), "feature_block_count": len(blocks),
        "maximum_nested_feature_count": sum(len(items) for items in schema.values()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
