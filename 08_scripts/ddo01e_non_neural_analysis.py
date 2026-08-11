#!/usr/bin/env python3
"""Execute the CA-05-frozen non-neural DDO-01E H3/H4 diagnostics."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree
from sklearn.preprocessing import PolynomialFeatures


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))
from h3_identifiability_semantics import h3_gate, project_status  # noqa: E402
from h4_locality_semantics import locality_verdict  # noqa: E402


DATA_DIR = ROOT / "data/identifiability"
FEATURE_PATH = DATA_DIR / "ddo01e_observable_feature_cache.npz"
FEATURE_SCHEMA_PATH = DATA_DIR / "ddo01e_observable_feature_schema.json"
TARGET_PATH = DATA_DIR / "ddo01e_reference_target_cache.npz"
TARGET_SCHEMA_PATH = DATA_DIR / "ddo01e_reference_target_schema.json"
PARTITION_PATH = ROOT / "06_manifests/ddo01e_diagnostic_partition.json"
SAMPLE_PATH = ROOT / "06_manifests/ddo01e_particle_sample_registry.json"
REF_INDEX_PATH = ROOT / "data/atlas/ddo01d_reference_target_atlas.json"
META_PATH = ROOT / "data/atlas/ddo01d_case_metadata.json"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
METRICS_PATH = DATA_DIR / "ddo01e_metrics.json"
DIAGNOSTICS_JSON_PATH = DATA_DIR / "ddo01e_non_neural_diagnostics.json"
DIAGNOSTICS_CSV_PATH = DATA_DIR / "ddo01e_non_neural_diagnostics.csv"
VERDICTS_PATH = DATA_DIR / "ddo01e_formal_verdicts.json"
LEDGER_PATH = ROOT / "07_reports/ddo01e_component_h3_h4_ledger.csv"

FEATURE_SHA256 = "ea5e9c4a1e036ec8f9b1634501e06b90191ed088d81ec618df2582a2068ee6e9"
FEATURE_SCHEMA_SHA256 = "2edda19ce9424efe548005850f4bbb74800685d8ea2fd7a730421e35ceaddce8"
PARTITION_SHA256 = "9b2de0b66b28b8912e2563cbf59317cd338904c441a4696768eb9c8d3dec57ce"
SAMPLE_SHA256 = "79daafacbbd3707889bf093a2e679220c6dcbd56e489fd025163e8e4b73bf160"
REF_INDEX_SHA256 = "c7e7608b269d6f1c3661e3fffb8c5ced430f2a8dc8b3432666fc745d0de483bc"
META_SHA256 = "b79a8f157f1094243397bf04a902907fa20d3205531d3034b40daf2ab94b1c6c"

LAYERS = {"C0": ("G",), "C1": ("G", "C"), "C2": ("G", "C", "P"), "C3": ("G", "C", "P", "N")}
LOCALITIES = ("L0", "L1", "L2", "L3")
COMPONENTS = (
    "density_rate", "pressure_gradient_acceleration",
    "viscosity_laplacian_acceleration", "interpolation_density",
)
ALL_REPORTED_COMPONENTS = COMPONENTS + ("total_acceleration",)
TARGET_FIELDS = {
    "density_rate": "target_ref__defect_density_rate",
    "pressure_gradient_acceleration": "target_ref__defect_pressure_acceleration",
    "viscosity_laplacian_acceleration": "target_ref__defect_viscosity_acceleration",
    "interpolation_density": "target_ref__defect_interpolation_density",
    "total_acceleration": "target_ref__defect_total_acceleration",
}
COMPONENT_SCALES = {
    "density_rate": 0.1, "pressure_gradient_acceleration": 0.01,
    "viscosity_laplacian_acceleration": 0.01, "interpolation_density": 1.0,
    "total_acceleration": 0.01,
}
CONSTANT_SOURCES = {"obs__eps64", "obs__mach", "obs__reynolds"}
POLYNOMIAL_SOURCES = {
    "obs__neighbor_count_normalized", "obs__anisotropy", "obs__zeroth_moment_error",
    "obs__first_moment_error_frobenius", "obs__gradient_constant_times_h_norm",
    "obs__delta_rho_over_rho0", "obs__sph_divergence_normalized", "obs__kh_rms",
}
ORACLES = ("knn5", "knn10", "knn20", "ridge", "polynomial_ridge")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_int(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest(), "big")


def atomic_json(path: Path, value: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temp, path)


def norm_sq(value: np.ndarray) -> np.ndarray:
    return value * value if value.ndim == 1 else np.sum(value * value, axis=1)


def row_norm(value: np.ndarray) -> np.ndarray:
    return np.abs(value) if value.ndim == 1 else np.linalg.norm(value, axis=1)


def build_target_cache() -> None:
    if TARGET_PATH.exists() and TARGET_SCHEMA_PATH.exists():
        return
    if TARGET_PATH.exists() or TARGET_SCHEMA_PATH.exists():
        raise RuntimeError("partial target cache exists")
    for path, expected in ((FEATURE_PATH, FEATURE_SHA256), (FEATURE_SCHEMA_PATH, FEATURE_SCHEMA_SHA256),
                           (PARTITION_PATH, PARTITION_SHA256), (SAMPLE_PATH, SAMPLE_SHA256),
                           (REF_INDEX_PATH, REF_INDEX_SHA256), (META_PATH, META_SHA256)):
        if sha256(path) != expected:
            raise RuntimeError(f"frozen binding mismatch: {path}")
    samples = json.loads(SAMPLE_PATH.read_text())
    ref_index = json.loads(REF_INDEX_PATH.read_text())
    metadata = json.loads(META_PATH.read_text())
    with np.load(FEATURE_PATH, allow_pickle=False) as feature:
        feature_keys = np.asarray(feature["sample_key"])
    targets: dict[str, list[np.ndarray]] = defaultdict(list)
    target_keys, uncertainty = [], defaultdict(list)
    for index, (ref_entry, sample_entry, meta) in enumerate(zip(ref_index["cases"], samples["cases"], metadata["cases"], strict=True)):
        case_id = ref_entry["canonical_case_id"]
        if case_id != sample_entry["canonical_case_id"] or case_id != meta["canonical_case_id"]:
            raise RuntimeError("reference/sample/metadata case mismatch")
        ref_path = ROOT / ref_entry["path"]
        if sha256(ref_path) != ref_entry["sha256"]:
            raise RuntimeError("reference archive hash mismatch")
        ids = np.asarray(sample_entry["particle_ids"], dtype=np.int64)
        with np.load(ref_path, allow_pickle=False) as ref:
            if any(name.startswith("obs__") for name in ref.files):
                raise RuntimeError("observable field encountered in reference archive")
            for component, field in TARGET_FIELDS.items():
                targets[component].append(np.asarray(ref[field][ids], dtype=np.float64))
        for particle_id in ids:
            target_keys.append(f"{case_id}|{int(particle_id)}")
        for component in ALL_REPORTED_COMPONENTS:
            uncertainty[component].append(float(meta["components"][component]["U_num"]))
        if (index + 1) % 64 == 0:
            print(f"reference_case_complete {index + 1}/512", flush=True)
    if not np.array_equal(feature_keys, np.asarray(target_keys, dtype=feature_keys.dtype)):
        raise RuntimeError("observable/reference formal sample alignment failure")
    output = {f"target__{name}": np.concatenate(values, axis=0) for name, values in targets.items()}
    output["sample_key"] = feature_keys
    for component, values in uncertainty.items():
        output[f"case_uncertainty__{component}"] = np.asarray(values, dtype=np.float64)
    temp = TARGET_PATH.with_suffix(".npz.tmp")
    with temp.open("wb") as handle:
        np.savez_compressed(handle, **output)
    os.replace(temp, TARGET_PATH)
    schema = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "side": "REFERENCE_TARGET_SIDE_FORMAL_SAMPLE", "eligible_as_model_input": False,
        "source_reference_index_sha256": REF_INDEX_SHA256, "sample_registry_sha256": SAMPLE_SHA256,
        "observable_feature_cache_sha256_for_key_alignment_only": FEATURE_SHA256,
        "sample_count": len(target_keys),
        "fields": {f"target__{name}": {"source_field": TARGET_FIELDS[name], "role": "formal_target" if name in COMPONENTS[:3] else "diagnostic_target"} for name in TARGET_FIELDS},
        "controls": {"target_fields_enter_observable_cache": False, "target_fields_enter_feature_standardization": False},
    }
    TARGET_SCHEMA_PATH.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"target_cache_sha256": sha256(TARGET_PATH), "target_schema_sha256": sha256(TARGET_SCHEMA_PATH)}, sort_keys=True), flush=True)


def feature_matrix(feature: Any, schema: dict[str, Any], content: str, locality: str) -> tuple[np.ndarray, list[dict[str, str]]]:
    max_increment = int(locality[1])
    arrays, specs = [], []
    for layer in LAYERS[content]:
        for increment in range(max_increment + 1):
            key = f"feature__{layer}__I{increment}"
            block_specs = schema["blocks"][key]["features"]
            keep = [i for i, item in enumerate(block_specs) if item["source_field"] not in CONSTANT_SOURCES]
            arrays.append(np.asarray(feature[key][:, keep], dtype=np.float64))
            specs.extend([{**block_specs[i], "block": key} for i in keep])
    return np.concatenate(arrays, axis=1), specs


def fit_scaler(train: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    median = np.median(train, axis=0)
    q25 = np.quantile(train, 0.25, axis=0, method="inverted_cdf")
    q75 = np.quantile(train, 0.75, axis=0, method="inverted_cdf")
    iqr = q75 - q25
    retain = np.isfinite(median) & np.isfinite(iqr) & (iqr > 0)
    if not retain.any():
        raise RuntimeError("training fold has no retained metric channel")
    return median, iqr, retain


def nearest_different_lineage(tree: cKDTree, train: np.ndarray, lineages: np.ndarray, dimension: int) -> np.ndarray:
    result = np.full(train.shape[0], np.inf)
    for lineage in np.unique(lineages):
        query_rows = np.flatnonzero(lineages == lineage)
        if query_rows.size > 256:
            permitted_rows = np.flatnonzero(lineages != lineage)
            permitted_tree = cKDTree(train[permitted_rows], compact_nodes=True, balanced_tree=True)
            distances, _ = permitted_tree.query(train[query_rows], k=1, eps=0, p=2, workers=1)
            result[query_rows] = distances / math.sqrt(dimension)
            continue
        # At most n candidates share the query lineage (including self), so the
        # first n+1 exact neighbors necessarily contain the nearest permitted one.
        use_k = min(query_rows.size + 1, train.shape[0])
        distances, indices = tree.query(train[query_rows], k=use_k, eps=0, p=2, workers=1)
        if use_k == 1:
            distances, indices = distances[:, None], indices[:, None]
        for local_row, global_row in enumerate(query_rows):
            valid = lineages[indices[local_row]] != lineage
            where = np.flatnonzero(valid)
            if where.size:
                result[global_row] = distances[local_row, where[0]] / math.sqrt(dimension)
    if not np.isfinite(result).all():
        raise RuntimeError("could not find different-lineage training neighbor")
    return result


def ridge_predict(train_x: np.ndarray, train_y: np.ndarray, query_x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    if train_y.ndim == 1:
        train_y = train_y[:, None]
    x_mean, y_mean = train_x.mean(axis=0), train_y.mean(axis=0)
    xc, yc = train_x - x_mean, train_y - y_mean
    gram = xc.T @ xc
    gram.flat[::gram.shape[0] + 1] += alpha
    beta = np.linalg.solve(gram, xc.T @ yc)
    result = (query_x - x_mean) @ beta + y_mean
    return result


def case_row(component: str, case_index: int, qmask: np.ndarray, target: np.ndarray,
             cvars: dict[int, np.ndarray], dnn: np.ndarray, coverage: np.ndarray,
             sign: np.ndarray, predictions: dict[str, np.ndarray], baseline: np.ndarray,
             family: str, layout: str, lineage: str, fold: int, uncertainty: float) -> dict[str, Any]:
    y = target[qmask]
    row = {
        "component": component, "case_index": case_index, "family": family, "layout": layout,
        "lineage": lineage, "fold": fold, "particle_count": int(qmask.sum()),
        "dnn_median": float(np.median(dnn[qmask])), "dnn_p90": float(np.quantile(dnn[qmask], .9, method="inverted_cdf")),
        "cvar5": float(np.mean(cvars[5][qmask])), "cvar10": float(np.mean(cvars[10][qmask])),
        "cvar20": float(np.mean(cvars[20][qmask])), "coverage": float(np.mean(coverage[qmask])),
        "sign_disagreement": float(np.mean(sign[qmask])), "target_ms": float(np.mean(norm_sq(y))),
        "uncertainty": uncertainty,
    }
    base_error = baseline[qmask] - y
    row["baseline_error_ms"] = float(np.mean(norm_sq(base_error)))
    for oracle, pred in predictions.items():
        error = pred[qmask] - y
        row[f"{oracle}_error_ms"] = float(np.mean(norm_sq(error)))
        row[f"{oracle}_mae"] = float(np.mean(row_norm(error)))
        row[f"{oracle}_bias"] = float(np.mean(error)) if error.ndim == 1 else float(np.linalg.norm(error.mean(axis=0)))
        if y.ndim == 2:
            floor = max(10.0 * uncertainty, 1.0e-6 * COMPONENT_SCALES[component])
            active = np.linalg.norm(y, axis=1) > floor
            if active.any():
                denom = np.linalg.norm(y[active], axis=1) * np.linalg.norm(pred[qmask][active], axis=1)
                valid = denom > 0
                cosine = np.clip(np.sum(y[active][valid] * pred[qmask][active][valid], axis=1) / denom[valid], -1, 1)
                row[f"{oracle}_angle_degrees"] = float(np.degrees(np.arccos(cosine)).mean()) if cosine.size else None
            else:
                row[f"{oracle}_angle_degrees"] = None
    return row


def fold_case_nrmse(rows: list[dict[str, Any]], oracle: str) -> float:
    target_energy = float(np.mean([row["target_ms"] for row in rows]))
    if target_energy <= 0:
        return math.nan
    return math.sqrt(np.mean([row[f"{oracle}_error_ms"] for row in rows]) / target_energy)


def fold_baseline_nrmse(rows: list[dict[str, Any]]) -> float:
    return math.sqrt(np.mean([row["baseline_error_ms"] for row in rows]) / np.mean([row["target_ms"] for row in rows]))


def aggregate_case_stat(rows: list[dict[str, Any]], field: str, reducer: str = "mean") -> float:
    by_fold = defaultdict(list)
    for row in rows:
        by_fold[row["fold"]].append(row[field])
    values = []
    for fold_rows in by_fold.values():
        if reducer == "median": values.append(float(np.median(fold_rows)))
        elif reducer == "p90": values.append(float(np.quantile(fold_rows, .9, method="inverted_cdf")))
        else: values.append(float(np.mean(fold_rows)))
    return float(np.mean(values))


def bootstrap_stat(rows: list[dict[str, Any]], value_field: str, seed_text: str, replicates: int = 2000) -> np.ndarray:
    strata = defaultdict(lambda: defaultdict(list))
    for row in rows:
        strata[(row["fold"], row["family"])][row["lineage"]].append(row)
    rng = np.random.Generator(np.random.PCG64(digest_int(seed_text)))
    output = np.empty(replicates)
    for replicate in range(replicates):
        selected_by_fold = defaultdict(list)
        for (fold, _family), lineage_rows in strata.items():
            lineage_ids = sorted(lineage_rows)
            chosen = rng.choice(lineage_ids, size=len(lineage_ids), replace=True)
            for lineage in chosen:
                selected_by_fold[fold].extend(lineage_rows[str(lineage)])
        output[replicate] = np.mean([np.mean([row[value_field] for row in values]) for values in selected_by_fold.values()])
    return output


def summarize_combination(rows: list[dict[str, Any]], component: str, content: str, locality: str) -> dict[str, Any]:
    component_rows = [row for row in rows if row["component"] == component]
    oracle_metrics = {}
    for oracle in ORACLES:
        fold_values, family_values = [], defaultdict(list)
        for fold in range(5):
            fold_rows = [row for row in component_rows if row["fold"] == fold]
            fold_values.append(fold_case_nrmse(fold_rows, oracle))
            for family in ("F1", "F2", "F3", "F4"):
                family_rows = [row for row in fold_rows if row["family"] == family]
                family_value = fold_case_nrmse(family_rows, oracle)
                if np.isfinite(family_value):
                    family_values[family].append(family_value)
        baseline = np.mean([fold_baseline_nrmse([row for row in component_rows if row["fold"] == fold]) for fold in range(5)])
        nrmse = float(np.mean(fold_values))
        oracle_metrics[oracle] = {
            "nrmse": nrmse, "baseline_nrmse": float(baseline),
            "baseline_improvement": float(1.0 - nrmse / baseline),
            "family_nrmse": {family: float(np.mean(family_values[family])) if family_values[family] else math.nan for family in ("F1", "F2", "F3", "F4")},
            "mae": aggregate_case_stat(component_rows, f"{oracle}_mae"),
            "bias": aggregate_case_stat(component_rows, f"{oracle}_bias"),
        }
    best = min(ORACLES, key=lambda name: (oracle_metrics[name]["nrmse"], name))
    cvar_boot = bootstrap_stat(component_rows, "cvar10", f"DDO01E|BOOTSTRAP|{component}|{content}|{locality}|cvar10")
    result = {
        "component": component, "content": content, "locality": locality,
        "dnn_median": aggregate_case_stat(component_rows, "dnn_median", "median"),
        "dnn_p90": aggregate_case_stat(component_rows, "dnn_p90", "p90"),
        "cvar": aggregate_case_stat(component_rows, "cvar10"),
        "cvar5_sensitivity": aggregate_case_stat(component_rows, "cvar5"),
        "cvar20_sensitivity": aggregate_case_stat(component_rows, "cvar20"),
        "cvar_lower95": float(np.quantile(cvar_boot, .025, method="inverted_cdf")),
        "cvar_upper95": float(np.quantile(cvar_boot, .975, method="inverted_cdf")),
        "coverage": aggregate_case_stat(component_rows, "coverage"),
        "sign_disagreement": aggregate_case_stat(component_rows, "sign_disagreement"),
        "oracles": oracle_metrics, "best_oracle": best,
        "oracle_nrmse": oracle_metrics[best]["nrmse"],
        "baseline_improvement": oracle_metrics[best]["baseline_improvement"],
        "max_family_nrmse": max(oracle_metrics[best]["family_nrmse"].values()),
        "execution_complete": True,
    }
    result["h3_status"] = h3_gate(result)
    return result


def paired_degradation(rows_by_locality: dict[str, list[dict[str, Any]]], summaries: dict[str, dict[str, Any]],
                       component: str, narrow: str, broad: str, replicates: int = 2000) -> dict[str, float]:
    narrow_oracle = summaries[narrow]["best_oracle"]
    broad_oracle = summaries[broad]["best_oracle"]
    narrow_rows = {row["case_index"]: row for row in rows_by_locality[narrow] if row["component"] == component}
    broad_rows = {row["case_index"]: row for row in rows_by_locality[broad] if row["component"] == component}
    case_ids = sorted(set(narrow_rows) & set(broad_rows))
    template = []
    for case in case_ids:
        a, b = narrow_rows[case], broad_rows[case]
        template.append({
            "case_index": case, "fold": a["fold"], "family": a["family"], "lineage": a["lineage"],
            "target_ms": a["target_ms"], "narrow_error": a[f"{narrow_oracle}_error_ms"],
            "broad_error": b[f"{broad_oracle}_error_ms"], "narrow_cvar": a["cvar10"], "broad_cvar": b["cvar10"],
        })
    strata = defaultdict(lambda: defaultdict(list))
    for row in template:
        strata[(row["fold"], row["family"])][row["lineage"]].append(row)
    rng = np.random.Generator(np.random.PCG64(digest_int(f"DDO01E|BOOTSTRAP|{component}|C3|{narrow}|versus|{broad}|paired")))
    delta_e, delta_c = np.empty(replicates), np.empty(replicates)
    for rep in range(replicates):
        by_fold = defaultdict(list)
        for (fold, _family), lineage_rows in strata.items():
            ids = sorted(lineage_rows)
            for lineage in rng.choice(ids, size=len(ids), replace=True):
                by_fold[fold].extend(lineage_rows[str(lineage)])
        en, eb, cvn, cvb = [], [], [], []
        for values in by_fold.values():
            t = np.mean([row["target_ms"] for row in values])
            en.append(math.sqrt(np.mean([row["narrow_error"] for row in values]) / t))
            eb.append(math.sqrt(np.mean([row["broad_error"] for row in values]) / t))
            cvn.append(np.mean([row["narrow_cvar"] for row in values]))
            cvb.append(np.mean([row["broad_cvar"] for row in values]))
        enm, ebm = np.mean(en), np.mean(eb)
        delta_e[rep] = (enm - ebm) / ebm if ebm > 0 else math.inf
        delta_c[rep] = np.mean(cvn) - np.mean(cvb)
    return {
        "relative_nrmse_upper95": float(np.quantile(delta_e, .95, method="inverted_cdf")),
        "cvar_difference_upper95": float(np.quantile(delta_c, .95, method="inverted_cdf")),
    }


def run_fold(content: str, locality: str, fold: int, x_all: np.ndarray, specs: list[dict[str, str]],
             feature: dict[str, np.ndarray], target: dict[str, np.ndarray],
             partition_cases: dict[int, dict[str, Any]], metadata: dict[int, dict[str, Any]]) -> dict[str, Any]:
    checkpoint = CHECKPOINT_DIR / f"{content}_{locality}_fold{fold}.json"
    if checkpoint.exists():
        return json.loads(checkpoint.read_text())
    folds = feature["sample_fold"]
    train_global = np.flatnonzero(folds != fold)
    query_global = np.flatnonzero(folds == fold)
    train_order = np.argsort(
        np.asarray([hashlib.sha256(value.encode()).hexdigest() for value in feature["sample_key"][train_global]]),
        kind="stable",
    )
    train_global = train_global[train_order]
    median, iqr, retain = fit_scaler(x_all[train_global])
    train_x = (x_all[train_global][:, retain] - median[retain]) / iqr[retain]
    query_x = (x_all[query_global][:, retain] - median[retain]) / iqr[retain]
    dimension = int(retain.sum())
    tree = cKDTree(train_x, compact_nodes=True, balanced_tree=True)
    distances, neighbor_local = tree.query(query_x, k=20, eps=0, p=2, workers=1)
    distances = distances / math.sqrt(dimension)
    train_lineages = feature["sample_lineage"][train_global]
    radius_values = nearest_different_lineage(tree, train_x, train_lineages, dimension)
    radius = float(np.quantile(radius_values, .95, method="inverted_cdf"))
    coverage = distances[:, 0] <= radius
    neighbor_global = train_global[neighbor_local]

    query_tree = cKDTree(query_x, compact_nodes=True, balanced_tree=True)
    used_train_positions = np.unique(neighbor_local[:, :10])
    _, reverse_used = query_tree.query(train_x[used_train_positions], k=10, eps=0, p=2, workers=1)
    reverse_query = {int(position): reverse_used[index] for index, position in enumerate(used_train_positions)}
    reciprocal_hits = 0
    for query_local in range(query_global.size):
        reciprocal_hits += sum(query_local in reverse_query[train_position] for train_position in neighbor_local[query_local, :10])
    reciprocal_fraction = reciprocal_hits / (query_global.size * 10)

    baseline_local = np.empty((query_global.size, 10), dtype=np.int64)
    for i, global_index in enumerate(query_global):
        rng = np.random.Generator(np.random.PCG64(digest_int(f"DDO01E|BASELINE|{feature['sample_key'][global_index]}")))
        baseline_local[i] = rng.choice(train_global.size, size=10, replace=False)
    predictions_by_component: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    target_query, target_train = {}, {}
    for component in COMPONENTS:
        values = target[f"target__{component}"]
        target_query[component], target_train[component] = values[query_global], values[train_global]
        for k in (5, 10, 20):
            predictions_by_component[component][f"knn{k}"] = values[neighbor_global[:, :k]].mean(axis=1)
    train_bundle = np.column_stack([
        target_train["density_rate"], target_train["pressure_gradient_acceleration"],
        target_train["viscosity_laplacian_acceleration"], target_train["interpolation_density"],
    ])
    ridge_bundle = ridge_predict(train_x, train_bundle, query_x)
    slices = {"density_rate": slice(0, 1), "pressure_gradient_acceleration": slice(1, 3),
              "viscosity_laplacian_acceleration": slice(3, 5), "interpolation_density": slice(5, 6)}
    for component, slc in slices.items():
        value = ridge_bundle[:, slc]
        predictions_by_component[component]["ridge"] = value[:, 0] if value.shape[1] == 1 else value

    poly_columns = [i for i, (item, keep) in enumerate(zip(specs, retain))
                    if keep and item["block"].endswith("__I0") and item["source_field"] in POLYNOMIAL_SOURCES]
    retained_original = np.flatnonzero(retain)
    retained_lookup = {original: position for position, original in enumerate(retained_original)}
    poly_positions = [retained_lookup[i] for i in poly_columns]
    polynomial = PolynomialFeatures(degree=2, include_bias=False)
    poly_train = polynomial.fit_transform(train_x[:, poly_positions])
    poly_query = polynomial.transform(query_x[:, poly_positions])
    poly_bundle = ridge_predict(poly_train, train_bundle, poly_query)
    for component, slc in slices.items():
        value = poly_bundle[:, slc]
        predictions_by_component[component]["polynomial_ridge"] = value[:, 0] if value.shape[1] == 1 else value

    rows = []
    query_case = feature["sample_case_index"][query_global]
    query_family = feature["sample_family"][query_global]
    query_lineage = feature["sample_lineage"][query_global]
    neighbor_family_composition = Counter(feature["sample_family"][neighbor_global[:, :10]].ravel().tolist())
    for component in COMPONENTS:
        yq, yt = target_query[component], target_train[component]
        neighbor_target = target[f"target__{component}"][neighbor_global]
        baseline_target = yt[baseline_local]
        diff_nn = neighbor_target[:, :10] - yq[:, None] if yq.ndim == 1 else neighbor_target[:, :10] - yq[:, None, :]
        diff_baseline = baseline_target - yq[:, None] if yq.ndim == 1 else baseline_target - yq[:, None, :]
        numerator = np.mean(norm_sq(diff_nn.reshape(-1, *diff_nn.shape[2:])).reshape(query_global.size, 10), axis=1)
        denominator = np.mean(norm_sq(diff_baseline.reshape(-1, *diff_baseline.shape[2:])).reshape(query_global.size, 10), axis=1)
        dnn = np.divide(numerator, denominator, out=np.full_like(numerator, np.inf), where=denominator > 0)
        zero_zero = (numerator == 0) & (denominator == 0)
        dnn[zero_zero] = np.nan
        if not np.isfinite(dnn).all():
            finite = dnn[np.isfinite(dnn)]
            dnn = np.nan_to_num(dnn, nan=float(np.max(finite)) if finite.size else math.inf, posinf=float(np.max(finite)) if finite.size else math.inf)
        unconditional = float(np.var(yt, ddof=1)) if yt.ndim == 1 else float(np.var(yt, axis=0, ddof=1).sum())
        cvars = {}
        for k in (5, 10, 20):
            local = neighbor_target[:, :k]
            centered = local - local.mean(axis=1, keepdims=True)
            local_trace = np.sum(centered * centered, axis=1) / (k - 1) if local.ndim == 2 else np.sum(centered * centered, axis=(1, 2)) / (k - 1)
            cvars[k] = local_trace / unconditional
        if yq.ndim == 1:
            sign = np.mean(np.sign(yq)[:, None] * np.sign(neighbor_target[:, :10]) < 0, axis=1)
        else:
            sign = np.mean(np.sum(yq[:, None, :] * neighbor_target[:, :10], axis=2) < 0, axis=1)
        baseline_prediction = np.full_like(yq, yt.mean()) if yq.ndim == 1 else np.broadcast_to(yt.mean(axis=0), yq.shape).copy()
        for case_index in np.unique(query_case):
            mask = query_case == case_index
            meta = metadata[int(case_index)]
            rows.append(case_row(
                component, int(case_index), mask, yq, cvars, dnn, coverage, sign,
                predictions_by_component[component], baseline_prediction,
                str(query_family[mask][0]), meta["layout_class"], str(query_lineage[mask][0]), fold,
                float(meta["components"][component]["U_num"]),
            ))

    # Derived total is formed only from pressure plus viscosity predictions.
    component = "total_acceleration"
    yq = target["target__total_acceleration"][query_global]
    yt = target["target__total_acceleration"][train_global]
    neighbor_target = target["target__total_acceleration"][neighbor_global]
    baseline_target = yt[baseline_local]
    diff_nn, diff_baseline = neighbor_target[:, :10] - yq[:, None, :], baseline_target - yq[:, None, :]
    numerator = np.mean(np.sum(diff_nn * diff_nn, axis=2), axis=1)
    denominator = np.mean(np.sum(diff_baseline * diff_baseline, axis=2), axis=1)
    dnn = np.divide(numerator, denominator, out=np.full_like(numerator, np.inf), where=denominator > 0)
    finite = dnn[np.isfinite(dnn)]
    dnn = np.nan_to_num(dnn, nan=float(np.max(finite)) if finite.size else math.inf, posinf=float(np.max(finite)) if finite.size else math.inf)
    unconditional = float(np.var(yt, axis=0, ddof=1).sum())
    cvars = {}
    for k in (5, 10, 20):
        local = neighbor_target[:, :k]
        centered = local - local.mean(axis=1, keepdims=True)
        cvars[k] = np.sum(centered * centered, axis=(1, 2)) / (k - 1) / unconditional
    sign = np.mean(np.sum(yq[:, None, :] * neighbor_target[:, :10], axis=2) < 0, axis=1)
    total_predictions = {oracle: predictions_by_component["pressure_gradient_acceleration"][oracle] + predictions_by_component["viscosity_laplacian_acceleration"][oracle] for oracle in ORACLES}
    baseline_prediction = np.broadcast_to(yt.mean(axis=0), yq.shape).copy()
    for case_index in np.unique(query_case):
        mask = query_case == case_index
        meta = metadata[int(case_index)]
        rows.append(case_row(component, int(case_index), mask, yq, cvars, dnn, coverage, sign,
                             total_predictions, baseline_prediction, str(query_family[mask][0]),
                             meta["layout_class"], str(query_lineage[mask][0]), fold,
                             float(meta["components"][component]["U_num"])))
    result = {
        "content": content, "locality": locality, "fold": fold,
        "training_sample_count": int(train_global.size), "query_sample_count": int(query_global.size),
        "raw_feature_count": int(x_all.shape[1]), "retained_feature_count": dimension,
        "zero_iqr_excluded_count": int((~retain).sum()),
        "zero_iqr_excluded_features": [specs[i]["name"] for i in np.flatnonzero(~retain)],
        "coverage_radius": radius, "reciprocal_neighbor_fraction": reciprocal_fraction,
        "neighbor_family_composition": dict(sorted(neighbor_family_composition.items())),
        "case_rows": rows,
    }
    atomic_json(checkpoint, result)
    return result


def main() -> None:
    if any(path.exists() for path in (METRICS_PATH, DIAGNOSTICS_JSON_PATH, DIAGNOSTICS_CSV_PATH, VERDICTS_PATH, LEDGER_PATH)):
        raise RuntimeError("final DDO-01E formal outputs already exist; refusing replacement")
    build_target_cache()
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    feature_schema = json.loads(FEATURE_SCHEMA_PATH.read_text())
    partition = json.loads(PARTITION_PATH.read_text())
    metadata_json = json.loads(META_PATH.read_text())
    partition_cases = {case["case_index"]: case for case in partition["cases"]}
    metadata = {case["case_index"]: case for case in metadata_json["cases"]}
    with np.load(FEATURE_PATH, allow_pickle=False) as feature, np.load(TARGET_PATH, allow_pickle=False) as target:
        feature_meta = {key: np.asarray(feature[key]) for key in (
            "sample_case_index", "sample_particle_id", "sample_fold", "sample_family",
            "sample_lineage", "sample_key",
        )}
        target_arrays = {key: np.asarray(target[key]) for key in target.files}
        all_results, all_case_rows = {}, []
        rows_by_combo = {}
        for content in ("C0", "C1", "C2", "C3"):
            for locality in LOCALITIES:
                combo = f"{content}/{locality}"
                x_all, specs = feature_matrix(feature, feature_schema, content, locality)
                fold_results = []
                for fold in range(5):
                    result = run_fold(content, locality, fold, x_all, specs, feature_meta, target_arrays, partition_cases, metadata)
                    fold_results.append(result)
                    print(f"diagnostic_complete {content} {locality} fold={fold}", flush=True)
                combo_rows = [row for result in fold_results for row in result["case_rows"]]
                rows_by_combo[combo] = combo_rows
                all_case_rows.extend([{**row, "content": content, "locality": locality} for row in combo_rows])
                all_results[combo] = {
                    "feature_qc": [{key: value for key, value in result.items() if key != "case_rows"} for result in fold_results],
                    "components": {component: summarize_combination(combo_rows, component, content, locality) for component in ALL_REPORTED_COMPONENTS},
                }
        formal_h3 = {component: all_results["C3/L3"]["components"][component]["h3_status"] for component in COMPONENTS}
        h4 = {}
        h4_evidence = {}
        for component in COMPONENTS:
            summaries = {locality: all_results[f"C3/{locality}"]["components"][component] for locality in LOCALITIES}
            evidence = {}
            for i, locality in enumerate(LOCALITIES):
                evidence[locality] = {"h3_status": summaries[locality]["h3_status"], "paired_degradation": {}}
                for broad in LOCALITIES[i + 1:]:
                    evidence[locality]["paired_degradation"][broad] = paired_degradation(
                        {name: rows_by_combo[f"C3/{name}"] for name in LOCALITIES}, summaries, component, locality, broad
                    )
            h4_evidence[component] = evidence
            h4[component] = locality_verdict(formal_h3[component], evidence)
        primary_h3 = {name: formal_h3[name] for name in COMPONENTS[:3]}
        primary_h4 = {name: h4[name]["status"] for name in COMPONENTS[:3]}
        terminal = project_status(primary_h3, primary_h4)
        metrics = {
            "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
            "generated_date": "2026-08-11", "formal_sample_count": 65536,
            "combination_count": 16, "results": all_results,
            "formal_h3_combination": "C3/L3", "formal_h3": formal_h3,
            "formal_h4_content": "C3", "formal_h4": h4, "h4_paired_evidence": h4_evidence,
            "terminal_status": terminal,
            "controls": {"neural_training": False, "target_svd_pca_performed_before_verdict_freeze": False},
        }
        atomic_json(METRICS_PATH, metrics)
        diagnostics = {
            "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
            "metric_file_sha256": sha256(METRICS_PATH),
            "oracle_classes": list(ORACLES), "case_row_count": len(all_case_rows),
            "case_diagnostics_csv": str(DIAGNOSTICS_CSV_PATH.relative_to(ROOT)),
            "component_roles": {"total_acceleration": "DERIVED_CLOSURE_DIAGNOSTIC_PREDICTION_EQUALS_PRESSURE_PLUS_VISCOSITY", "interpolation_density": "ALGEBRAIC_DENSITY_DIAGNOSTIC"},
            "controls": {"production_model_claim": False, "architecture_selection": False, "neural_training": False},
        }
        atomic_json(DIAGNOSTICS_JSON_PATH, diagnostics)
        fieldnames = sorted({key for row in all_case_rows for key in row})
        with DIAGNOSTICS_CSV_PATH.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader(); writer.writerows(all_case_rows)
        verdicts = {
            "schema_version": "1.0", "stage": "DDO-01E", "generated_date": "2026-08-11",
            "metrics_sha256": sha256(METRICS_PATH), "formal_h3": formal_h3, "formal_h4": h4,
            "terminal_status": terminal, "verdicts_frozen_before_target_subspace_diagnostic": True,
        }
        atomic_json(VERDICTS_PATH, verdicts)
        with LEDGER_PATH.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=("component", "role", "formal_combination", "h3_status", "h4_selected_rung", "h4_status"))
            writer.writeheader()
            for component in ALL_REPORTED_COMPONENTS:
                role = metadata[0]["components"][component]["role"]
                if component == "total_acceleration":
                    writer.writerow({"component": component, "role": role, "formal_combination": "derived only", "h3_status": "DERIVED_CLOSURE_DIAGNOSTIC_NO_INDEPENDENT_H3", "h4_selected_rung": "", "h4_status": "NOT_APPLICABLE_INDEPENDENT_ROUTE"})
                else:
                    hv = h4[component]
                    writer.writerow({"component": component, "role": role, "formal_combination": "C3/L3", "h3_status": formal_h3[component], "h4_selected_rung": hv["selected_rung"] or "", "h4_status": hv["status"]})
    print(json.dumps({
        "terminal_status": terminal, "metrics_sha256": sha256(METRICS_PATH),
        "diagnostics_csv_sha256": sha256(DIAGNOSTICS_CSV_PATH), "verdicts_sha256": sha256(VERDICTS_PATH),
        "formal_h3": formal_h3, "formal_h4": h4,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
