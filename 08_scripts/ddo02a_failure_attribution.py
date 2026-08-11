#!/usr/bin/env python3
"""DDO-02A consumed-evidence failure attribution; never emits an H3 verdict."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))
from ddo02_descriptors import DESCRIPTOR_NAMES, compute_case_descriptors, descriptor_specs  # noqa: E402

DATA = ROOT / "data/ddo02a"
REPORT = ROOT / "07_reports"
MANIFEST = ROOT / "06_manifests"
OBS_INDEX = ROOT / "data/atlas/ddo01d_observable_atlas.json"
META = ROOT / "data/atlas/ddo01d_case_metadata.json"
SAMPLES = ROOT / "06_manifests/ddo01e_particle_sample_registry.json"
FEATURE = ROOT / "data/identifiability/ddo01e_observable_feature_cache.npz"
TARGET = ROOT / "data/identifiability/ddo01e_reference_target_cache.npz"
DIAG = ROOT / "data/identifiability/ddo01e_non_neural_diagnostics.csv"
VERDICTS = ROOT / "data/identifiability/ddo01e_formal_verdicts.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def observability_class(field: str) -> tuple[str, str]:
    design_only = {"obs__kh_max", "obs__kh_rms", "obs__mode_count", "obs__jitter_fraction"}
    direct = {
        "obs__rho_over_rho0", "obs__delta_rho_over_rho0", "obs__pressure_over_P0",
        "obs__support_h_over_L0", "obs__support_over_dx", "obs__mach", "obs__reynolds", "obs__eps64",
    }
    if field in design_only:
        return "DESIGN_ONLY", "requires manufactured-wave or prescribed-jitter design metadata"
    if field in direct:
        return "RUNTIME_DIRECT", "stored low-cost state or frozen numerical parameter"
    return "RUNTIME_ESTIMABLE", "deterministically computable from low-cost particles/graph without reference truth"


def robust(train: np.ndarray, query: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    med = np.median(train, axis=0)
    q1 = np.quantile(train, .25, axis=0, method="inverted_cdf")
    q3 = np.quantile(train, .75, axis=0, method="inverted_cdf")
    keep = np.isfinite(med) & np.isfinite(q1) & np.isfinite(q3) & (q3 > q1)
    return (train[:, keep]-med[keep])/(q3[keep]-q1[keep]), (query[:, keep]-med[keep])/(q3[keep]-q1[keep])


def ridge(train_x: np.ndarray, train_y: np.ndarray, query_x: np.ndarray) -> np.ndarray:
    y = train_y[:, None] if train_y.ndim == 1 else train_y
    xm, ym = train_x.mean(0), y.mean(0)
    xc, yc = train_x-xm, y-ym
    gram = xc.T @ xc
    gram.flat[::gram.shape[0]+1] += 1.0
    beta = np.linalg.solve(gram, xc.T @ yc)
    pred = (query_x-xm) @ beta + ym
    return pred[:, 0] if train_y.ndim == 1 else pred


def norm2(value: np.ndarray) -> np.ndarray:
    return value*value if value.ndim == 1 else np.sum(value*value, axis=-1)


def diagnostic_cv(x: np.ndarray, y: np.ndarray, folds: np.ndarray, keys: np.ndarray) -> dict[str, float]:
    dnn, errors, energies = [], [], []
    for fold in range(5):
        tr, qu = np.flatnonzero(folds != fold), np.flatnonzero(folds == fold)
        tx, qx = robust(x[tr], x[qu])
        tree = cKDTree(tx, compact_nodes=True, balanced_tree=True)
        _, nn = tree.query(qx, k=10, eps=0, workers=1)
        near = y[tr][nn]
        random_idx = np.empty((qu.size, 10), dtype=np.int64)
        for i, key in enumerate(keys[qu]):
            seed = int.from_bytes(hashlib.sha256(("DDO02A|"+str(key)).encode()).digest()[:8], "big")
            random_idx[i] = np.random.Generator(np.random.PCG64(seed)).choice(tr.size, 10, replace=False)
        random = y[tr][random_idx]
        qy = y[qu]
        near_diff = near-qy[:, None] if qy.ndim == 1 else near-qy[:, None, :]
        rand_diff = random-qy[:, None] if qy.ndim == 1 else random-qy[:, None, :]
        if qy.ndim == 1:
            num = np.mean(near_diff * near_diff, axis=1)
            den = np.mean(rand_diff * rand_diff, axis=1)
        else:
            num = np.mean(np.sum(near_diff * near_diff, axis=2), axis=1)
            den = np.mean(np.sum(rand_diff * rand_diff, axis=2), axis=1)
        ratio = np.divide(num, den, out=np.full_like(num, np.inf), where=den > 0)
        finite = ratio[np.isfinite(ratio)]
        ratio = np.nan_to_num(ratio, nan=float(finite.max()), posinf=float(finite.max()))
        pred = ridge(tx, y[tr], qx)
        errors.append(float(np.mean(norm2(pred-qy))))
        energies.append(float(np.mean(norm2(qy))))
        dnn.extend(ratio.tolist())
    return {
        "dnn_median": float(np.median(dnn)),
        "dnn_p90": float(np.quantile(dnn, .9, method="inverted_cdf")),
        "ridge_nrmse": float(math.sqrt(np.mean(errors)/np.mean(energies))),
        "sample_count": int(len(dnn)),
    }


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    old_verdict_hash = sha256(VERDICTS)
    old = json.loads(VERDICTS.read_text())
    if old["terminal_status"] != "DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE":
        raise RuntimeError("frozen negative prerequisite missing")
    obs_index = json.loads(OBS_INDEX.read_text())
    samples = json.loads(SAMPLES.read_text())
    metadata = json.loads(META.read_text())

    ledger_path = DATA / "deployment_observability_ledger.csv"
    with ledger_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("field", "classification", "reason", "future_formal_feature_eligible"))
        writer.writeheader()
        for field in sorted(name for name in obs_index["schema"] if name.startswith("obs__")):
            cls, reason = observability_class(field)
            writer.writerow({"field": field, "classification": cls, "reason": reason,
                             "future_formal_feature_eligible": cls != "DESIGN_ONLY"})

    dictionary_path = DATA / "candidate_descriptor_dictionary.csv"
    with dictionary_path.open("w", newline="") as handle:
        fields = ("name", "source_fields", "reference_free", "rotation_behavior", "normalization", "scope", "complexity")
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for item in descriptor_specs():
            writer.writerow({**item, "source_fields": ";".join(item["source_fields"])})

    cache_path = DATA / "attribution_descriptor_cache.npz"
    case_summary, counters = [], Counter()
    if cache_path.exists():
        with np.load(cache_path, allow_pickle=False) as cached:
            descriptors = np.asarray(cached["descriptors"])
            frames = np.asarray(cached["frames"])
        for case_index in range(512):
            values = descriptors[case_index*128:(case_index+1)*128]
            case_summary.append({"case_index": case_index, **{
                f"descriptor_mean__{name}": float(values[:, i].mean()) for i, name in enumerate(DESCRIPTOR_NAMES)}})
        counters["quadratic_failure_count"] = int(descriptors[:, -1].sum())
        counters["sample_particle_count"] = int(descriptors.shape[0])
    else:
        descriptor_rows, frame_rows = [], []
        for number, (entry, sample) in enumerate(zip(obs_index["cases"], samples["cases"], strict=True)):
            with np.load(ROOT / entry["path"], allow_pickle=False) as obs:
                values, frames_case, qc = compute_case_descriptors(obs)
            ids = np.asarray(sample["particle_ids"], dtype=np.int64)
            descriptor_rows.append(values[ids]); frame_rows.append(frames_case[ids])
            case_summary.append({"case_index": entry["case_index"], **{
                f"descriptor_mean__{name}": float(values[ids, i].mean()) for i, name in enumerate(DESCRIPTOR_NAMES)}})
            counters.update(qc)
            if (number+1) % 32 == 0:
                print(f"ddo02a_descriptor_case {number+1}/512", flush=True)
        descriptors = np.concatenate(descriptor_rows)
        frames = np.concatenate(frame_rows)
        with cache_path.open("wb") as handle:
            np.savez_compressed(handle, descriptors=descriptors, frames=frames,
                                descriptor_names=np.asarray(DESCRIPTOR_NAMES, dtype="U64"))

    with np.load(FEATURE, allow_pickle=False) as feature, np.load(TARGET, allow_pickle=False) as target:
        # 32 deterministic already-frozen samples per case; this remains consumed diagnostic evidence.
        take = (np.arange(feature["sample_key"].size) % 128) < 32
        keys = np.asarray(feature["sample_key"])[take]
        folds = np.asarray(feature["sample_fold"])[take]
        base = np.concatenate([np.asarray(feature[f"feature__{layer}__I0"])[take]
                               for layer in ("G", "C", "P")], axis=1)
        desc = descriptors[take]
        frm = frames[take]
        alternatives = {
            "CURRENT_INVARIANT_COMPACT": base,
            "HIGHER_ORDER_PARTICLE_MOMENTS": np.concatenate((base, desc[:, :14]), axis=1),
            "HIGHER_DERIVATIVE_PROXIES": np.concatenate((base, desc[:, 18:]), axis=1),
            "COMPONENT_SPECIFIC_COMBINATION": np.concatenate((base, desc), axis=1),
        }
        components = {
            "density_rate": np.asarray(target["target__density_rate"])[take],
            "pressure_gradient": np.asarray(target["target__pressure_gradient_acceleration"])[take],
            "viscosity_laplacian": np.asarray(target["target__viscosity_laplacian_acceleration"])[take],
        }
        results = defaultdict(dict)
        for component, y in components.items():
            for name, x in alternatives.items():
                results[component][name] = diagnostic_cv(x, y, folds, keys)
            if y.ndim == 2:
                aligned = np.einsum("ni,nij->nj", y, frm)
                results[component]["EQUIVARIANT_DIRECTIONAL"] = diagnostic_cv(
                    np.concatenate((base, desc[:, 14:18]), axis=1), aligned, folds, keys)

    # Frozen case-level tail attribution, joined only after the diagnostics are consumed.
    with DIAG.open(newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["content"] == "C3" and r["locality"] == "L3"
                and r["component"] in ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration")]
    meta_by_case = {int(item["case_index"]): item for item in metadata["cases"]}
    summary_by_case = {int(item["case_index"]): item for item in case_summary}
    tail = {}
    for component in ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration"):
        cr = [row for row in rows if row["component"] == component]
        threshold = float(np.quantile([float(row["dnn_p90"]) for row in cr], .9, method="inverted_cdf"))
        selected = [row for row in cr if float(row["dnn_p90"]) >= threshold]
        families = Counter(row["family"] for row in selected)
        layouts = Counter(meta_by_case[int(row["case_index"])]["layout_class"] for row in selected)
        numeric = {}
        for field in ("resolution_per_axis", "support_over_dx", "jitter_fraction"):
            numeric[field] = float(np.median([meta_by_case[int(row["case_index"])][field] for row in selected]))
        for name in ("moment2_anisotropy", "moment4_frobenius", "quadratic_log10_condition",
                     "quadratic_failure_flag"):
            numeric[name] = float(np.median([summary_by_case[int(row["case_index"])][f"descriptor_mean__{name}"] for row in selected]))
        tail[component] = {"frozen_case_dnn_p90_top_decile_threshold": threshold, "case_count": len(selected),
                           "family_counts": dict(families), "layout_counts": dict(layouts), "median_associations": numeric}

    decisions = {}
    mapping = {
        "EQUIVARIANT_DIRECTIONAL": ("pressure_gradient", "viscosity_laplacian"),
        "HIGHER_ORDER_PARTICLE_MOMENTS": ("density_rate", "pressure_gradient", "viscosity_laplacian"),
        "HIGHER_DERIVATIVE_PROXIES": ("density_rate", "pressure_gradient", "viscosity_laplacian"),
        "COMPONENT_SPECIFIC_COMBINATION": ("density_rate", "pressure_gradient", "viscosity_laplacian"),
    }
    for hypothesis, comps in mapping.items():
        improvements = []
        for comp in comps:
            if hypothesis not in results[comp]:
                continue
            b = results[comp]["CURRENT_INVARIANT_COMPACT"]["dnn_p90"]
            n = results[comp][hypothesis]["dnn_p90"]
            improvements.append((b-n)/b if b else 0.0)
        best = max(improvements) if improvements else 0.0
        decisions[hypothesis] = {
            "status": "SUPPORTED_FOR_FRESH_TEST" if best >= .10 else ("NOT_SUPPORTED" if best <= 0 else "INCONCLUSIVE"),
            "best_dnn_p90_relative_reduction": best,
            "basis": "consumed 512-case development evidence; diagnostic only",
        }

    metrics = {
        "schema_version": "1.0", "stage": "DDO-02A", "metric_role": "FAILURE_ATTRIBUTION_DIAGNOSTIC",
        "permanent_prior_terminal_status": old["terminal_status"], "prior_verdict_sha256": old_verdict_hash,
        "diagnostic_sample_count": 16384, "components": results, "tail_attribution": tail,
        "descriptor_qc": dict(counters), "rescue_hypotheses": decisions,
        "controls": {"h3_requalification": False, "h3_pass_emitted": False, "neural_training": False,
                     "target_alignment_selected_from_observables_only": True},
    }
    metrics_path = DATA / "attribution_metrics.json"; write_json(metrics_path, metrics)

    role_ledger = {
        "schema_version": "1.0", "stage": "DDO-02A", "case_count": 512,
        "canonical_role_labels": ["DEVELOPMENT_ATLAS", "CONSUMED_OBSERVABLE_DESIGN_EVIDENCE"],
        "future_formal_h3_eligibility": False, "source_registry_sha256": sha256(ROOT / "06_manifests/ddo01d_case_registry.json"),
        "permanent_terminal_status": old["terminal_status"],
    }
    write_json(MANIFEST / "ddo02_project_status_ledger.json", role_ledger)

    design_only = [row for row in csv.DictReader(ledger_path.open()) if row["classification"] == "DESIGN_ONLY"]
    def report(name: str, title: str, body: str) -> None:
        (REPORT / name).write_text(f"# {title}\n\n{body}\n")
    report("ddo02a_failure_attribution_report.md", "DDO-02A failure attribution",
           f"All results are `FAILURE_ATTRIBUTION_DIAGNOSTIC`. The permanent result remains `{old['terminal_status']}`. "
           f"The diagnostic used 16,384 particles from the consumed 512-case atlas. Rescue decisions: `{json.dumps(decisions, sort_keys=True)}`.")
    report("ddo02a_deployment_observability_report.md", "Deployment observability audit",
           f"Every existing `obs__` field was classified exactly once. DESIGN_ONLY fields are: "
           f"{', '.join(row['field'] for row in design_only)}. Reference-free does not imply deployment-observable; these fields are prohibited from future formal inputs.")
    report("ddo02a_directional_attribution_report.md", "Directional and equivariance attribution",
           "Targets were rotated only by covariance-principal frames derived from observable particle geometry. "
           "No target-similarity alignment was used. The detailed comparable DNN and ridge results are in `data/ddo02a/attribution_metrics.json`.")
    report("ddo02a_moment_attribution_report.md", "Higher-order moment attribution",
           "Reference-free second-, third- and fourth-order weighted moments, eigen-invariants, condition numbers and angular harmonics m=1..4 were evaluated. "
           f"The fresh-test decision is `{decisions['HIGHER_ORDER_PARTICLE_MOMENTS']['status']}`.")
    report("ddo02a_derivative_proxy_report.md", "Higher-derivative proxy attribution",
           "Weighted local quadratic reconstructions used only low-cost density, velocity differences and particle geometry. Ill-conditioned particles were retained with a failure flag and capped log-condition value. "
           f"The fresh-test decision is `{decisions['HIGHER_DERIVATIVE_PROXIES']['status']}`.")
    report("ddo02a_tail_attribution_report.md", "Frozen ambiguity-tail attribution",
           "The top decile was isolated from the frozen DDO-01E C3/L3 case DNN-p90 diagnostic and associated with family, resolution, h/dx, disorder, consistency, moments, reconstruction conditioning and directional degeneracy. "
           "This consumed-evidence analysis cannot emit a new H3 PASS.")
    report("ddo02a_next_stage_decision.md", "DDO-02A next-stage decision",
           "DDO-02A is frozen. Only hypotheses marked `SUPPORTED_FOR_FRESH_TEST` are preferred for CA-06; INCONCLUSIVE descriptors may be retained as preregistered secondary ablations. "
           "No neural architecture is selected or authorized.")

    bound = [ledger_path, dictionary_path, metrics_path, cache_path, MANIFEST / "ddo02_project_status_ledger.json"] + [
        REPORT / name for name in (
            "ddo02a_failure_attribution_report.md", "ddo02a_deployment_observability_report.md",
            "ddo02a_directional_attribution_report.md", "ddo02a_moment_attribution_report.md",
            "ddo02a_derivative_proxy_report.md", "ddo02a_tail_attribution_report.md", "ddo02a_next_stage_decision.md")]
    manifest = {
        "schema_version": "1.0", "stage": "DDO-02A", "terminal_status": "DDO02A_FAILURE_ATTRIBUTION_FROZEN",
        "permanent_prior_status": old["terminal_status"], "prior_verdict_sha256_before": old_verdict_hash,
        "prior_verdict_sha256_after": sha256(VERDICTS), "prior_verdict_unchanged": sha256(VERDICTS) == old_verdict_hash,
        "bound_files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in bound],
        "controls": {"formal_h3_evaluated": False, "neural_training": False, "h5_authorized": False},
    }
    write_json(MANIFEST / "ddo02a_manifest.json", manifest)
    print(json.dumps({"terminal_status": manifest["terminal_status"], "manifest_sha256": sha256(MANIFEST / "ddo02a_manifest.json"),
                      "rescue_hypotheses": decisions}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
