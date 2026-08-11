#!/usr/bin/env python3
"""Synthesize frozen SPH-DDO evidence into the DDO-02Z publication source pack."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "publication"
MAN = ROOT / "06_manifests"
REPORT = ROOT / "07_reports"

SOURCES = {
    "charter": "00_project_contract/ddo_project_charter.md",
    "h1": "06_manifests/ddo01br_manifest.json",
    "h2": "06_manifests/ddo01cr_manifest.json",
    "h2_ledger": "07_reports/ddo01cr_component_h2_ledger.csv",
    "atlas": "06_manifests/ddo01d_manifest.json",
    "atlas_report": "07_reports/ddo01d_atlas_report.md",
    "h3_initial": "data/identifiability/ddo01e_metrics.json",
    "h3_initial_verdict": "data/identifiability/ddo01e_formal_verdicts.json",
    "h3_initial_firewall": "data/identifiability/ddo01e_firewall_audit.json",
    "ablation": "07_reports/ddo01e_descriptor_ablation_report.md",
    "disorder": "07_reports/ddo01e_disorder_mechanism_report.md",
    "subspace": "data/identifiability/ddo01e_target_subspace_diagnostic.json",
    "attribution": "data/ddo02a/attribution_metrics.json",
    "observability": "data/ddo02a/deployment_observability_ledger.csv",
    "ddo02a_manifest": "06_manifests/ddo02a_manifest.json",
    "ca06": "06_manifests/ca06_manifest.json",
    "ca06_dictionary": "06_manifests/ca06_descriptor_dictionary.json",
    "fresh_registry": "06_manifests/ddo02b_case_registry.json",
    "fresh_metadata": "data/ddo02b_atlas/ddo02b_case_metadata.json",
    "fresh_schema": "data/ddo02b_identifiability/ddo02b_observable_feature_schema.json",
    "fresh_metrics": "data/ddo02b_identifiability/ddo02b_metrics.json",
    "fresh_verdict": "data/ddo02b_identifiability/ddo02b_formal_verdicts.json",
    "fresh_audit": "data/ddo02b_identifiability/ddo02b_release_audit.json",
    "fresh_manifest": "06_manifests/ddo02b_manifest.json",
    "historical_boundary": "01_imported_baseline/README.md",
}


def path(key: str) -> Path:
    return ROOT / SOURCES[key]


def sha(value: Path) -> str:
    return hashlib.sha256(value.read_bytes()).hexdigest()


def write(name: str, text: str) -> Path:
    output = PUB / name
    output.write_text(text.strip() + "\n")
    return output


def evidence_row(claim: str, hypothesis: str, component: str, stage: str, status: str,
                 metric: str, threshold: str, result: str, scope: str, prohibited: str,
                 source_key: str) -> dict[str, str]:
    return {
        "claim": claim, "hypothesis": hypothesis, "component": component,
        "evidence_stage": stage, "development_fresh_status": status,
        "metric": metric, "threshold": threshold, "result": result,
        "claim_scope": scope, "prohibited_extrapolation": prohibited,
        "source_artifact": SOURCES[source_key], "sha256": sha(path(source_key)),
    }


def main() -> None:
    PUB.mkdir(exist_ok=True)
    final = json.loads(path("fresh_manifest").read_text())
    if final["terminal_status"] != "ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED":
        raise RuntimeError("permanent route-closure prerequisite missing")
    h1 = json.loads(path("h1").read_text())
    h2 = json.loads(path("h2").read_text())
    old = json.loads(path("h3_initial").read_text())
    fresh = json.loads(path("fresh_metrics").read_text())
    registry = json.loads(path("fresh_registry").read_text())
    fresh_meta = json.loads(path("fresh_metadata").read_text())
    schema = json.loads(path("fresh_schema").read_text())
    attribution = json.loads(path("attribution").read_text())
    if not (registry["case_count"] == 384 and registry["old_ddo01d_lineage_overlap_count"] == 0):
        raise RuntimeError("fresh-evidence registry mismatch")
    if not all(case["mandatory_audit"]["mandatory_case_pass"] for case in fresh_meta["cases"]):
        raise RuntimeError("fresh numerical qualification mismatch")

    components = [
        ("interpolation_density", "interpolation density", "ALGEBRAIC_DIAGNOSTIC"),
        ("density_rate", "density rate", "PRIMARY_DYNAMIC"),
        ("pressure_gradient_acceleration", "pressure gradient", "PRIMARY_DYNAMIC"),
        ("viscosity_laplacian_acceleration", "viscosity Laplacian", "PRIMARY_DYNAMIC"),
        ("total_acceleration", "total acceleration", "DERIVED_DIAGNOSTIC"),
    ]

    # Final H1--H6 componentwise ledger.
    hypothesis_rows = []
    h2_interpretation = {
        "interpolation_density": ("FAIL", "regular F1 scaling scope; algebraic diagnostic"),
        "density_rate": ("PASS", "canonical h/dx=4 support including tested disorder"),
        "pressure_gradient_acceleration": ("PASS_REGULAR_SCOPE_ONLY", "regular F1 scope only"),
        "viscosity_laplacian_acceleration": ("PASS_REGULAR_SCOPE_ONLY", "regular F1 scope only"),
        "total_acceleration": ("PASS_REGULAR_SCOPE_ONLY", "regular F1 scope only; derived diagnostic"),
    }
    for key, label, role in components:
        hypothesis_rows.append({"component": key, "component_role": role, "hypothesis": "H1_SIGNAL",
            "final_status": "PASS", "scope": "qualified DDO-01B-R excited-case scope",
            "interpretation": "defect signal resolved above float64 numerical/reference uncertainty",
            "source_artifact": SOURCES["h1"], "sha256": sha(path("h1"))})
        h2_status, h2_scope = h2_interpretation[key]
        hypothesis_rows.append({"component": key, "component_role": role, "hypothesis": "H2_SCALING",
            "final_status": h2_status, "scope": h2_scope,
            "interpretation": "componentwise systematic spatial-defect scaling; not identifiability",
            "source_artifact": SOURCES["h2"], "sha256": sha(path("h2"))})
        if key in ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration"):
            h3_status = "FAIL_AFTER_FRESH_REQUALIFICATION"; h3_scope = "CA-06 C3/L3 deployable observables; 384 fresh cases"
        elif key == "interpolation_density":
            h3_status = "DIAGNOSTIC_FAIL_NOT_PRIMARY_ROUTE"; h3_scope = "algebraic diagnostic only"
        else:
            h3_status = "NOT_INDEPENDENTLY_EVALUATED"; h3_scope = "derived pressure-plus-viscosity closure diagnostic"
        hypothesis_rows.append({"component": key, "component_role": role, "hypothesis": "H3_IDENTIFIABILITY",
            "final_status": h3_status, "scope": h3_scope,
            "interpretation": "primary deployable-observable mapping failed only where independently tested",
            "source_artifact": SOURCES["fresh_verdict"], "sha256": sha(path("fresh_verdict"))})
        h4_status = "NOT_QUALIFIED" if key != "total_acceleration" else "NOT_APPLICABLE_DERIVED_DIAGNOSTIC"
        hypothesis_rows.append({"component": key, "component_role": role, "hypothesis": "H4_LOCALITY",
            "final_status": h4_status, "scope": "no locality qualification because independent H3 prerequisite was absent",
            "interpretation": "not a global H4 failure", "source_artifact": SOURCES["fresh_verdict"], "sha256": sha(path("fresh_verdict"))})
        for hypothesis in ("H5_REPRESENTATION", "H6_GENERALIZATION"):
            hypothesis_rows.append({"component": key, "component_role": role, "hypothesis": hypothesis,
                "final_status": "NOT_AUTHORIZED", "scope": "project route closed upstream at H3",
                "interpretation": "not evaluated and not failed", "source_artifact": SOURCES["fresh_manifest"],
                "sha256": sha(path("fresh_manifest"))})
    hypothesis_path = PUB / "final_hypothesis_ledger.csv"
    with hypothesis_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(hypothesis_rows[0])); writer.writeheader(); writer.writerows(hypothesis_rows)

    # Cross-stage load-bearing claim matrix.
    rows = []
    h1_labels = {
        "interpolation_density": "interpolation density", "density_rate": "density rate",
        "pressure_gradient_acceleration": "pressure gradient", "viscosity_laplacian_acceleration": "viscosity Laplacian",
        "total_acceleration": "total acceleration",
    }
    for key, value in h1["component_h1"].items():
        rows.append(evidence_row(
            f"{h1_labels[key]} defect signal is resolved above qualified uncertainty", "H1", key, "DDO-01B-R", "FRESH_H1_EVIDENCE",
            "R_c; bootstrap L95_c", "R_c >= 10; L95_c > 5",
            f"R_c={value['R_c']:.7g}; L95_c={value['L95_c']:.7g}; PASS", "frozen excited-case F1 scope",
            "does not establish scaling, identifiability, or learnability", "h1"))
    for key, value in h2["component_h2"].items():
        rows.append(evidence_row(
            f"{h1_labels[key]} has the stated componentwise scaling scope", "H2", key, "DDO-01C-R", "FRESH_H2_EVIDENCE",
            "regular and jitter family gates", "M_family >= 0.75 and C-D > 0 on mandatory tracks",
            value["verdict"], "F1, canonical formal h/dx=4 and stated disorder scope",
            "no fitted convergence order, H3 conclusion, or extrapolation beyond sampled scope", "h2"))
    rows += [
        evidence_row("DDO-01B-R fixed-time references and signals were numerically qualified", "F0", "all", "DDO-01B-R", "FRESH_H1_EVIDENCE",
            "mandatory valid cases; maximum derivative discrepancy; maximum closure residual", "24/24; derivative gates PASS; closure within bound",
            "24/24; 1.776357e-15; 0", "F1 H1 qualification cases", "not a dynamic solver or H2-H6 qualification", "h1"),
        evidence_row("DDO-01C-R scaling evidence was numerically qualified", "F0", "all", "DDO-01C-R", "FRESH_H2_EVIDENCE",
            "mandatory valid cases; admissible log responses", "204/204 and all admissible", "204/204 PASS", "F1 scaling design",
            "not a balanced F1-F4 atlas or H3 evidence", "h2"),
    ]
    rows += [
        evidence_row("The development atlas contains 512 balanced complete cases", "ATLAS_QUALIFICATION", "all", "DDO-01D", "DEVELOPMENT_ATLAS",
            "case and family counts", "512; 128 each F1--F4", "512; F1=F2=F3=F4=128", "static analytical fields", "not sealed/fresh DDO-02B evidence", "atlas_report"),
        evidence_row("All DDO-01D cases passed numerical qualification", "F0", "all", "DDO-01D", "DEVELOPMENT_ATLAS",
            "mandatory valid cases", "512/512", "512/512 PASS", "float64 analytical/SPH fixed-time evaluation", "high-resolution SPH is not truth", "atlas_report"),
        evidence_row("Observable and reference archives were physically separated", "F0_FIREWALL", "all", "DDO-01D", "DEVELOPMENT_ATLAS",
            "reference firewall", "PASS", "PASS", "DDO-01D stored atlas", "reference-free is not automatically deployment-observable", "atlas_report"),
        evidence_row("The first observable representation failed H3", "H3", "three primary components", "DDO-01E", "CONSUMED_DEVELOPMENT_EVIDENCE",
            "formal H3 statuses on 65,536 samples", "all component gates must pass", old["terminal_status"], "512-case development atlas; C3/L3",
            "cannot be replaced by DDO-02A diagnostics", "h3_initial"),
        evidence_row("The initial H3 analysis preserved the observable/reference firewall", "H3_FIREWALL", "all", "DDO-01E", "CONSUMED_DEVELOPMENT_EVIDENCE",
            "observable-source and fold-scaling audit", "PASS", "PASS", "65,536 diagnostic samples", "no deployment-observability claim for DESIGN_ONLY metadata", "h3_initial_firewall"),
        evidence_row("Feature-space coverage was above the formal minimum but H3 still failed", "F3", "three primary components", "DDO-01E", "CONSUMED_DEVELOPMENT_EVIDENCE",
            "C3/L3 coverage", ">=0.90", "0.953 and H3 FAIL", "DDO-01E formal combination", "coverage is not proof of identifiability", "h3_initial"),
        evidence_row("Observable conditional ambiguity is supported", "F4", "primary dynamic components", "DDO-01E", "CONSUMED_DEVELOPMENT_EVIDENCE",
            "DNN tail/Cvar/oracle gates", "CA-05 H3 thresholds", "multiple ambiguity and/or oracle gates failed", "mechanism-stratified development atlas", "not fundamental unlearnability", "h3_initial"),
        evidence_row("Simple consistency descriptors did not rescue disorder ambiguity", "F5", "pressure; viscosity", "DDO-01E", "CONSUMED_DEVELOPMENT_DIAGNOSTIC",
            "F4 C0 versus C1 ablation", "uniform negative ambiguity/error delta required for rescue", "no uniform rescue", "matched F4 blocks", "no independent causal attribution to h/dx or neighbor count", "ablation"),
        evidence_row("Directional augmentation was supported only for a fresh test", "F6", "pressure; viscosity", "DDO-02A", "CONSUMED_DESIGN_EVIDENCE",
            "best DNN-P90 relative reduction", ">=0.10 diagnostic support rule", f"{attribution['rescue_hypotheses']['EQUIVARIANT_DIRECTIONAL']['best_dnn_p90_relative_reduction']:.4f}; SUPPORTED_FOR_FRESH_TEST",
            "16,384 consumed diagnostic samples", "not a new H3 PASS", "attribution"),
        evidence_row("CA-06 froze 30 deployment-compatible expanded descriptors before fresh target evaluation", "PROSPECTIVE_REDESIGN", "all", "CA-06", "PROSPECTIVE_CONTRACT",
            "descriptor count and freeze order", "contract frozen before DDO-02B targets", "30; freeze prerequisite PASS", "C0--C3 deployable ladder",
            "DESIGN_ONLY fields excluded; no retrospective DDO-01E repair", "ca06"),
        evidence_row("DDO-02B used 384 entirely fresh balanced cases", "FRESH_REQUALIFICATION", "all", "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            "case/family counts and lineage overlap", "384; 96 each; overlap=0", "384; 96 each; overlap=0", "new phases and disorder realizations",
            "old 512 cases cannot count as fresh evidence", "fresh_registry"),
        evidence_row("All DDO-02B cases passed numerical qualification", "F0", "all", "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            "mandatory valid cases", "384/384", "384/384 PASS", "fixed-time analytical/SPH evaluation", "no dynamic solver qualification", "fresh_metadata"),
        evidence_row("The fresh observable cache excludes DESIGN_ONLY fields", "FIREWALL", "all", "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            "prohibited fields absent", "kh_max, kh_rms, mode_count, jitter_fraction absent", "PASS", "formal deployable feature cache",
            "does not establish real-solver external validity", "fresh_schema"),
        evidence_row("The DDO-02B release audit passed all frozen release gates", "EVIDENCE_FREEZE", "all", "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            "release gates", "all required gates PASS", "13/13 PASS", "fresh formal evidence release", "not an H5/H6 or solver qualification", "fresh_audit"),
    ]
    for key in ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration"):
        value = fresh["results"]["C3/L3"]["components"][key]
        metric = f"DNN median={value['dnn_median']:.5g}; DNN P90={value['dnn_p90']:.5g}; Cvar upper95={value['cvar_upper95']:.5g}; oracle NRMSE={value['oracle_nrmse']:.5g}"
        rows.append(evidence_row(
            f"Fresh {h1_labels[key]} deployable-observable mapping failed H3", "H3", key, "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            metric, "DNN median<=0.25; P90<=0.60; Cvar upper95<=0.35; NRMSE<=0.50 plus remaining CA-05 gates",
            "H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE", "C3/L3; 49,152 samples across 384 fresh cases",
            "not all defects unlearnable; temporal or other observables untested", "fresh_metrics"))
    degeneracy = schema["descriptor_qc"]["directional_degeneracy_count"]
    denominator = schema["descriptor_qc"]["particle_count"]
    rows += [
        evidence_row("Observable directional frames frequently used the frozen degeneracy fallback", "F6", "all", "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            "degenerate-frame count / exact particle denominator", "eigenvalue-gap fallback <1e-6", f"{degeneracy}/{denominator} ({degeneracy/denominator:.6%})",
            "all particles used to construct DDO-02B descriptors", "not proof that all equivariant approaches fail", "fresh_schema"),
        evidence_row("H4 was not qualified because H3 failed", "H4", "primary dynamic components", "DDO-02B", "FRESH_FORMAL_EVIDENCE",
            "H4 prerequisite", "H3 PASS required", "NOT QUALIFIED", "tested C3 L0--L3 ladder", "do not state that locality globally fails", "fresh_verdict"),
        evidence_row("No neural training was performed because H3 was not met", "H5", "all", "DDO-02B", "PROJECT_CLOSURE",
            "H5 authorization and training controls", "at least one primary H3 PASS required", "authorized=[]; executed=false", "current instantaneous online spatial-DDO route",
            "does not show that neural SPH, GNNs, or Transformers cannot work", "fresh_manifest"),
        evidence_row("Target SVD remains a covariance diagnostic only", "DIAGNOSTIC_BOUNDARY", "target bundle", "DDO-01E", "CONSUMED_DEVELOPMENT_DIAGNOSTIC",
            "first-two covariance concentration", "no identifiability/manifold gate", "~0.999709 overall; no verdict change", "normalized target covariance",
            "do not claim a two-dimensional target manifold", "subspace"),
    ]
    claim_path = PUB / "claim_ledger.csv"
    with claim_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0])); writer.writeheader(); writer.writerows(rows)

    write("failure_taxonomy.md", f"""
# Final failure taxonomy

| Code | Question | Frozen disposition | Evidence boundary |
|---|---|---|---|
| F0 | Numerical/reference implementation uncertainty | Resolved/qualified | DDO-01B-R, DDO-01C-R, DDO-01D and DDO-02B mandatory audits passed. This qualifies the fixed-time analytical reference chain, not a dynamic solver. |
| F1 | Defect signal too weak | Rejected by H1 evidence | Every frozen component passed `R_c >= 10` and `L95_c > 5` over its qualified excited-case scope. |
| F2 | No systematic scaling | Component-dependent | Density rate passed regular and tested-disorder scope; momentum and total passed regular scope only; interpolation density failed regular scaling scope. |
| F3 | Insufficient feature-space coverage | Not sufficient to explain DDO-01E failure | Formal coverage was 0.953 in DDO-01E and 0.936 in DDO-02B, both above 0.90, while H3 failed. Coverage alone is not identifiability. |
| F4 | Observable conditional ambiguity | Supported | DNN-tail, conditional-variance and oracle-error failures persisted componentwise. |
| F5 | Simple consistency descriptors rescue disorder failure | Not supported | F4 C0-versus-C1 ablations showed no uniform pressure/viscosity rescue. |
| F6 | Explicit directional-frame augmentation rescues the route | Not supported as a complete route | DDO-02A justified a fresh test, but DDO-02B still failed all primary H3 gates; fallback occurred for exactly {degeneracy}/{denominator} particle environments. |
| F7 | Expanded deployment-compatible observables identify the defects | Fresh requalification failed | CA-06 was prospectively frozen, then tested on 384 new cases with zero DDO-01D lineage overlap. |

No entry implies that every SPH defect is fundamentally unlearnable, that temporal information cannot help, or that an untested observable/representation must fail.
""")

    write("manuscript_outline.md", """
# Manuscript outline

## Working title

**Resolvable yet non-identifiable: pre-learning qualification of instantaneous SPH discretization-defect correction**

## Core question and conclusion

Question: Is a fixed-time SPH spatial discretization defect identifiable from deployable low-cost observables before introducing a learned correction operator?

Conclusion: Defect resolvability and systematic scaling do not imply observable identifiability. The initial deployable representation failed H3, and a prospectively expanded representation again failed all three primary mappings on 384 entirely fresh cases. The tested instantaneous online spatial-DDO route is therefore closed upstream of neural training.

## Scientific narrative

1. **Fixed-time defect definition.** Define the sampled continuum-minus-semidiscrete spatial operator defect, component signs, and the separation from time-integration error.
2. **Numerical/reference qualification.** Establish analytical/autodifferentiation agreement, topology audits, float64 uncertainty, sign closure, and observable/reference storage separation.
3. **Signal resolvability.** Report H1 ratios and bootstrap lower bounds; reject weak signal as the stopping cause.
4. **Componentwise scaling structure.** Separate density-rate disorder robustness from regular-only momentum/total scaling and interpolation scaling failure.
5. **Mechanism-stratified atlas.** Introduce the balanced F1--F4 512-case development atlas without calling it fresh requalification evidence.
6. **Deployable-observable identifiability.** State the prospective H3 metrics and show initial C3/L3 failure despite qualified coverage.
7. **Failure attribution.** Isolate conditional ambiguity, disorder strata, consistency ablations, directional hypotheses, higher moments and derivative proxies using consumed evidence only.
8. **Prospective redesign.** Describe CA-06, deployment observability classes, excluded DESIGN_ONLY metadata, expanded moment/directional/reconstruction descriptors, and frozen degeneracy rules.
9. **Fresh requalification.** Present 384 new cases, zero lineage overlap, 49,152 samples, component metrics, and repeated H3 failure.
10. **Closure and implications.** Close only the tested instantaneous online-observable route; explain why no H5/H6 or neural experiment was scientifically authorized.

## Abstract skeleton

Motivation: learned SPH corrections are often introduced before testing whether their target is identifiable from deployment-time information. Methods: define and numerically qualify fixed-time component defects, test signal and scaling, then apply prospective non-neural identifiability gates to an initial and a redesigned observable representation. Results: all components were resolvable; scaling was component/disorder dependent; both observable representations failed H3, including the redesigned representation on fresh evidence. Conclusion: pre-learning identifiability is a necessary gate, and the tested route did not satisfy it.

## Claim boundary

Use only the claims enumerated in `claim_ledger.csv`. H4 is not qualified, H5/H6 are not authorized, high-resolution SPH is not truth, and the covariance subspace diagnostic is not a manifold-dimension result.
""")

    write("manuscript_evidence_map.md", """
# Manuscript evidence map

| Narrative section | Load-bearing evidence | Primary source | Planned display |
|---|---|---|---|
| Defect definition | Fixed-time continuum-minus-SPH operator target and firewall | `00_project_contract/ddo_project_charter.md` | Fig. 2, Methods |
| Numerical qualification | H1/H2/atlas/DDO-02B mandatory validity and closure | H1, H2, DDO-01D and DDO-02B manifests | Table 1, supplement |
| Signal resolvability | Five component H1 ratios and bootstrap bounds | `06_manifests/ddo01br_manifest.json` | Fig. 3 |
| Scaling | Component and disorder H2 verdicts | `06_manifests/ddo01cr_manifest.json` | Fig. 4, Table 2 |
| Atlas | 512 cases, balance, F4 matched blocks, firewall | `07_reports/ddo01d_atlas_report.md` | Fig. 5 |
| Initial H3 | 65,536 samples and component gates | `data/identifiability/ddo01e_metrics.json` | Fig. 6 |
| Attribution/redesign | Consistency ablation, DDO-02A diagnostics, observability audit, CA-06 | DDO-01E/DDO-02A reports and CA-06 manifest | Fig. 7 |
| Fresh H3 | 384 cases, zero overlap, 49,152 samples and C3/L3 metrics | DDO-02B registry, metrics and verdict | Fig. 8, Table 3 |
| Closure | H4 prerequisite, H5/H6 authorization state and route status | `06_manifests/ddo02b_manifest.json` | Fig. 1 and Discussion |

Exact metric-to-source hashes are in `claim_ledger.csv`. Manuscript prose must cite that ledger during drafting so that rounded display values never become the authoritative evidence.
""")

    write("methods_source_pack.md", """
# Methods source pack

## Target and component roles

The fixed-time target is `d_h* = R_h L(q*) - L_h(R_h q*)`. It excludes time-integration, next-state and rollout errors. Primary mappings are density rate, pressure-gradient acceleration and viscosity-Laplacian acceleration. Total acceleration is derived as pressure plus viscosity; interpolation density is an algebraic diagnostic.

## Reference qualification

Closed-form manufactured derivatives were checked against an independent automatic-derivative route. Periodic graph topology, repeatability, neighbor permutation, independent geometry reconstruction, compensated accumulation, positive-additive sign convention and component closure were audited. Float32 degradation remained non-gating; the primary uncertainty was float64. High-resolution SPH was never treated as truth.

## H1 and H2

H1 required component signal-to-uncertainty ratio `R_c >= 10` and strict bootstrap lower bound `L95_c > 5`, excluding analytically unexcited cases rather than inserting zeros. H2 used prospectively frozen monotonicity and dispersion gates on refinement and spectral tracks at canonical `h/dx=4`; descriptive slopes were not convergence-order fits.

## Atlas and firewall

The development atlas contained 512 static analytical cases, balanced across F1--F4. Observable and reference archives were physically separated. Reference-minus-low-cost values, analytical derivatives and targets were prohibited inputs. DDO-02A additionally classified fields as runtime-direct, runtime-estimable or design-only.

## H3/H4 semantics

Five folds were separated by field lineage. Exactly 128 SHA-selected particles per case were used. Feature scaling used training-fold median/IQR and excluded zero-IQR channels fold-locally. Exact cKDTree queries used k=5, 10 and 20; fixed ridge/polynomial-ridge and kNN models were diagnostic non-neural oracles. H3 required all frozen DNN, conditional-variance, oracle-error, family-robustness and coverage gates. H4 could be evaluated only after H3 PASS.

## Prospective redesign and fresh test

CA-06 froze 30 reference-free moment, angular, observable-frame and quadratic-reconstruction descriptors. Four DESIGN_ONLY fields were excluded. Frame degeneracy and reconstruction fallbacks were fixed before fresh targets. DDO-02B then generated 384 new cases (96 per family) with new phases/seeds and zero field-lineage overlap with DDO-01D, yielding 49,152 formal samples.

## Reproducibility boundary

All authoritative values and file hashes are enumerated in `claim_ledger.csv` and `06_manifests/ddo02z_final_evidence_manifest.json`. No neural model, optimizer, integrator, rollout, or solver-in-loop experiment belongs in Methods.
""")

    write("results_source_pack.md", f"""
# Results source pack

## Resolvability

All five frozen components passed H1. Signal-to-uncertainty ratios ranged from 2.455e11 to 2.194e12, with bootstrap lower bounds from 2.284e11 to 1.643e12, far above the thresholds of 10 and 5. Numerical uncertainty therefore did not explain subsequent stopping.

## Scaling

Density rate passed refinement and spectral gates in regular and tested jittered scopes. Pressure, viscosity and derived total acceleration passed only the formal regular scope. Interpolation density failed regular scaling. These results establish component/disorder dependence, not identifiability.

## Initial identifiability failure

The 512-case development atlas was numerically qualified and balanced. On 65,536 samples, the first deployable representation failed H3 for all primary components. Formal coverage was 0.953, so inadequate coverage alone was not sufficient to explain the result. Simple consistency additions did not uniformly reduce pressure/viscosity ambiguity in F4 disorder strata.

## Attribution and redesign

Consumed-evidence attribution supported testing observable directional augmentation and component-specific combinations on fresh data; higher moments and derivative proxies remained inconclusive. CA-06 froze the complete expanded representation before fresh target evaluation.

## Fresh requalification

DDO-02B contained 384 complete new cases, 96 per family, with zero field-lineage overlap and 384/384 numerical qualification. The formal set contained 49,152 samples. Density rate had DNN P90 8.202 and oracle NRMSE 0.5481. Pressure gradient had DNN P90 45.54, Cvar upper95 1.070 and NRMSE 1.010. Viscosity Laplacian had DNN median 0.2773, DNN P90 26.88, Cvar upper95 0.4042 and NRMSE 1.049. All failed their frozen H3 gates.

The observable-frame fallback was used for exactly {degeneracy}/{denominator} ({degeneracy/denominator:.2%}) particle environments. This limits the proposed directional rescue but does not rule out all equivariant representations.

## Terminal result

Because all three primary mappings failed fresh H3, H4 was not qualified and no H5 component was authorized. No neural training occurred. The terminal result is `ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED`.
""")

    write("discussion_source_pack.md", """
# Discussion source pack

## Main inference

The evidence separates three questions often conflated in correction modeling: whether a defect is numerically resolvable, whether it changes systematically with discretization parameters, and whether deployment-time observables identify it. The first two can hold while the third fails.

## Mechanistic interpretation within evidence

The H3 failures combine heavy nearest-neighbor disagreement tails, component-dependent conditional variance, poor non-neural oracle error and family sensitivity. Qualified coverage means the failure cannot be reduced to a simple absence of nearby samples. Disorder was important for pressure ambiguity, but support and neighbor-count changes prevent a single-cause claim. Consistency descriptors did not provide a uniform rescue.

## Redesign lesson

Consumed data suggested that directional alignment and component-specific descriptors merited a fresh test. The prospectively frozen expansion nevertheless failed on new lineages. Frequent directional-frame degeneracy is a documented limitation of that specific construction, not evidence against every equivariant method.

## Implications

The result supports an upstream identifiability gate before architecture search. It does not establish that neural SPH is impossible or that defects are intrinsically unlearnable. Temporal history, alternative deployment sensors, boundary-aware variables, latent state, other discretizations and other target definitions remain outside the tested claim.

## Limitations

The evidence is static, two-dimensional, periodic, manufactured-field and operator specific. H2 has component-dependent scope. Diagnostic oracles are deliberately simple and non-neural. H4, H5 and H6 were not reached. No stability, conservation of a learned correction, rollout or solver-improvement claim is available.

## Publication positioning

The contribution is methodological and negative-but-informative: a prospective pre-learning qualification pipeline prevented unsupported model training. The paper should emphasize falsifiable gates, fresh redesign evidence and disciplined closure rather than architecture performance.
""")

    write("cross_paper_relation_memo.md", """
# Cross-paper relation memo: SPH-PIO versus SPH-DDO

## Separate scientific questions

The SPH-PIO paper concerns qualification of a conservative learned-correction route through gradients, optimizer dynamics, training behavior and support failure. The SPH-DDO paper asks an upstream question: whether the fixed-time discretization-defect target is identifiable from low-cost deployment observables before learning. SPH-DDO terminates at identifiability and contains no optimizer or neural-training evidence.

## Shared foundations

Both projects may describe common SPH operators, periodic neighborhoods, kernels and structure-preserving force identities. SPH-DDO imported only a byte-identical static dependency subset. Shared foundations should be cited or cross-referenced, not presented twice as new primary evidence.

## Non-overlap rules

- Do not merge manuscripts automatically.
- Do not reuse SPH-PIO training/optimizer outcomes as SPH-DDO evidence.
- Do not use SPH-DDO H3 failure to reinterpret SPH-PIO architecture results.
- Do not duplicate publication of the same numerical experiment as independent primary evidence.
- Maintain the historical `V2_QUALIFICATION_FAIL` boundary and the limited static inheritance claims.

## Recommended relation statement

“The present study addresses pre-learning observability of a fixed-time SPH defect and is distinct from our separate investigation of a trained conservative correction route. The studies share static SPH foundations but use different primary questions, evidence chains and terminal criteria.”
""")

    write("figure_plan.md", """
# Publication figure source plan

No new scientific result is authorized. Every panel must be reconstructed only from the frozen source artifacts and values in `claim_ledger.csv`.

| Figure | Scientific purpose | Panels/source | Visual guardrail |
|---|---|---|---|
| 1 | Qualification hierarchy and stopping logic | Defect -> F0/H1 -> H2 -> H3 -> conditional H4/H5; final stop at H3 | H4 marked “not qualified”; H5/H6 marked “not authorized”; no neural icon implying training |
| 2 | Defect definition and firewall | Fixed-time operator equation; observable/reference stores; prohibited arrows | High-resolution SPH never shown as truth |
| 3 | H1 signal resolvability | Component R_c and L95_c versus thresholds | Log scale; distinguish unexcited exclusions |
| 4 | H2 scaling structure | Existing refinement/spectral and disorder figures; component scope matrix | Slopes labeled descriptive, not convergence orders |
| 5 | Mechanism-stratified atlas | F1--F4 design, balance, F4 matched blocks | Label all 512 cases development evidence |
| 6 | Initial H3 failure | Existing DDO-01E identifiability/locality panels | Preserve formal thresholds and diagnostic roles |
| 7 | Failure attribution and prospective redesign | Consistency ablation; DDO-02A hypothesis statuses; CA-06 descriptor groups | Attribution labeled consumed development evidence |
| 8 | Fresh requalification and route closure | DDO-02B component metrics/thresholds; 384-case freshness; final status | No favorable metric may hide a failed all-gates verdict |

Supplement: contract chronology, family strata, support-ratio diagnostics, full descriptor dictionary, firewall/QC, target covariance-subspace diagnostic with explicit “no manifold claim” label.

Existing reusable figure sources include `figures/ddo01cr/` and `figures/ddo01e/`. DDO-02B panels should be tabular reconstructions from frozen JSON, not a new analysis.
""")

    write("table_plan.md", """
# Table plan

| Table | Content | Authoritative source |
|---|---|---|
| 1 | Numerical/reference qualification across H1, H2, DDO-01D and DDO-02B | Stage manifests and claim ledger |
| 2 | Componentwise H1--H6 final status and scope | `final_hypothesis_ledger.csv` |
| 3 | Initial versus fresh H3 metrics and thresholds | DDO-01E/DDO-02B metrics |
| 4 | Failure taxonomy F0--F7 | `failure_taxonomy.md` |
| S1 | H1 exact T_c, U_c, R_c and L95_c | DDO-01B-R manifest |
| S2 | H2 family/layout gates and descriptive slopes | DDO-01C-R ledger/report |
| S3 | Atlas family, resolution, support and disorder balance | DDO-01D registry/manifest |
| S4 | Deployment observability classification for every legacy field | DDO-02A ledger |
| S5 | CA-06 descriptor definitions, dimensions, transforms and complexity | CA-06 dictionary |
| S6 | H3/H4 fold-level QC and family-stratified diagnostics | DDO-01E/DDO-02B checkpoints and diagnostics |

Rounding policy: show 3--4 significant digits in the paper, retain full precision in source data, and never use rounded values for gate recomputation.
""")

    write("reviewer_risk_register.md", """
# Reviewer risk register

| Risk/question | Evidence-based response | Prohibited response |
|---|---|---|
| “Does H3 failure prove defects are unlearnable?” | Restrict to the tested instantaneous online observables and operators. | All SPH defects are fundamentally unlearnable. |
| “Why no neural baseline?” | H3 was a prospective upstream prerequisite; architecture search was scientifically unauthorized after repeated failure. | Neural networks or Transformers cannot work. |
| “Was the redesign tested on reused data?” | Design used consumed DDO-01D evidence; qualification used 384 new cases with zero lineage overlap. | Call the old 512 cases fresh evidence. |
| “Were manufactured parameters leaked?” | DESIGN_ONLY kh/mode/jitter metadata were excluded from fresh formal features. | Equate reference-free with deployment-observable. |
| “Does H4 fail?” | H4 was not qualified because H3 did not pass. | H4 globally fails. |
| “Are H5 and H6 negative?” | They were not authorized or evaluated. | H5/H6 failed. |
| “Is the target two-dimensional?” | SVD is an empirical covariance diagnostic and did not affect verdicts. | The target manifold is two-dimensional. |
| “Did frame degeneracy doom all equivariant methods?” | Report the exact fallback statistic as a limitation of this frame construction. | Equivariant GNNs cannot help. |
| “Is high-resolution SPH the reference truth?” | Closed-form/independent continuum derivatives define the reference. | High-resolution SPH is truth. |
| “Does coverage rule out distribution shift?” | Coverage passed the frozen in-atlas gate only. | Coverage proves deployment generalization. |
| “Can results transfer to boundaries or dynamics?” | Boundaries, temporal history, integration and rollout were not tested. | Temporal information cannot help. |
| “Does this duplicate SPH-PIO?” | The papers have distinct questions and primary evidence; shared static foundations are cross-referenced. | Merge training evidence into SPH-DDO. |
| “Do simple oracles understate neural capacity?” | H3 tests observable conditional ambiguity and uses simple oracles as diagnostics; the conclusion is route-specific, not universal capacity. | Claim an architecture-independent impossibility theorem. |
""")

    closure_report = REPORT / "ddo02z_closure_report.md"
    closure_report.write_text(f"""# DDO-02Z route-closure report

## Final status

`SPH_DDO_ONLINE_ROUTE_CLOSED_PUBLICATION_EVIDENCE_FROZEN`

The permanent scientific result `ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED` is preserved. The current instantaneous online spatial-DDO development route is closed. H5-authorized components are empty; neural training, optimizer creation, time integration, rollout, solver-in-loop work and DDO-03 are not authorized.

## Evidence synthesis

H1 passed for all five frozen components over their qualified scopes. H2 was component/disorder dependent. The initial deployable representation failed H3 on the 512-case development atlas. DDO-02A generated design hypotheses without changing that verdict. CA-06 was frozen before new targets, and its 30-descriptor representation was evaluated on 384 entirely fresh balanced cases with zero field-lineage overlap. All three primary mappings again failed H3. H4 therefore remained unqualified; H5/H6 were not authorized.

The frozen directional fallback statistic is exactly `{degeneracy}/{denominator}` particle environments ({degeneracy/denominator:.6%}).

## Closure boundary

Closure applies only to the tested fixed-time, deployment-observable, instantaneous spatial-defect route. It is not a claim about all neural SPH, all observable representations, temporal information, equivariant GNNs, target intrinsic dimension, or high-resolution SPH truth.
""")
    publication_decision = REPORT / "ddo02z_publication_decision.md"
    publication_decision.write_text("""# DDO-02Z publication decision

SPH-DDO is suitable for preparation as a standalone methodological publication centered on pre-learning qualification and disciplined negative evidence. Its core result is that fixed-time defect signal resolvability and systematic scaling did not imply identifiability from the tested deployable observables.

The manuscript must remain separate from SPH-PIO, use the scientific narrative in `publication/manuscript_outline.md`, and preserve the claim ledger. No external references have been fabricated or selected in this source pack; literature review and citations require a separate evidence-based workflow.
""")

    status_ledger = MAN / "ddo02z_final_status_ledger.json"
    status_ledger.write_text(json.dumps({
        "schema_version": "1.0", "stage": "DDO-02Z",
        "terminal_status": "SPH_DDO_ONLINE_ROUTE_CLOSED_PUBLICATION_EVIDENCE_FROZEN",
        "permanent_scientific_status": "ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED",
        "ONLINE_SPATIAL_DDO_ROUTE_CLOSED": True, "H5_AUTHORIZED_COMPONENTS": [],
        "H5_AUTHORIZED": False, "NEURAL_TRAINING_AUTHORIZED": False,
        "NEURAL_TRAINING_EXECUTED": False, "OPTIMIZER_AUTHORIZED": False,
        "TIME_INTEGRATION_AUTHORIZED": False, "TIME_INTEGRATION_EXECUTED": False,
        "ROLLOUT_AUTHORIZED": False, "ROLLOUT_EXECUTED": False,
        "SOLVER_IN_LOOP_AUTHORIZED": False, "SOLVER_DEVELOPMENT_AUTHORIZED": False,
        "DDO03_AUTHORIZED": False, "development_frozen": True,
        "new_descriptors_created_in_ddo02z": False, "new_field_lineages_created_in_ddo02z": False,
        "new_numerical_targets_created_in_ddo02z": False, "new_h3_analysis_performed_in_ddo02z": False,
        "new_models_or_architectures_created_in_ddo02z": False,
    }, indent=2, sort_keys=True) + "\n")

    publication_files = sorted(PUB.glob("*"))
    source_files = [path(key) for key in SOURCES]
    generated_files = publication_files + [closure_report, publication_decision, status_ledger,
        ROOT / "08_scripts/ddo02z_publication_freeze.py"]
    manifest = {
        "schema_version": "1.0", "project": "SPH-DDO-PoC", "stage": "DDO-02Z",
        "terminal_status": "SPH_DDO_ONLINE_ROUTE_CLOSED_PUBLICATION_EVIDENCE_FROZEN",
        "permanent_scientific_status": "ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED",
        "hash_algorithm": "SHA-256", "manifest_self_hash": None,
        "manifest_self_hash_policy": "self hash excluded; ddo02z_final_sha256.txt records the post-write manifest hash",
        "publication_file_count": len(publication_files), "claim_ledger_row_count": len(rows),
        "hypothesis_ledger_row_count": len(hypothesis_rows),
        "frozen_source_artifacts": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in source_files],
        "generated_publication_and_closure_artifacts": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in generated_files],
        "final_boolean_states": json.loads(status_ledger.read_text()),
        "controls": {"new_scientific_results": False, "h3_reopened": False, "h5_authorized": False,
            "neural_training": False, "optimizer_evidence": False, "ddo03_created": False,
            "fabricated_references": False, "manuscripts_merged": False},
    }
    manifest_path = MAN / "ddo02z_final_evidence_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    sha_path = MAN / "ddo02z_final_sha256.txt"
    listed = source_files + generated_files + [manifest_path]
    sha_path.write_text("".join(f"{sha(p)}  {p.relative_to(ROOT)}\n" for p in listed))
    print(json.dumps({
        "terminal_status": manifest["terminal_status"], "manifest_sha256": sha(manifest_path),
        "sha256_sidecar_sha256": sha(sha_path), "publication_files": len(publication_files),
        "claim_rows": len(rows), "hypothesis_rows": len(hypothesis_rows),
        "directional_fallback": f"{degeneracy}/{denominator}",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
