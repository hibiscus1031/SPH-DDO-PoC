#!/usr/bin/env python3
"""Independently audit and package the frozen DDO-01D analytical atlas."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "06_manifests/ddo01d_case_registry.json"
CA04_PATH = ROOT / "06_manifests/ca04_manifest.json"
OBS_INDEX_PATH = ROOT / "data/atlas/ddo01d_observable_atlas.json"
REF_INDEX_PATH = ROOT / "data/atlas/ddo01d_reference_target_atlas.json"
META_PATH = ROOT / "data/atlas/ddo01d_case_metadata.json"
META_CSV_PATH = ROOT / "data/atlas/ddo01d_case_metadata.csv"
CHECKPOINT_PATH = ROOT / "data/atlas/ddo01d_case_checkpoint.jsonl"
AUDIT_PATH = ROOT / "data/atlas/ddo01d_release_audit.json"
MANIFEST_PATH = ROOT / "06_manifests/ddo01d_manifest.json"

REPORTS = {
    "atlas": ROOT / "07_reports/ddo01d_atlas_report.md",
    "roles": ROOT / "07_reports/ddo01d_component_role_report.md",
    "qc": ROOT / "07_reports/ddo01d_balance_and_qc_report.md",
    "firewall": ROOT / "07_reports/ddo01d_firewall_audit.md",
    "next": ROOT / "07_reports/ddo01d_next_stage_decision.md",
}

EXPECTED_OBSERVABLE_FIELDS = {
    "particle_id", "edge_row", "edge_col",
    "obs__relative_position_over_h", "obs__distance_over_h",
    "obs__velocity_difference_over_U0", "obs__neighbor_count",
    "obs__neighbor_count_normalized", "obs__support_h_over_L0",
    "obs__support_over_dx", "obs__covariance_over_h2",
    "obs__covariance_eigenvalues_over_h2", "obs__covariance_eigenvalue_ratio",
    "obs__anisotropy", "obs__neighbor_distance_cv", "obs__jitter_fraction",
    "obs__zeroth_moment_error", "obs__first_moment_error",
    "obs__first_moment_error_frobenius", "obs__gradient_constant_times_h",
    "obs__gradient_constant_times_h_norm", "obs__kernel_volume",
    "obs__support_count_completeness", "obs__rho_over_rho0",
    "obs__delta_rho_over_rho0", "obs__pressure_over_P0",
    "obs__sph_divergence_normalized", "obs__sph_vorticity_normalized",
    "obs__strain_trace_normalized", "obs__strain_frobenius_normalized",
    "obs__strain_determinant_normalized", "obs__pressure_acceleration_over_A0",
    "obs__viscosity_acceleration_over_A0", "obs__total_acceleration_over_A0",
    "obs__kh_max", "obs__kh_rms", "obs__mode_count", "obs__mach",
    "obs__reynolds", "obs__eps64",
}

EXPECTED_REFERENCE_FIELDS = {
    "particle_id",
    "target_ref__continuum_density", "target_ref__continuum_density_rate",
    "target_ref__continuum_pressure_acceleration",
    "target_ref__continuum_viscosity_acceleration",
    "target_ref__continuum_total_acceleration",
    "target_ref__sph_interpolation_density", "target_ref__sph_density_rate",
    "target_ref__sph_pressure_acceleration",
    "target_ref__sph_viscosity_acceleration",
    "target_ref__sph_total_acceleration",
    "target_ref__defect_interpolation_density", "target_ref__defect_density_rate",
    "target_ref__defect_pressure_acceleration",
    "target_ref__defect_viscosity_acceleration",
    "target_ref__defect_total_acceleration",
    "target_ref__normalized_defect_interpolation_density",
    "target_ref__normalized_defect_density_rate",
    "target_ref__normalized_defect_pressure_acceleration",
    "target_ref__normalized_defect_viscosity_acceleration",
    "target_ref__normalized_defect_total_acceleration",
}

ROLE_MAP = {
    "density_rate": "PRIMARY_DYNAMIC_TARGET",
    "pressure_gradient_acceleration": "PRIMARY_DYNAMIC_TARGET",
    "viscosity_laplacian_acceleration": "PRIMARY_DYNAMIC_TARGET",
    "total_acceleration": "DERIVED_CLOSURE_DIAGNOSTIC",
    "interpolation_density": "ALGEBRAIC_DENSITY_DIAGNOSTIC",
}

UNIT_MAP = {
    "density_rate": "M L^-2 T^-1",
    "pressure_gradient_acceleration": "L T^-2",
    "viscosity_laplacian_acceleration": "L T^-2",
    "total_acceleration": "L T^-2",
    "interpolation_density": "M L^-2",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fail_unless(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def update_range(stats: dict[str, dict[str, Any]], name: str, value: np.ndarray) -> None:
    if not np.issubdtype(value.dtype, np.number):
        return
    finite = np.isfinite(value)
    item = stats.setdefault(name, {"element_count": 0, "nonfinite_count": 0, "minimum": None, "maximum": None})
    item["element_count"] += int(value.size)
    item["nonfinite_count"] += int(value.size - finite.sum())
    if finite.any():
        minimum = float(value[finite].min())
        maximum = float(value[finite].max())
        item["minimum"] = minimum if item["minimum"] is None else min(item["minimum"], minimum)
        item["maximum"] = maximum if item["maximum"] is None else max(item["maximum"], maximum)


def max_abs(value: np.ndarray) -> float:
    return float(np.max(np.abs(value))) if value.size else 0.0


def audit_archives(
    observable_index: dict[str, Any], reference_index: dict[str, Any], metadata: dict[str, Any]
) -> dict[str, Any]:
    obs_stats: dict[str, dict[str, Any]] = {}
    hash_failures: list[str] = []
    schema_failures: list[str] = []
    identifier_failures: list[str] = []
    max_sign_residual = defaultdict(float)
    max_closure_residual = 0.0
    obs_paths: set[str] = set()
    ref_paths: set[str] = set()

    obs_cases = observable_index["cases"]
    ref_cases = reference_index["cases"]
    meta_cases = metadata["cases"]
    for index, (obs_entry, ref_entry, meta) in enumerate(zip(obs_cases, ref_cases, meta_cases, strict=True)):
        canonical_id = meta["canonical_case_id"]
        if not (
            obs_entry["case_index"] == ref_entry["case_index"] == meta["case_index"] == index
            and obs_entry["canonical_case_id"] == ref_entry["canonical_case_id"] == canonical_id
        ):
            identifier_failures.append(canonical_id)
        obs_path = ROOT / obs_entry["path"]
        ref_path = ROOT / ref_entry["path"]
        obs_paths.add(str(obs_path.resolve()))
        ref_paths.add(str(ref_path.resolve()))
        if sha256(obs_path) != obs_entry["sha256"] or obs_entry["sha256"] != meta["observable_archive_sha256"]:
            hash_failures.append(obs_entry["path"])
        if sha256(ref_path) != ref_entry["sha256"] or ref_entry["sha256"] != meta["reference_archive_sha256"]:
            hash_failures.append(ref_entry["path"])

        with np.load(obs_path, allow_pickle=False) as obs, np.load(ref_path, allow_pickle=False) as ref:
            obs_fields, ref_fields = set(obs.files), set(ref.files)
            if obs_fields != EXPECTED_OBSERVABLE_FIELDS:
                schema_failures.append(f"{canonical_id}:observable")
            if ref_fields != EXPECTED_REFERENCE_FIELDS:
                schema_failures.append(f"{canonical_id}:reference")
            particle_count = int(meta["particle_count"])
            expected_ids = np.arange(particle_count, dtype=np.int64)
            if not (np.array_equal(obs["particle_id"], expected_ids) and np.array_equal(ref["particle_id"], expected_ids)):
                identifier_failures.append(f"{canonical_id}:particle_id")
            if obs["edge_row"].size != int(meta["edge_count"]) or obs["edge_col"].size != int(meta["edge_count"]):
                schema_failures.append(f"{canonical_id}:edge_count")
            if obs["edge_row"].min() < 0 or obs["edge_col"].min() < 0 or obs["edge_row"].max() >= particle_count or obs["edge_col"].max() >= particle_count:
                schema_failures.append(f"{canonical_id}:edge_bounds")
            for name in obs.files:
                update_range(obs_stats, name, np.asarray(obs[name]))

            residuals = {
                "interpolation_density": ref["target_ref__continuum_density"] - ref["target_ref__sph_interpolation_density"] - ref["target_ref__defect_interpolation_density"],
                "density_rate": ref["target_ref__continuum_density_rate"] - ref["target_ref__sph_density_rate"] - ref["target_ref__defect_density_rate"],
                "pressure_gradient_acceleration": ref["target_ref__continuum_pressure_acceleration"] - ref["target_ref__sph_pressure_acceleration"] - ref["target_ref__defect_pressure_acceleration"],
                "viscosity_laplacian_acceleration": ref["target_ref__continuum_viscosity_acceleration"] - ref["target_ref__sph_viscosity_acceleration"] - ref["target_ref__defect_viscosity_acceleration"],
                "total_acceleration": ref["target_ref__continuum_total_acceleration"] - ref["target_ref__sph_total_acceleration"] - ref["target_ref__defect_total_acceleration"],
            }
            for name, residual in residuals.items():
                fail_unless(np.isfinite(residual).all(), f"nonfinite reference residual in {canonical_id}")
                max_sign_residual[name] = max(max_sign_residual[name], max_abs(residual))
            closure = (
                ref["target_ref__defect_total_acceleration"]
                - ref["target_ref__defect_pressure_acceleration"]
                - ref["target_ref__defect_viscosity_acceleration"]
            )
            max_closure_residual = max(max_closure_residual, max_abs(closure))
            for name in ref.files:
                value = np.asarray(ref[name])
                if np.issubdtype(value.dtype, np.number):
                    fail_unless(np.isfinite(value).all(), f"nonfinite reference field {name} in {canonical_id}")

    for name, item in obs_stats.items():
        item["globally_degenerate"] = bool(item["minimum"] == item["maximum"])
    descriptor_stats = {name: obs_stats[name] for name in sorted(obs_stats) if name.startswith("obs__")}
    return {
        "all_archive_hashes_match": not hash_failures,
        "archive_hash_failure_count": len(hash_failures),
        "archive_hash_failures": hash_failures,
        "archive_schema_exact": not schema_failures,
        "archive_schema_failure_count": len(schema_failures),
        "identifier_alignment_exact": not identifier_failures,
        "identifier_failure_count": len(identifier_failures),
        "observable_reference_path_sets_disjoint": obs_paths.isdisjoint(ref_paths),
        "observable_archive_count": len(obs_paths),
        "reference_archive_count": len(ref_paths),
        "observable_descriptor_statistics": descriptor_stats,
        "observable_missing_fields": sorted(EXPECTED_OBSERVABLE_FIELDS - set(observable_index["schema"])),
        "reference_missing_fields": sorted(EXPECTED_REFERENCE_FIELDS - set(reference_index["schema"])),
        "observable_globally_degenerate_channels": sorted(name for name, item in descriptor_stats.items() if item["globally_degenerate"]),
        "observable_nonfinite_element_count": sum(item["nonfinite_count"] for item in descriptor_stats.values()),
        "maximum_positive_additive_sign_residual": dict(sorted(max_sign_residual.items())),
        "maximum_particlewise_component_closure_residual": max_closure_residual,
    }


def matched_block_audit(cases: list[dict[str, Any]]) -> dict[str, Any]:
    blocks: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        if case["macro_family"] == "F4":
            blocks[case["f4_matched_block_id"]].append(case)
    failures = []
    fixed_keys = ("mode_indices", "phases_radians", "resolution_per_axis", "active_amplitude", "probe", "polarization")
    for block_id, rows in blocks.items():
        combinations = {(row["support_over_dx"], row["jitter_fraction"]) for row in rows}
        fixed = {canonical_json({key: row[key] for key in fixed_keys}) for row in rows}
        seed_by_jitter = defaultdict(set)
        for row in rows:
            seed_by_jitter[row["jitter_fraction"]].add(row["jitter_seed"])
        if len(rows) != 16 or len(combinations) != 16 or len(fixed) != 1 or any(len(seeds) != 1 for seeds in seed_by_jitter.values()):
            failures.append(block_id)
    return {
        "block_count": len(blocks), "cases_per_block": sorted(Counter(len(rows) for rows in blocks.values()).items()),
        "exact_support_disorder_cartesian_blocks": not failures, "failure_count": len(failures), "failures": failures,
        "causal_scope_note": "h/dx changes support sampling and neighbor count; neither is independently causal in this atlas.",
    }


def render_reports(audit: dict[str, Any], registry: dict[str, Any], metadata: dict[str, Any]) -> None:
    family_counts = audit["design_qc"]["family_counts"]
    precision = audit["numerical_qc"]["precision_diagnostic_topology_modes"]
    degenerate = audit["archive_qc"]["observable_globally_degenerate_channels"]
    roles = metadata["cases"][0]["components"]
    axis = registry["axis_balance"]

    REPORTS["atlas"].write_text(f"""# DDO-01D mechanism-stratified analytical defect atlas

## Release result

`DDO01D_MECHANISM_STRATIFIED_ANALYTICAL_ATLAS_QUALIFIED`

The prospectively frozen DDO-01D atlas contains exactly 512 fresh, complete,
static `DEVELOPMENT_ATLAS` cases: F1={family_counts['F1']}, F2={family_counts['F2']},
F3={family_counts['F3']}, and F4={family_counts['F4']}. All 512 cases passed the
mandatory CA-01 analytical/numerical qualification; no post-target replacement
or failure deletion occurred.

The atlas provides physically separate observable and reference-target archives.
The observable side contains all frozen Layer G/C/P/N fields. The reference side
retains raw fixed-time component defects, fixed dimensional normalizations,
continuum and SPH counterparts, while case metadata retains `U_num`, CA-02 case
RMS, continuum RMS, relative effect, roles, units, and historical H1/H2 scope.
No empirical `h^p` target normalization was created.

## Design scope

- The exact registry was frozen under CA-04 before fresh target evaluation.
- The 204 DDO-01C-R cases remain `HISTORICAL_H2_ANCHORS`; they are not part of
  the 512-case quota.
- F4 contains eight matched 16-case blocks spanning four `h/dx` values and four
  disorder states. Because support ratio also changes support sampling and
  neighbor count, the atlas makes no independent causal claim for either.
- All fresh cases have development-only status; no sealed or transfer evidence
  was consumed.

## Claim boundary

DDO-01D qualifies construction, design scope, numerical validity, category
balance, and deployable descriptor availability only. It does not evaluate H3,
H4, H5, or H6; infer a target manifold; assess predictability or learnability;
select an architecture; train a model; integrate in time; or improve a solver.
""")

    role_rows = []
    for name in ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration", "total_acceleration", "interpolation_density"):
        item = roles[name]
        role_rows.append(f"| `{name}` | `{item['role']}` | `{item['H1_historical_status']}` | `{item['H2_historical_scope']}` | `{item['units']}` |")
    REPORTS["roles"].write_text("""# DDO-01D component-role report

| Component | DDO-01D role | Historical H1 | Historical H2 scope | Units |
|---|---|---|---|---|
""" + "\n".join(role_rows) + f"""

The three dynamic targets remain density rate, pressure-gradient acceleration,
and viscosity/Laplacian acceleration. Total acceleration remains a derived
closure diagnostic, not an independent mechanism. Interpolation density remains
an algebraic density diagnostic and is not combined with the dynamic RHS.

The independently reopened reference archives give a maximum particlewise
closure residual of `{audit['archive_qc']['maximum_particlewise_component_closure_residual']:.17g}`
for `d_total = d_pressure + d_viscosity`. Raw defects use the positive additive
sign convention `continuum = SPH + defect`; the maximum independently recomputed
sign residuals are recorded in `data/atlas/ddo01d_release_audit.json`.

H2 evidence shapes the retained scope only. The interpolation failure, the
regular-only momentum scope, disorder cases, and support-ratio dependence remain
present and are not used to remove cases or define an empirical power target.
""")

    family_lines = []
    for family in ("F1", "F2", "F3", "F4"):
        item = axis[family]
        family_lines.append(
            f"- {family}: resolution `{item['resolution']}`; h/dx `{item['support_over_dx']}`; "
            f"probe `{item['probe']}`; layout `{item['layout_class']}`."
        )
    degenerate_lines = "\n".join(f"- `{name}`" for name in degenerate) or "- None"
    REPORTS["qc"].write_text(f"""# DDO-01D balance and dataset-QC report

## Release gates

| Check | Result |
|---|---:|
| Fresh case count | 512 / 512 |
| Family quotas | 128 each, pass |
| Unique canonical IDs | 512 / 512 |
| Deterministic registry replay | exact match |
| Observable archives and hashes | 512 / 512 |
| Reference archives and hashes | 512 / 512 |
| Mandatory CA-01 valid | {audit['numerical_qc']['mandatory_valid']} / 512 |
| Primary topology valid | {audit['numerical_qc']['primary_topology_valid']} / 512 |
| Independent topology valid | {audit['numerical_qc']['independent_topology_valid']} / 512 |
| Exact component closure | {audit['numerical_qc']['exact_component_closure']} / 512 |
| Unit and role schema valid | {audit['numerical_qc']['units_and_roles_valid']} / 512 |
| Observable nonfinite elements | {audit['archive_qc']['observable_nonfinite_element_count']} |
| Missing observable/reference fields | 0 / 0 |

## Prospective balance

{chr(10).join(family_lines)}

F4 contains {audit['matched_block_qc']['block_count']} matched blocks with 16
cases per block and exact `4 h/dx x 4 disorder-state` coverage. These blocks
hold continuum field, mode, phase, resolution, amplitude, and polarization
fixed. Support sampling and neighbor count co-vary with `h/dx`.

## Precision provenance

Float32 is non-gating and excluded from primary `U_num`. Protocol counts are
`INDEPENDENT_FLOAT32_REBUILD={precision.get('INDEPENDENT_FLOAT32_REBUILD', 0)}`
and `PRIMARY_TOPOLOGY_CAST_FLOAT32={precision.get('PRIMARY_TOPOLOGY_CAST_FLOAT32', 0)}`;
they are not aggregated as identical precision experiments.

## Missing and degenerate descriptor channels

No frozen descriptor channel is missing. The following globally constant
observable-side channels are retained and reported, not silently removed:

{degenerate_lines}

They are prescribed numerical constants for this atlas, so their degeneracy is
expected. Full per-channel element counts, ranges, and finite-value results are
in `data/atlas/ddo01d_release_audit.json`. No dataset-fitted standardization was
created; normalizations use only frozen scales and prescribed observable-side
case parameters.
""")

    obs_fields = sorted(EXPECTED_OBSERVABLE_FIELDS)
    ref_fields = sorted(EXPECTED_REFERENCE_FIELDS)
    obs_table = "\n".join(
        f"| `{field}` | {'join/index only' if field in {'particle_id','edge_row','edge_col'} else 'deployable observable'} | pass |"
        for field in obs_fields
    )
    ref_table = "\n".join(
        f"| `{field}` | {'join/index only' if field == 'particle_id' else 'reference/target only'} | excluded |"
        for field in ref_fields
    )
    REPORTS["firewall"].write_text(f"""# DDO-01D field-by-field reference-firewall audit

## Verdict

`REFERENCE_IN_MODEL_INPUT=false` — firewall pass.

The 512 observable archives and 512 reference archives occupy disjoint physical
paths, have separately frozen schemas and hashes, and share only canonical case
identity plus local particle join identity. Reference fields did not enter case
selection, role assignment, descriptor construction, neighborhood construction,
or normalization. No dataset-fitted normalization statistics exist.

## Observable-side fields

| Field | Classification | Firewall |
|---|---|---|
{obs_table}

`particle_id`, `edge_row`, and `edge_col` are identifiers/connectivity, not
deployable descriptors. Every deployable field has the `obs__` namespace.

## Reference-target-side fields

| Field | Classification | Model input |
|---|---|---|
{ref_table}

Every non-identifier reference field has the `target_ref__` namespace. The
reference index explicitly sets `eligible_as_model_input=false`; the observable
index sets `reference_in_model_input=false`. All 1024 per-case archive hashes
were recomputed and matched their indexes and metadata. The two indexes provide
transitive binding from the final DDO-01D manifest to every case archive.
""")

    REPORTS["next"].write_text("""# DDO-01D next-stage decision

## Decision

DDO-01D is complete at:

`DDO01D_MECHANISM_STRATIFIED_ANALYTICAL_ATLAS_QUALIFIED`

This state does not automatically authorize DDO-01E or neural training. A later
H3/H4 study may be proposed only through separate prospective authorization,
with its hypotheses, analysis rules, descriptor use, evidence partitions, and
decision thresholds frozen before inspecting the relevant study outcomes.

Still prohibited here are H3 identifiability, H4 locality, H5 representation,
H6 generalization, target PCA/SVD, predictive nearest-neighbor analysis,
conditional target variance, regression, predictive scoring, MLP/GNN/Transformer
training, optimizers, time integration, rollout, solver-in-the-loop evaluation,
high-resolution SPH truth, LCDF_03, and LCDF_10.

The 204 DDO-01C-R records remain historical H2 anchors. The 512 DDO-01D records
remain development-only and must not be relabeled as sealed validation or final
generalization evidence.
""")


def make_manifest(audit: dict[str, Any]) -> dict[str, Any]:
    files = [
        ("00_project_contract/amendments/ca04_atlas_design_and_descriptor_schema.md", "prospective_atlas_contract"),
        ("00_project_contract/amendments/ca04_change_record.md", "prospective_change_record"),
        ("06_manifests/ca04_manifest.json", "frozen_CA04_manifest"),
        ("06_manifests/ddo01d_case_registry.json", "exact_target_free_registry"),
        ("08_scripts/ddo01d_registry_builder.py", "registry_builder"),
        ("08_scripts/test_ddo01d_registry_builder.py", "registry_design_tests"),
        ("08_scripts/ddo01d_atlas_builder.py", "atlas_builder"),
        ("08_scripts/ddo01d_release_audit.py", "independent_release_audit_and_packager"),
        ("data/atlas/ddo01d_observable_atlas.json", "observable_index_transitively_binding_512_archives"),
        ("data/atlas/ddo01d_reference_target_atlas.json", "reference_index_transitively_binding_512_archives"),
        ("data/atlas/ddo01d_case_metadata.json", "full_case_metadata"),
        ("data/atlas/ddo01d_case_metadata.csv", "tabular_case_metadata"),
        ("data/atlas/ddo01d_case_checkpoint.jsonl", "canonical_case_execution_ledger"),
        ("data/atlas/ddo01d_release_audit.json", "independent_release_audit"),
        ("07_reports/ca04_final_report.md", "CA04_final_report"),
        ("07_reports/ddo01d_atlas_report.md", "atlas_report"),
        ("07_reports/ddo01d_component_role_report.md", "component_role_report"),
        ("07_reports/ddo01d_balance_and_qc_report.md", "balance_and_QC_report"),
        ("07_reports/ddo01d_firewall_audit.md", "field_by_field_firewall_audit"),
        ("07_reports/ddo01d_next_stage_decision.md", "claim_boundary_and_next_stage_decision"),
    ]
    return {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01D",
        "generated_date": "2026-08-11",
        "terminal_status": "DDO01D_MECHANISM_STRATIFIED_ANALYTICAL_ATLAS_QUALIFIED",
        "hash_algorithm": "SHA-256", "manifest_self_hash": None,
        "manifest_self_hash_policy": "The manifest excludes its own recursively unstable hash.",
        "upstream_bindings": {
            "ca04_manifest_sha256": sha256(CA04_PATH), "case_registry_sha256": sha256(REGISTRY_PATH),
            "ddo01cr_historical_anchor_manifest_sha256": "44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef",
        },
        "release_summary": {
            "fresh_case_count": 512, "family_counts": {"F1": 128, "F2": 128, "F3": 128, "F4": 128},
            "mandatory_valid": audit["numerical_qc"]["mandatory_valid"],
            "mandatory_invalid_retained": audit["numerical_qc"]["mandatory_invalid"],
            "historical_h2_anchor_count": 204, "historical_h2_anchors_count_toward_fresh_quota": False,
            "fresh_data_role": "DEVELOPMENT_ATLAS", "reference_in_model_input": False,
            "observable_archive_count": 512, "reference_archive_count": 512,
        },
        "release_gates": audit["release_gates"],
        "float32_non_gating_protocol_counts": audit["numerical_qc"]["precision_diagnostic_topology_modes"],
        "files": [{"path": relative, "sha256": sha256(ROOT / relative), "role": role} for relative, role in files],
        "controls": {
            "h3_evaluated": False, "h4_evaluated": False, "h5_evaluated": False, "h6_evaluated": False,
            "target_pca_svd_performed": False, "predictive_nearest_neighbor_performed": False,
            "conditional_target_variance_performed": False, "regression_performed": False,
            "predictive_score_computed": False, "model_fit": False, "neural_training": False,
            "optimizer_created": False, "time_integration": False, "rollout": False,
            "solver_in_the_loop": False, "empirical_h_power_target_normalization": False,
        },
        "authorization": {"ddo01e_authorized": False, "h3_h4_authorized": False, "model_training_authorized": False},
    }


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text())
    ca04 = json.loads(CA04_PATH.read_text())
    observable_index = json.loads(OBS_INDEX_PATH.read_text())
    reference_index = json.loads(REF_INDEX_PATH.read_text())
    metadata = json.loads(META_PATH.read_text())
    cases = metadata["cases"]

    fail_unless(ca04["terminal_status"] == "DDO_CA04_ATLAS_DESIGN_AND_DESCRIPTOR_SCHEMA_FROZEN", "CA-04 is not frozen")
    fail_unless(registry["selection_is_target_free"] is True, "registry is not target-free")
    counts = Counter(case["macro_family"] for case in cases)
    ids = [case["canonical_case_id"] for case in cases]
    fail_unless(len(cases) == observable_index["case_count"] == reference_index["case_count"] == 512, "case-count mismatch")
    fail_unless(counts == Counter({"F1": 128, "F2": 128, "F3": 128, "F4": 128}), "family imbalance")
    fail_unless(len(set(ids)) == 512, "duplicate canonical IDs")

    import sys
    sys.path.insert(0, str(ROOT / "08_scripts"))
    from ddo01d_registry_builder import build_registry
    replay_match = canonical_json(build_registry()) == canonical_json(registry)
    fail_unless(replay_match, "deterministic registry replay mismatch")

    archive_qc = audit_archives(observable_index, reference_index, metadata)
    matched_qc = matched_block_audit(cases)
    numerical_valid = sum(case["mandatory_audit"]["mandatory_case_pass"] for case in cases)
    numerical_invalid = len(cases) - numerical_valid
    units_and_roles_valid = sum(
        all(case["components"][name]["role"] == ROLE_MAP[name] and case["components"][name]["units"] == UNIT_MAP[name] for name in ROLE_MAP)
        for case in cases
    )
    numerical_qc = {
        "mandatory_valid": numerical_valid, "mandatory_invalid": numerical_invalid,
        "primary_topology_valid": sum(case["mandatory_audit"]["primary_topology_pass"] for case in cases),
        "independent_topology_valid": sum(case["mandatory_audit"]["independent_topology_pass"] for case in cases),
        "derivative_a_b_valid": sum(case["mandatory_audit"]["derivative_pass"] for case in cases),
        "continuum_a_b_valid": sum(case["mandatory_audit"]["continuum_pass"] for case in cases),
        "sign_and_uncertainty_valid": sum(case["mandatory_audit"]["uncertainty_and_sign_pass"] for case in cases),
        "exact_component_closure": sum(case["component_closure"]["exact_particlewise_identity"] for case in cases),
        "units_and_roles_valid": units_and_roles_valid,
        "precision_diagnostic_topology_modes": dict(sorted(Counter(case["precision_diagnostic_topology_mode"] for case in cases).items())),
        "source_hash_audit_pass": all(item["match"] for item in metadata["source_hash_audit"]),
    }
    release_gates = {
        "exact_case_count": len(cases) == 512,
        "exact_family_balance": counts == Counter({"F1": 128, "F2": 128, "F3": 128, "F4": 128}),
        "unique_canonical_ids": len(set(ids)) == 512,
        "deterministic_registry_replay": replay_match,
        "all_archive_hashes_match": archive_qc["all_archive_hashes_match"],
        "archive_schemas_exact": archive_qc["archive_schema_exact"],
        "identifier_alignment_exact": archive_qc["identifier_alignment_exact"],
        "reference_firewall": archive_qc["observable_reference_path_sets_disjoint"] and observable_index["reference_in_model_input"] is False and reference_index["eligible_as_model_input"] is False,
        "all_mandatory_cases_valid_or_retained": numerical_valid + numerical_invalid == 512,
        "all_mandatory_cases_numerically_valid": numerical_valid == 512,
        "topology_valid": numerical_qc["primary_topology_valid"] == numerical_qc["independent_topology_valid"] == 512,
        "component_closure_exact": numerical_qc["exact_component_closure"] == 512 and archive_qc["maximum_particlewise_component_closure_residual"] == 0.0,
        "units_roles_valid": units_and_roles_valid == 512,
        "target_sign_valid": all(value == 0.0 for value in archive_qc["maximum_positive_additive_sign_residual"].values()),
        "observable_descriptors_finite": archive_qc["observable_nonfinite_element_count"] == 0,
        "no_missing_frozen_fields": not archive_qc["observable_missing_fields"] and not archive_qc["reference_missing_fields"],
        "matched_disorder_support_blocks": matched_qc["exact_support_disorder_cartesian_blocks"],
        "normalization_observable_only_and_not_fitted": observable_index["normalization_source"] == "frozen_dimensional_scales_and_prescribed_case_parameters_only" and observable_index["dataset_fitted_standardization_created"] is False,
        "source_hash_audit": numerical_qc["source_hash_audit_pass"],
    }
    fail_unless(all(release_gates.values()), "one or more DDO-01D release gates failed")
    audit = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01D", "generated_date": "2026-08-11",
        "audit_scope": "independent archive reopening, hash recomputation, schema/firewall, CA-01 summaries, sign and closure, and observable-only descriptor QC",
        "design_qc": {"case_count": len(cases), "family_counts": dict(sorted(counts.items())), "unique_canonical_ids": len(set(ids)), "deterministic_registry_replay_match": replay_match, "axis_balance": registry["axis_balance"]},
        "matched_block_qc": matched_qc, "numerical_qc": numerical_qc, "archive_qc": archive_qc,
        "release_gates": release_gates,
        "prohibited_analyses_not_performed": metadata["controls"],
        "terminal_status": "DDO01D_MECHANISM_STRATIFIED_ANALYTICAL_ATLAS_QUALIFIED",
    }
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    render_reports(audit, registry, metadata)
    MANIFEST_PATH.write_text(json.dumps(make_manifest(audit), indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal_status": "DDO01D_MECHANISM_STRATIFIED_ANALYTICAL_ATLAS_QUALIFIED",
        "manifest_sha256": sha256(MANIFEST_PATH), "release_audit_sha256": sha256(AUDIT_PATH),
        "mandatory_valid": numerical_valid, "mandatory_invalid_retained": numerical_invalid,
        "observable_archives": archive_qc["observable_archive_count"], "reference_archives": archive_qc["reference_archive_count"],
        "globally_degenerate_observable_channels": archive_qc["observable_globally_degenerate_channels"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
