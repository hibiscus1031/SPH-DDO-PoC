#!/usr/bin/env python3
"""Freeze CA-06 after DDO-02A and before any DDO-02B target evaluation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/ddo02a"
AMEND = ROOT / "00_project_contract/amendments"
REPORT = ROOT / "07_reports"
MANIFEST = ROOT / "06_manifests"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    a = MANIFEST / "ddo02a_manifest.json"
    if not a.exists() or json.loads(a.read_text()).get("terminal_status") != "DDO02A_FAILURE_ATTRIBUTION_FROZEN":
        raise RuntimeError("DDO-02A must be frozen first")
    ledger = list(csv.DictReader((DATA / "deployment_observability_ledger.csv").open()))
    candidates = list(csv.DictReader((DATA / "candidate_descriptor_dictionary.csv").open()))
    prohibited = [row["field"] for row in ledger if row["classification"] == "DESIGN_ONLY"]
    allowed = [row["field"] for row in ledger if row["classification"] != "DESIGN_ONLY"]
    AMEND.mkdir(parents=True, exist_ok=True)
    contract = AMEND / "ca06_expanded_observable_contract.md"
    contract.write_text("""# CA-06 expanded observable contract

Status: `DDO_CA06_EXPANDED_OBSERVABLE_CONTRACT_FROZEN`

This contract was frozen after DDO-02A and before any fresh DDO-02B reference target was evaluated.

## Deployability and firewall

Formal inputs may use only fields classified `RUNTIME_DIRECT` or `RUNTIME_ESTIMABLE` in the DDO-02A ledger. `obs__kh_max`, `obs__kh_rms`, `obs__mode_count`, and `obs__jitter_fraction` are DESIGN_ONLY and prohibited. No analytical derivative, continuum value, defect, or reference-minus-low-cost quantity may enter a descriptor.

## Content ladder

- C0: deployable geometry/graph scalars G, excluding DESIGN_ONLY fields.
- C1: C0 plus low-cost consistency residuals C.
- C2: C1 plus low-cost physical state and baseline SPH operator values P.
- C3: C2 plus the 30 frozen higher-order moment, observable-frame directional, and local quadratic-reconstruction descriptors listed in `data/ddo02a/candidate_descriptor_dictionary.csv`.

The CA-05 L0--L3 ladder is unchanged: particle, one-hop, unique two-hop, and case-global observable summary. Each C3 descriptor is evaluated at L0 and summarized by mean/std/min/max at L1, L2 and L3.

## Frames and degeneracy

The local O(2) frame is the principal frame of the observable second weighted particle moment. Its first-axis sign is fixed lexicographically from observable geometry and its second axis gives determinant +1. If the normalized eigenvalue gap is below 1e-6, the frame is marked degenerate and deterministically falls back to the global identity frame. Targets may only be transformed by this already-frozen observable frame for equivariant diagnostics.

## Moments and reconstruction

Neighbor weights are exp(-|r/h|^2), normalized per particle. Second-, third- and fourth-order tensor moments, contractions, eigen-invariants, condition number and angular harmonic magnitudes m=1..4 are computed in O(neighbors). Density and velocity use a weighted quadratic basis [x,y,x^2/2,xy,y^2/2]. Rank below 5, nonfinite condition, or condition above 1e12 triggers a retained failure flag; coefficients fall back to zero and residual/condition diagnostics remain present. Scaling uses only frozen physical scales followed by train-fold median/IQR; zero-IQR channels are excluded fold-locally.

## Fresh evidence and gates

DDO-02B contains exactly 384 complete cases, 96 each in F1--F4. Fresh phases are pi/7, 3pi/7 and 5pi/7; fresh disorder seeds are 20260901, 20260907 and 20260913. Exact CA-05 five-fold lineage partition, 128-particle SHA sampling, exact cKDTree, non-neural oracle, bootstrap and H3/H4 thresholds remain unchanged. No old DDO-01D case is formal evidence.
""")
    record = AMEND / "ca06_change_record.md"
    record.write_text("""# CA-06 change record

CA-06 declares a new prospective observable-expansion hypothesis. It does not repair, supersede, or recompute DDO-01E. The permanent DDO-01E negative verdict remains bound. The amendment adds reference-free higher-order particle moments, observable-frame directional channels, and local quadratic derivative proxies; it does not select a neural architecture or authorize H5.
""")
    dictionary = MANIFEST / "ca06_descriptor_dictionary.json"
    dictionary.write_text(json.dumps({
        "schema_version":"1.0", "stage":"CA-06", "descriptor_count":len(candidates),
        "descriptors":candidates, "allowed_existing_observable_fields":allowed,
        "prohibited_design_only_fields":prohibited,
        "content_ladder":{"C0":["G"],"C1":["G","C"],"C2":["G","C","P"],"C3":["G","C","P","EXPANDED"]},
        "locality_ladder":{"L0":"particle","L1":"one-hop","L2":"unique two-hop","L3":"case-global observable summary"},
    }, indent=2, sort_keys=True)+"\n")
    final_report = REPORT / "ca06_final_report.md"
    final_report.write_text("""# CA-06 final report

CA-06 is frozen with 30 exact, reference-free expanded descriptors and an explicitly deployable C0--C3 ladder. All four DESIGN_ONLY legacy fields are excluded. The CA-05 scientific gates and statistical semantics are unchanged. The registry design requires 384 entirely fresh cases with zero field-lineage overlap against DDO-01D. Neural training and H5 remain unauthorized.
""")
    bound = [a, DATA/"deployment_observability_ledger.csv", DATA/"candidate_descriptor_dictionary.csv",
             contract, record, dictionary, final_report]
    manifest = {
        "schema_version":"1.0", "stage":"CA-06", "terminal_status":"DDO_CA06_EXPANDED_OBSERVABLE_CONTRACT_FROZEN",
        "ddo02a_manifest_sha256":sha(a), "frozen_before_ddo02b_target_evaluation":True,
        "descriptor_count":len(candidates), "prohibited_design_only_fields":prohibited,
        "h3_h4_thresholds":"UNCHANGED_CA05", "neural_architecture_selected":False, "h5_authorized":False,
        "bound_files":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in bound],
    }
    out = MANIFEST / "ca06_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"terminal_status":manifest["terminal_status"],"manifest_sha256":sha(out),"descriptor_count":len(candidates)}, indent=2))


if __name__ == "__main__":
    main()
