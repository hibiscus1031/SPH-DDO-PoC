#!/usr/bin/env python3
"""Audit and bind the complete non-neural DDO-01E release."""

from __future__ import annotations

import hashlib
import json
import py_compile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/identifiability"
CHECKPOINT_MANIFEST = DATA / "ddo01e_checkpoint_manifest.json"
AUDIT_PATH = DATA / "ddo01e_release_audit.json"
MANIFEST_PATH = ROOT / "06_manifests/ddo01e_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    if any(path.exists() for path in (AUDIT_PATH, MANIFEST_PATH)):
        raise RuntimeError("one or more final release binding outputs already exist")
    metrics_path = DATA / "ddo01e_metrics.json"
    verdicts_path = DATA / "ddo01e_formal_verdicts.json"
    subspace_path = DATA / "ddo01e_target_subspace_diagnostic.json"
    firewall_path = DATA / "ddo01e_firewall_audit.json"
    metrics = json.loads(metrics_path.read_text())
    verdicts = json.loads(verdicts_path.read_text())
    subspace = json.loads(subspace_path.read_text())
    firewall = json.loads(firewall_path.read_text())
    partition = json.loads((ROOT / "06_manifests/ddo01e_diagnostic_partition.json").read_text())
    sample = json.loads((ROOT / "06_manifests/ddo01e_particle_sample_registry.json").read_text())

    checkpoints = sorted((DATA / "checkpoints").glob("*.json"))
    checkpoint_items = [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in checkpoints]
    require(len(checkpoint_items) == 80, "expected exactly 80 fold checkpoints")
    CHECKPOINT_MANIFEST.write_text(json.dumps({
        "schema_version": "1.0", "stage": "DDO-01E", "checkpoint_count": 80,
        "expected_grid": "4 content sets x 4 locality levels x 5 folds",
        "files": checkpoint_items,
    }, indent=2, sort_keys=True) + "\n")

    scripts = [
        "08_scripts/h3_identifiability_semantics.py", "08_scripts/h4_locality_semantics.py",
        "08_scripts/test_h3_h4_semantics.py", "08_scripts/ddo01e_partition_builder.py",
        "08_scripts/ddo01e_feature_builder.py", "08_scripts/ddo01e_non_neural_analysis.py",
        "08_scripts/ddo01e_target_subspace.py", "08_scripts/ddo01e_reporting.py",
        "08_scripts/ddo01e_figures.py", "08_scripts/ddo01e_release_audit.py",
    ]
    for relative in scripts:
        py_compile.compile(str(ROOT / relative), doraise=True)

    figure_stems = (
        "identifiability_ladder", "locality_ladder", "consistency_ablation",
        "disorder_stratified_ambiguity", "family_stratified_metrics",
    )
    figure_qc = {}
    for stem in figure_stems:
        svg = ROOT / f"figures/ddo01e/{stem}.svg"
        pdf = ROOT / f"figures/ddo01e/{stem}.pdf"
        tiff = ROOT / f"figures/ddo01e/{stem}.tiff"
        png = ROOT / f"figures/ddo01e/{stem}.png"
        require(all(path.exists() for path in (svg, pdf, tiff, png)), f"missing figure export: {stem}")
        text_nodes = svg.read_text(errors="replace").count("<text")
        reader = PdfReader(str(pdf))
        with Image.open(tiff) as image:
            tiff_qc = {"mode": image.mode, "size": list(image.size), "dpi": [float(value) for value in image.info.get("dpi", (0, 0))]}
        require(text_nodes > 0 and len(reader.pages) == 1, f"vector figure QA failed: {stem}")
        require(tiff_qc["mode"] == "RGB" and min(tiff_qc["dpi"]) >= 599.9, f"TIFF QA failed: {stem}")
        figure_qc[stem] = {"svg_text_nodes": text_nodes, "pdf_pages": len(reader.pages), "tiff": tiff_qc}

    required_reports = [
        "07_reports/ddo01e_semantic_precheck.md", "07_reports/ddo01e_identifiability_report.md",
        "07_reports/ddo01e_locality_report.md", "07_reports/ddo01e_descriptor_ablation_report.md",
        "07_reports/ddo01e_disorder_mechanism_report.md", "07_reports/ddo01e_family_stratified_report.md",
        "07_reports/ddo01e_target_subspace_diagnostic.md", "07_reports/ddo01e_component_h3_h4_ledger.csv",
        "07_reports/ddo01e_firewall_audit.md", "07_reports/ddo01e_next_stage_decision.md",
        "07_reports/ddo01e_figure_contract.md", "07_reports/ddo01e_figure_qa.md",
    ]
    require(all((ROOT / path).exists() for path in required_reports), "missing required report")
    gates = {
        "ca05_frozen": json.loads((ROOT / "06_manifests/ca05_manifest.json").read_text())["terminal_status"] == "DDO_CA05_H3_H4_IDENTIFIABILITY_LOCALITY_SEMANTICS_FROZEN",
        "exact_case_count": partition["case_count"] == 512,
        "zero_lineage_overlap": partition["lineage_overlap_audit"]["pass"],
        "f4_blocks_same_lineage": partition["f4_matched_block_audit"]["pass"],
        "exact_formal_particle_sample": sample["total_formal_particle_samples"] == 65536 and sample["sample_count_per_case"] == 128,
        "formal_grid_complete": len(metrics["results"]) == 16 and len(checkpoints) == 80,
        "formal_verdict_metrics_bound": verdicts["metrics_sha256"] == sha256(metrics_path),
        "formal_verdict_frozen_before_subspace": subspace["formal_verdicts_sha256_before_analysis"] == sha256(verdicts_path),
        "formal_verdict_unchanged": sha256(verdicts_path) == "478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e",
        "reference_firewall": firewall["pass"] is True,
        "figure_exports_and_qa": len(figure_qc) == 5,
        "reports_complete": True,
        "scripts_compile": True,
        "terminal_state_consistent": metrics["terminal_status"] == verdicts["terminal_status"] == "DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE",
    }
    require(all(gates.values()), "one or more DDO-01E release gates failed")
    controls = {
        "h5_evaluated": False, "h6_evaluated": False, "sealed_test_created_or_consumed": False,
        "mlp_training": False, "gnn_training": False, "transformer_training": False,
        "optimizer_created": False, "time_integration": False, "rollout": False,
        "solver_in_the_loop": False, "corrected_solver_claim": False,
        "high_resolution_sph_truth": False, "lcdf_03": False, "lcdf_10": False,
        "target_subspace_changed_formal_verdict": False,
    }
    audit = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "generated_date": "2026-08-11", "terminal_status": "DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE",
        "release_gates": gates, "formal_h3": verdicts["formal_h3"], "formal_h4": verdicts["formal_h4"],
        "checkpoint_manifest_sha256": sha256(CHECKPOINT_MANIFEST), "figure_qc": figure_qc,
        "controls": controls,
    }
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")

    base_files = [
        ("00_project_contract/amendments/ca05_h3_h4_identifiability_locality_semantics.md", "prospective_CA05_semantics"),
        ("00_project_contract/amendments/ca05_change_record.md", "CA05_change_record"),
        ("06_manifests/ca05_manifest.json", "frozen_CA05_manifest"),
        ("06_manifests/ca05_synthetic_expected_outputs.json", "CA05_synthetic_expectations"),
        ("06_manifests/ddo01e_diagnostic_partition.json", "target_free_lineage_folds"),
        ("06_manifests/ddo01e_particle_sample_registry.json", "target_free_formal_particle_samples"),
        ("data/identifiability/ddo01e_observable_feature_cache.npz", "observable_only_feature_cache"),
        ("data/identifiability/ddo01e_observable_feature_schema.json", "derived_observable_schema"),
        ("data/identifiability/ddo01e_reference_target_cache.npz", "physically_separate_reference_sample"),
        ("data/identifiability/ddo01e_reference_target_schema.json", "reference_sample_schema"),
        ("data/identifiability/ddo01e_metrics.json", "formal_H3_H4_metrics"),
        ("data/identifiability/ddo01e_non_neural_diagnostics.json", "non_neural_diagnostic_index"),
        ("data/identifiability/ddo01e_non_neural_diagnostics.csv", "case_level_non_neural_diagnostics"),
        ("data/identifiability/ddo01e_formal_verdicts.json", "pre_SVD_frozen_formal_verdicts"),
        ("data/identifiability/ddo01e_target_subspace_diagnostic.json", "post_verdict_target_subspace"),
        ("data/identifiability/ddo01e_figure_source_data.csv", "figure_source_data"),
        ("data/identifiability/ddo01e_firewall_audit.json", "machine_readable_firewall_audit"),
        ("data/identifiability/ddo01e_checkpoint_manifest.json", "transitive_binding_of_80_fold_checkpoints"),
        ("data/identifiability/ddo01e_release_audit.json", "release_audit"),
    ]
    base_files.extend((path, "required_report") for path in required_reports)
    base_files.extend((path, "DDO01E_implementation") for path in scripts)
    for stem in figure_stems:
        for suffix in ("svg", "pdf", "tiff", "png"):
            base_files.append((f"figures/ddo01e/{stem}.{suffix}", f"Python_figure_{suffix}"))
    manifest = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "generated_date": "2026-08-11", "terminal_status": "DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE",
        "hash_algorithm": "SHA-256", "manifest_self_hash": None,
        "manifest_self_hash_policy": "The manifest excludes its own recursively unstable hash.",
        "upstream_bindings": {
            "ddo01d_manifest_sha256": "aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8",
            "ca05_manifest_sha256": "633fdbfa14868f27920cfb0814367370d6da90df1dbe03132f73a82174fdec7d",
            "observable_index_sha256": "99fdf8115e1c2d6280756bcc46edbefc7d52b5f245cc32e308d9100cc4290e53",
            "reference_index_sha256": "c7e7608b269d6f1c3661e3fffb8c5ced430f2a8dc8b3432666fc745d0de483bc",
        },
        "release_summary": {
            "case_count": 512, "formal_particle_samples": 65536, "lineage_count": partition["lineage_count"],
            "diagnostic_folds": 5, "content_locality_combinations": 16, "fold_checkpoints": 80,
            "data_role": "DEVELOPMENT_ATLAS", "reference_in_model_input": False,
            "formal_h3": verdicts["formal_h3"], "formal_h4": verdicts["formal_h4"],
        },
        "release_gates": gates, "controls": controls,
        "authorization": {"h5_architecture_selection_authorized": False, "h6_authorized": False, "neural_training_authorized": False},
        "files": [{"path": path, "sha256": sha256(ROOT / path), "role": role} for path, role in base_files],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal_status": manifest["terminal_status"], "manifest_sha256": sha256(MANIFEST_PATH),
        "release_audit_sha256": sha256(AUDIT_PATH), "bound_file_count": len(manifest["files"]),
        "release_gate_count": len(gates), "release_gates_passed": sum(gates.values()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
