#!/usr/bin/env python3
"""Build target-free DDO-01E lineage folds and formal particle samples."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))

from h3_identifiability_semantics import (  # noqa: E402
    CONSTANT_EXCLUDED, CONTENT_LAYERS, LAYER_FIELDS, assign_diagnostic_folds,
    content_fields, field_lineage_id, lineage_payload, selected_particle_ids,
)


CA05_PATH = ROOT / "06_manifests/ca05_manifest.json"
REGISTRY_PATH = ROOT / "06_manifests/ddo01d_case_registry.json"
PARTITION_PATH = ROOT / "06_manifests/ddo01e_diagnostic_partition.json"
SAMPLE_PATH = ROOT / "06_manifests/ddo01e_particle_sample_registry.json"
CA05_SHA256 = "633fdbfa14868f27920cfb0814367370d6da90df1dbe03132f73a82174fdec7d"
REGISTRY_SHA256 = "b4365cd02cd56d917282a490712247a3a287ce405261c4e80c474cc09739d1df"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    if PARTITION_PATH.exists() or SAMPLE_PATH.exists():
        raise RuntimeError("DDO-01E target-free registries already exist; refusing replacement")
    if sha256(CA05_PATH) != CA05_SHA256 or sha256(REGISTRY_PATH) != REGISTRY_SHA256:
        raise RuntimeError("frozen CA-05 or DDO-01D registry hash mismatch")
    ca05 = json.loads(CA05_PATH.read_text())
    registry = json.loads(REGISTRY_PATH.read_text())
    if ca05["terminal_status"] != "DDO_CA05_H3_H4_IDENTIFIABILITY_LOCALITY_SEMANTICS_FROZEN":
        raise RuntimeError("CA-05 is not frozen")
    cases = registry["cases"]
    folds = assign_diagnostic_folds(cases)
    partition_cases = []
    lineages: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        case_id = case["canonical_case_id"]
        lineage = field_lineage_id(case)
        lineages[lineage].append(case_id)
        partition_cases.append({
            "case_index": case["case_index"], "canonical_case_id": case_id,
            "macro_family": case["macro_family"], "field_lineage_id": lineage,
            "field_lineage_payload": lineage_payload(case),
            "diagnostic_fold": f"DIAGNOSTIC_FOLD_{folds[case_id]}",
            "f4_matched_block_id": case.get("f4_matched_block_id"),
            "data_role": "DEVELOPMENT_ATLAS",
        })
    lineage_folds = defaultdict(set)
    for case in partition_cases:
        lineage_folds[case["field_lineage_id"]].add(case["diagnostic_fold"])
    overlaps = {lineage: sorted(values) for lineage, values in lineage_folds.items() if len(values) != 1}
    f4_groups = defaultdict(set)
    for case in partition_cases:
        if case["macro_family"] == "F4":
            f4_groups[case["f4_matched_block_id"]].add(case["field_lineage_id"])
    f4_failures = {block: sorted(values) for block, values in f4_groups.items() if len(values) != 1}
    fold_counts = Counter(case["diagnostic_fold"] for case in partition_cases)
    family_fold_counts = defaultdict(Counter)
    for case in partition_cases:
        family_fold_counts[case["macro_family"]][case["diagnostic_fold"]] += 1
    partition = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "generated_date": "2026-08-11", "registry_status": "FROZEN_BEFORE_H3_H4_TARGET_ANALYSIS",
        "ca05_manifest_sha256": CA05_SHA256, "ddo01d_case_registry_sha256": REGISTRY_SHA256,
        "selection_is_target_free": True, "partition_role": "DIAGNOSTIC_DEVELOPMENT_FOLDS_ONLY",
        "fold_count": 5, "case_count": len(partition_cases), "lineage_count": len(lineages),
        "fold_case_counts": dict(sorted(fold_counts.items())),
        "family_fold_case_counts": {family: dict(sorted(counts.items())) for family, counts in sorted(family_fold_counts.items())},
        "lineage_overlap_audit": {"overlap_count": len(overlaps), "overlaps": overlaps, "pass": not overlaps},
        "f4_matched_block_audit": {"block_count": len(f4_groups), "failure_count": len(f4_failures), "failures": f4_failures, "pass": not f4_failures},
        "content_sets": {name: {"layers": list(CONTENT_LAYERS[name]), "source_fields": list(content_fields(name))} for name in ("C0", "C1", "C2", "C3")},
        "source_field_layers": {name: list(fields) for name, fields in LAYER_FIELDS.items()},
        "constant_current_atlas_metric_exclusions": {name: "CONSTANT_IN_CURRENT_ATLAS_EXCLUDED_FROM_METRIC" for name in CONSTANT_EXCLUDED},
        "cases": partition_cases,
    }
    sample_cases = []
    for case in cases:
        case_id = case["canonical_case_id"]
        particle_count = int(case["resolution_per_axis"]) ** 2
        selected = selected_particle_ids(case_id, particle_count)
        sample_cases.append({
            "case_index": case["case_index"], "canonical_case_id": case_id,
            "field_lineage_id": field_lineage_id(case),
            "diagnostic_fold": f"DIAGNOSTIC_FOLD_{folds[case_id]}",
            "particle_count_available": particle_count, "sample_count": 128,
            "particle_ids": selected, "particle_ids_sha256": canonical_hash(selected),
        })
    sample = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-01E",
        "generated_date": "2026-08-11", "registry_status": "FROZEN_BEFORE_H3_H4_TARGET_ANALYSIS",
        "ca05_manifest_sha256": CA05_SHA256, "diagnostic_case_count": len(sample_cases),
        "sample_count_per_case": 128, "total_formal_particle_samples": 128 * len(sample_cases),
        "selection_is_target_free": True,
        "selection_rule": "SHA-256 rank of DDO01E|PARTICLE|canonical_case_id|particle_id; first 128 unique IDs",
        "full_particle_archives_unchanged": True, "cases": sample_cases,
    }
    PARTITION_PATH.write_text(json.dumps(partition, indent=2, sort_keys=True) + "\n")
    SAMPLE_PATH.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "partition_sha256": sha256(PARTITION_PATH), "particle_sample_sha256": sha256(SAMPLE_PATH),
        "case_count": len(partition_cases), "lineage_count": len(lineages),
        "fold_case_counts": dict(sorted(fold_counts.items())), "lineage_overlap_count": len(overlaps),
        "f4_block_failure_count": len(f4_failures), "formal_particle_samples": 128 * len(sample_cases),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
