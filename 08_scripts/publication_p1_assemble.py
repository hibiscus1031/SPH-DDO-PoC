#!/usr/bin/env python3
"""Assemble manuscript v0.1 from frozen SPH-DDO evidence without new analysis."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "publication"

ARTIFACTS = {
    "charter": "00_project_contract/ddo_project_charter.md",
    "defect": "02_defect_definitions/spatial_defect_definition.md",
    "operator": "02_defect_definitions/operator_decomposition.md",
    "h1": "06_manifests/ddo01br_manifest.json",
    "h2": "06_manifests/ddo01cr_manifest.json",
    "atlas": "06_manifests/ddo01d_manifest.json",
    "atlas_report": "07_reports/ddo01d_atlas_report.md",
    "initial_metrics": "data/identifiability/ddo01e_metrics.json",
    "initial_verdict": "data/identifiability/ddo01e_formal_verdicts.json",
    "initial_firewall": "data/identifiability/ddo01e_firewall_audit.json",
    "ablation": "07_reports/ddo01e_descriptor_ablation_report.md",
    "disorder": "07_reports/ddo01e_disorder_mechanism_report.md",
    "subspace": "data/identifiability/ddo01e_target_subspace_diagnostic.json",
    "attribution": "data/ddo02a/attribution_metrics.json",
    "observability": "data/ddo02a/deployment_observability_ledger.csv",
    "ca06": "06_manifests/ca06_manifest.json",
    "ca06_dictionary": "06_manifests/ca06_descriptor_dictionary.json",
    "fresh_registry": "06_manifests/ddo02b_case_registry.json",
    "fresh_metadata": "data/ddo02b_atlas/ddo02b_case_metadata.json",
    "fresh_schema": "data/ddo02b_identifiability/ddo02b_observable_feature_schema.json",
    "fresh_metrics": "data/ddo02b_identifiability/ddo02b_metrics.json",
    "fresh_verdict": "data/ddo02b_identifiability/ddo02b_formal_verdicts.json",
    "fresh_manifest": "06_manifests/ddo02b_manifest.json",
    "final_hypotheses": "publication/final_hypothesis_ledger.csv",
    "failure_taxonomy": "publication/failure_taxonomy.md",
    "final_status": "06_manifests/ddo02z_final_status_ledger.json",
    "cross_paper": "publication/cross_paper_relation_memo.md",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Paragraph:
    claim_id: str
    section: str
    purpose: str
    text: str
    artifact_keys: tuple[str, ...]
    status: str
    permitted: str
    prohibited: str
    citations: tuple[str, ...] = ()

    @property
    def artifact_paths(self) -> str:
        if not self.artifact_keys:
            return "EXTERNAL_CITATION_NOT_YET_SELECTED"
        return ";".join(ARTIFACTS[key] for key in self.artifact_keys)

    @property
    def artifact_hashes(self) -> str:
        if not self.artifact_keys:
            return "N/A"
        return ";".join(sha256(ROOT / ARTIFACTS[key]) for key in self.artifact_keys)

    def annotation(self) -> str:
        return (
            "<!-- EVIDENCE_ANNOTATION\n"
            f"CLAIM_ID: {self.claim_id}\n"
            f"EVIDENCE_ARTIFACT: {self.artifact_paths}\n"
            f"EVIDENCE_SHA256: {self.artifact_hashes}\n"
            f"SCIENTIFIC_STATUS: {self.status}\n"
            f"PERMITTED_WORDING: {self.permitted}\n"
            f"PROHIBITED_EXTRAPOLATION: {self.prohibited}\n"
            "-->"
        )


def main() -> None:
    final = json.loads((ROOT / ARTIFACTS["final_status"]).read_text())
    if final["terminal_status"] != "SPH_DDO_ONLINE_ROUTE_CLOSED_PUBLICATION_EVIDENCE_FROZEN":
        raise RuntimeError("publication evidence is not frozen")
    if final["H5_AUTHORIZED"] or final["NEURAL_TRAINING_EXECUTED"] or final["DDO03_AUTHORIZED"]:
        raise RuntimeError("publication-only boundary mismatch")

    citations = {
        "C01": {
            "placeholder": "[CITATION NEEDED: foundational SPH discretization and consistency errors]",
            "section": "Introduction",
            "topic": "Foundational literature on SPH approximation, consistency, and spatial discretization error",
            "support": "External context for why particle consistency and disorder affect spatial operators",
            "boundary": "Must not be used as evidence for the project-specific H1-H3 results",
        },
        "C02": {
            "placeholder": "[CITATION NEEDED: learned correction operators and data-driven SPH methods]",
            "section": "Introduction",
            "topic": "Peer-reviewed learned-correction and data-driven SPH literature",
            "support": "External context that learned corrections have been proposed for particle methods",
            "boundary": "Must not imply that SPH-DDO trained or compared a neural architecture",
        },
        "C03": {
            "placeholder": "[CITATION NEEDED: identifiability and conditional ambiguity in inverse problems]",
            "section": "Introduction; Discussion",
            "topic": "Identifiability, observability, and conditional ambiguity in inverse problems",
            "support": "External conceptual framing for separating signal, scaling, and identifiability",
            "boundary": "Must not convert empirical H3 failure into an impossibility theorem",
        },
        "C04": {
            "placeholder": "[CITATION NEEDED: equivariant representations for particle and geometric learning]",
            "section": "Prospective redesign; Discussion",
            "topic": "Equivariant and frame-based representations in particle/geometric learning",
            "support": "External context for directional information and frame degeneracy",
            "boundary": "Must not claim that equivariant GNNs were tested or cannot work",
        },
        "C05": {
            "placeholder": "[CITATION NEEDED: preregistration and prospective validation in computational science]",
            "section": "Discussion",
            "topic": "Prospective contracts, fresh validation, and disciplined negative evidence",
            "support": "External methodological context for freezing gates before outcome inspection",
            "boundary": "Must not overstate the present workflow as a universal standard",
        },
    }

    p: list[Paragraph] = []
    def add(claim_id: str, section: str, purpose: str, text: str, keys: tuple[str, ...],
            status: str, permitted: str, prohibited: str, cites: tuple[str, ...] = ()) -> None:
        p.append(Paragraph(claim_id, section, purpose, text, keys, status, permitted, prohibited, cites))

    # Abstract
    add("ABSTRACT-P01", "Abstract", "Question and design",
        "Learned corrections are meaningful only if the correction target is inferable from information available at deployment. Here we ask whether a fixed-time smoothed particle hydrodynamics (SPH) spatial discretization defect can be identified from low-cost instantaneous observables before a learned correction operator is introduced. We qualified the analytical reference, separated signal resolvability from scaling and identifiability, and applied prospectively frozen non-neural H3 gates to an initial and a redesigned observable representation.",
        ("charter", "h1", "h2", "initial_metrics", "ca06", "fresh_metrics"), "FROZEN_SYNTHESIS",
        "State the pre-learning question and the prospective qualification sequence.",
        "Do not imply that neural training, temporal prediction, or solver-in-loop evaluation occurred.")
    add("ABSTRACT-P02", "Abstract", "Principal result",
        "All frozen defect components were resolvable above qualified float64 numerical and reference uncertainty, while spatial scaling was component- and disorder-dependent. The first deployable representation failed H3, and a prospectively expanded representation again failed all three primary dynamic mappings on 384 entirely fresh cases. Thus, a spatial discretization defect can be numerically resolvable and exhibit systematic scaling without being identifiable from the tested deployment-compatible instantaneous observables; no neural training was performed because the upstream H3 prerequisite was not met.",
        ("h1", "h2", "initial_verdict", "fresh_metrics", "fresh_manifest", "final_status"), "FROZEN_CORE_CONCLUSION",
        "Use the exact route-specific conclusion and state why training was not performed.",
        "Do not claim fundamental unlearnability, neural failure, global H4 failure, or H5/H6 failure.")

    # 1 Introduction
    add("INTRO-P01", "1. Introduction", "SPH context",
        "SPH represents continuum fields on moving particles through compact-support kernel approximations, so its spatial operators depend on resolution, support, particle arrangement, and local consistency. These dependencies can produce component-specific spatial discretization defects, particularly when the particle configuration departs from regularity. " + citations["C01"]["placeholder"],
        (), "EXTERNAL_CONTEXT_PENDING_CITATION", "Retain only as literature-supported background after citation verification.",
        "Do not present this paragraph as project evidence or claim universal behavior for all SPH formulations.", ("C01",))
    add("INTRO-P02", "1. Introduction", "Learning context",
        "Data-driven correction operators have been proposed as one route for compensating numerical error in particle and mesh-based solvers. However, architecture selection and optimization cannot resolve a more basic information question: whether the desired correction is determined by quantities that remain available when the model is deployed. " + citations["C02"]["placeholder"],
        (), "EXTERNAL_CONTEXT_PENDING_CITATION", "Use as motivation for an upstream observability test once suitable literature is supplied.",
        "Do not imply that any neural architecture was evaluated in SPH-DDO.", ("C02",))
    add("INTRO-P03", "1. Introduction", "Identifiability distinction",
        "A target may be large relative to numerical uncertainty and may vary systematically with discretization parameters, yet still be conditionally ambiguous given the observable input. This distinction motivates separate tests of signal, scaling, and identifiability rather than treating predictive model fitting as the first qualification step. " + citations["C03"]["placeholder"],
        ("charter",), "FROZEN_PROJECT_LOGIC_WITH_EXTERNAL_CONTEXT", "Separate H1, H2, and H3 as distinct questions.",
        "Do not turn the empirical diagnostics into a general inverse-problem theorem.", ("C03",))
    add("INTRO-P04", "1. Introduction", "Study objective and contribution",
        "We therefore formulate SPH-DDO around the question: is the instantaneous spatial discretization defect of a low-cost SPH operator identifiable from deployment-compatible observables before a learned correction is introduced? The contribution is a prospective evidence chain spanning reference qualification, signal resolvability, componentwise scaling, mechanism-stratified atlas construction, observable identifiability, failure attribution, observable redesign, and fresh requalification. The chain terminates when all three primary dynamic mappings fail fresh H3.",
        ("charter", "final_status"), "FROZEN_PROJECT_SCOPE", "Present the scientific logic and terminal boundary.",
        "Do not describe the work as an architecture comparison, a trained correction method, or SPH-PIO continuation.")

    # 2 Formulation
    add("FORM-P01", "2. Spatial discretization-defect formulation and qualification hierarchy", "Defect definition",
        "For a smooth manufactured continuum state q*(x), continuum spatial operator L, sampling map R_h, and corresponding SPH semi-discrete operator L_h, the fixed-time defect is defined as d_h* = R_h L(q*) - L_h(R_h q*). The sign convention is positive-additive: adding the defect to the low-cost spatial operator recovers the sampled continuum operator within the qualified numerical uncertainty.",
        ("charter", "defect"), "FROZEN_DEFINITION", "Use the frozen fixed-time defect equation and positive-additive sign convention.",
        "Do not include time-integration, next-state, rollout, or division-by-dt error in the target.")
    add("FORM-P02", "2. Spatial discretization-defect formulation and qualification hierarchy", "Component roles",
        "The independently tested primary dynamic components are density rate, pressure-gradient acceleration, and viscosity-Laplacian acceleration. Total acceleration is retained only as the derived pressure-plus-viscosity closure diagnostic, while interpolation density is an algebraic density diagnostic. Component roles remain fixed throughout the qualification chain.",
        ("operator", "final_hypotheses"), "FROZEN_COMPONENT_ROLES", "Distinguish primary mappings from derived and algebraic diagnostics.",
        "Do not report total acceleration as an independently fitted H3 route or interpolation density as a primary dynamic target.")
    add("FORM-P03", "2. Spatial discretization-defect formulation and qualification hierarchy", "Information firewall",
        "Analytical and manufactured information is used only to construct or audit targets. Candidate deployable descriptors, normalization, neighborhood construction, data routing, and diagnostic inputs are prohibited from using reference-minus-low-cost quantities or any equivalent target-derived proxy. Observable and reference fields are stored separately and audited before each identifiability analysis.",
        ("charter", "initial_firewall", "fresh_schema"), "FROZEN_FIREWALL", "State the strict separation of deployable inputs and reference targets.",
        "Do not equate reference-free with deployment-observable or imply that manufactured metadata is automatically deployable.")
    add("FORM-P04", "2. Spatial discretization-defect formulation and qualification hierarchy", "Hypothesis sequence",
        "The hierarchy tests H1 signal resolvability, H2 systematic scaling, H3 observable identifiability, H4 bounded locality conditional on H3, H5 structure-compatible representation conditional on upstream qualification, and H6 generalization. A downstream stage is not interpreted when its prerequisite is absent. In the final ledger, H4 is NOT_QUALIFIED and H5 and H6 are NOT_AUTHORIZED, rather than failed.",
        ("charter", "final_hypotheses", "final_status"), "FROZEN_HYPOTHESIS_GOVERNANCE", "Use the exact final status vocabulary.",
        "Do not collapse NOT_QUALIFIED or NOT_AUTHORIZED into FAIL.")
    add("FORM-P05", "2. Spatial discretization-defect formulation and qualification hierarchy", "Reference hierarchy boundary",
        "Closed-form analytical derivatives are the primary reference and are cross-checked by an independent automatic-differentiation route. Refining the same SPH discretization is not treated as truth. This hierarchy confines the study to analytical fixed-time spatial defects and avoids conflating discretization refinement with an independent continuum reference.",
        ("charter", "h1", "atlas"), "FROZEN_REFERENCE_HIERARCHY", "State the analytical-reference hierarchy and high-resolution-SPH boundary.",
        "Do not claim that high-resolution SPH is truth.")

    # 3 Numerical qualification
    add("NUM-P01", "3. Analytical reference and numerical qualification", "Cross-check methodology",
        "Analytical derivatives and continuum components were independently evaluated and compared under float64 discrepancy gates. The SPH graph was audited for periodic topology, reciprocity, support completeness, and deterministic reconstruction, while repeat evaluation, neighbor permutation, compensated accumulation, sign recovery, and component closure were retained as explicit numerical checks.",
        ("h1", "h2", "atlas", "fresh_metadata"), "FROZEN_METHOD", "Describe only the audits recorded in the frozen stage artifacts.",
        "Do not infer dynamic stability, conservation of a learned correction, or solver convergence.")
    add("NUM-P02", "3. Analytical reference and numerical qualification", "Early-stage numerical results",
        "All 24 fresh H1 cases passed the mandatory analytical, topology, uncertainty, sign, and closure audits; the maximum analytical-route derivative discrepancy was 1.776357e-15 and the maximum component-closure residual was zero. All 204 fresh H2 cases likewise passed mandatory qualification, with a maximum derivative discrepancy of 1.421086e-14 and admissible formal log responses throughout.",
        ("h1", "h2"), "FROZEN_QUALIFIED_RESULT", "Report the exact H1/H2 numerical qualification counts and discrepancies.",
        "Do not treat these cases as balanced F1-F4 H3 evidence.")
    add("NUM-P03", "3. Analytical reference and numerical qualification", "Atlas numerical results",
        "The 512-case DDO-01D development atlas passed numerical qualification without post-target replacement or failure deletion. Its observable and reference-target archives were physically separated, and no empirical target normalization based on fitted powers of h was created.",
        ("atlas", "atlas_report"), "FROZEN_DEVELOPMENT_ATLAS_QUALIFICATION", "State 512/512 qualification and storage separation.",
        "Do not call the DDO-01D cases fresh DDO-02B requalification evidence.")
    add("NUM-P04", "3. Analytical reference and numerical qualification", "Fresh numerical results",
        "All 384 DDO-02B cases passed the same fixed-time mandatory numerical qualification before formal H3 aggregation. The release audit passed all 13 frozen gates, and the fresh observable feature schema records that no reference archive was opened during observable feature construction.",
        ("fresh_metadata", "fresh_schema", "fresh_manifest"), "FROZEN_FRESH_QUALIFICATION", "State 384/384 validity, firewall preservation, and release completion.",
        "Do not interpret release qualification as H3, H5, rollout, or solver qualification.")

    # 4 Signal
    add("SIGNAL-P01", "4. Signal resolvability", "H1 semantics",
        "H1 compares a componentwise target scale T_c with qualified numerical/reference uncertainty U_c through R_c = T_c/U_c and a stratified bootstrap lower bound L95_c. The frozen criteria require R_c >= 10 and strictly L95_c > 5; analytically unexcited component-case pairs are excluded rather than inserted as zeros.",
        ("h1",), "FROZEN_H1_METHOD", "State the frozen H1 thresholds and unexcited-case rule.",
        "Do not redefine H1 using average target magnitude or include unexcited zeros.")
    add("SIGNAL-P02", "4. Signal resolvability", "H1 component results",
        "All five frozen components passed H1 over their qualified excited-case scopes. R_c ranged from 2.455e11 for interpolation density to 2.194e12 for pressure-gradient acceleration, and L95_c ranged from 2.284e11 to 1.643e12. These margins place the fixed-time defects far above the qualified float64 uncertainty floor.",
        ("h1",), "FROZEN_H1_PASS", "Report componentwise H1 PASS and the frozen numerical range.",
        "Do not infer scaling, identifiability, learnability, or deployment performance from H1.")
    add("SIGNAL-P03", "4. Signal resolvability", "Failure-taxonomy implication",
        "The H1 evidence rejects insufficient signal amplitude as the reason that the project later stopped. It does not establish that the same signals are uniquely determined by deployable observables; that question remains H3 and requires separate evidence.",
        ("h1", "failure_taxonomy"), "FROZEN_INTERPRETATION", "State that weak signal was rejected within the tested scopes and distinguish H1 from H3.",
        "Do not describe H1 PASS as proof of predictability.")

    # 5 Scaling
    add("SCALE-P01", "5. Componentwise scaling and disorder sensitivity", "H2 design",
        "H2 was evaluated prospectively on refinement and spectral tracks at the canonical formal support ratio h/dx = 4. Formal decisions used monotonicity and dispersion gates; reported local slopes were descriptive and were not fitted convergence orders.",
        ("h2",), "FROZEN_H2_METHOD", "State the frozen H2 design and decision variables.",
        "Do not report descriptive slopes as universal convergence orders.")
    add("SCALE-P02", "5. Componentwise scaling and disorder sensitivity", "Density scaling",
        "Density rate passed the refinement and spectral gates in both regular and tested jittered scopes, yielding H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT. Within the frozen design, density rate therefore retained systematic scaling under the tested disorder perturbation.",
        ("h2",), "FROZEN_H2_PASS", "Restrict density-rate scaling to the frozen F1 and canonical-support scope.",
        "Do not extrapolate to all disorder types, support ratios, boundaries, or H3 identifiability.")
    add("SCALE-P03", "5. Componentwise scaling and disorder sensitivity", "Momentum scaling",
        "Pressure-gradient acceleration, viscosity-Laplacian acceleration, and the derived total acceleration passed the formal regular scope but failed the jitter refinement requirement. Their final H2 status is therefore regular-scope-only, consistent with a component- and disorder-dependent scaling structure.",
        ("h2",), "FROZEN_H2_REGULAR_ONLY", "Use regular-scope-only wording for pressure, viscosity, and total acceleration.",
        "Do not claim disorder-robust momentum scaling or a common component exponent.")
    add("SCALE-P04", "5. Componentwise scaling and disorder sensitivity", "Interpolation scaling and boundary",
        "Interpolation density failed the regular and jitter scaling scopes and remains an algebraic diagnostic. Taken together, the H2 results show that systematic scaling is neither uniform across components nor sufficient to establish H3.",
        ("h2", "final_hypotheses"), "FROZEN_H2_FAIL_DIAGNOSTIC", "State interpolation H2 failure and the componentwise H2 conclusion.",
        "Do not infer that interpolation H2 failure forces H3 failure in another component.")

    # 6 Atlas
    add("ATLAS-P01", "6. Mechanism-stratified analytical defect atlas", "Atlas purpose",
        "A mechanism-stratified analytical atlas was constructed to expose identifiability to multiple spatial-defect mechanisms rather than to a single refinement track. The exact registry was frozen before target evaluation and contained 512 complete static cases balanced as F1 = F2 = F3 = F4 = 128.",
        ("atlas", "atlas_report"), "FROZEN_ATLAS_DESIGN", "State the prospective registry and exact balance.",
        "Do not imply that the atlas itself evaluated H3 or constituted a sealed test.")
    add("ATLAS-P02", "6. Mechanism-stratified analytical defect atlas", "Family structure",
        "The families span single-mode, multimode, directional/mechanism, and controlled-disorder configurations under the frozen analytical-field specification. F4 includes matched blocks across support ratio and disorder, retaining difficult strata without failure deletion.",
        ("atlas", "atlas_report", "disorder"), "FROZEN_ATLAS_SCOPE", "Describe the mechanism and matched-block organization at the frozen level.",
        "Do not attribute an independent causal effect to support ratio or neighbor count when they co-vary.")
    add("ATLAS-P03", "6. Mechanism-stratified analytical defect atlas", "Evidence role",
        "DDO-01D is permanently labeled DEVELOPMENT_ATLAS and later CONSUMED_OBSERVABLE_DESIGN_EVIDENCE. Its 512 cases support initial identifiability analysis and redesign attribution, but they cannot be relabeled as fresh formal requalification evidence.",
        ("atlas", "final_status"), "FROZEN_DATA_ROLE", "Maintain the development/consumed role of all 512 cases.",
        "Do not count DDO-01D cases toward the DDO-02B fresh quota.")
    add("ATLAS-P04", "6. Mechanism-stratified analytical defect atlas", "Atlas claim boundary",
        "The atlas qualifies construction, balance, numerical validity, descriptor availability, and the reference firewall. It does not by itself establish predictability, locality, representation suitability, target manifold dimension, or solver improvement.",
        ("atlas_report",), "FROZEN_CLAIM_BOUNDARY", "Use the atlas only for its qualified design and data roles.",
        "Do not claim H3-H6, manifold structure, training success, or solver correction from atlas construction.")

    # 7 Initial identifiability
    add("ID-P01", "7. Deployable-observable identifiability", "H3 operational question",
        "H3 asks whether particles that are close in a deployment-compatible observable space also have sufficiently similar defects, and whether simple fixed non-neural oracles can predict held-out field lineages. The formal diagnostics combine nearest-neighbor target disagreement, conditional target variance, oracle NRMSE and improvement, family robustness, and feature-space coverage.",
        ("initial_metrics",), "FROZEN_H3_METHOD", "Describe the preregistered H3 diagnostic classes without presenting them as production models.",
        "Do not call kNN, ridge, or polynomial ridge trained correction architectures.")
    add("ID-P02", "7. Deployable-observable identifiability", "Partition and preprocessing",
        "The initial analysis used 65,536 SHA-selected particle samples from the 512-case development atlas. Five folds were separated by field lineage, feature scaling was fitted only on each training fold using median and interquartile range, and zero-IQR channels were excluded fold-locally.",
        ("initial_metrics", "initial_firewall"), "FROZEN_INITIAL_H3_EXECUTION", "State sample count, lineage isolation, and train-only preprocessing.",
        "Do not describe the development evidence as fresh DDO-02B evidence.")
    add("ID-P03", "7. Deployable-observable identifiability", "Initial component result",
        "At the formal C3/L3 combination, density rate, pressure-gradient acceleration, and viscosity-Laplacian acceleration all received H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE. Favorable averages in selected diagnostics did not override failed tail, conditional-variance, oracle, or family gates because H3 required all frozen criteria.",
        ("initial_metrics", "initial_verdict"), "FROZEN_INITIAL_H3_FAIL", "Report the componentwise all-gates verdict.",
        "Do not recompute a favorable replacement score or describe H3 failure as fundamental unlearnability.")
    add("ID-P04", "7. Deployable-observable identifiability", "Coverage and ambiguity",
        "Formal feature-space coverage was approximately 0.953, above the 0.90 minimum, while H3 still failed. Insufficient coverage was therefore not a sufficient explanation for the initial result; the evidence instead supported observable conditional ambiguity through component-specific disagreement tails, variance, and oracle failures.",
        ("initial_metrics", "failure_taxonomy"), "FROZEN_FAILURE_ATTRIBUTION_BOUNDARY", "State that coverage passed but did not remove conditional ambiguity.",
        "Do not claim that coverage proves deployment generalization or that one ambiguity metric alone proves impossibility.")
    add("ID-P05", "7. Deployable-observable identifiability", "Consistency and target-subspace boundaries",
        "Within matched F4 blocks, adding simple consistency descriptors did not uniformly reduce pressure or viscosity ambiguity across disorder strata. A post-verdict target SVD remained a covariance diagnostic only and did not alter the formal H3 result or establish a two-dimensional physical manifold.",
        ("ablation", "subspace"), "FROZEN_DIAGNOSTIC_BOUNDARY", "Report no uniform consistency rescue and preserve the SVD diagnostic label.",
        "Do not claim a two-dimensional target manifold or use target coordinates as inputs.")

    # 8 Redesign and fresh
    add("REDESIGN-P01", "8. Prospective observable redesign and fresh requalification", "Attribution role",
        "DDO-02A used the consumed 512-case evidence only to diagnose why the initial representation failed; it was not an H3 requalification. Directional/equivariant augmentation and component-specific combinations were supported for a fresh test, whereas higher-order moments and derivative proxies were individually inconclusive.",
        ("attribution",), "FROZEN_CONSUMED_ATTRIBUTION", "Use the diagnostic statuses only to motivate prospective testing.",
        "Do not present DDO-02A reductions as a new H3 PASS.")
    add("REDESIGN-P02", "8. Prospective observable redesign and fresh requalification", "Deployment observability",
        "The redesign distinguished runtime-direct, runtime-estimable, and design-only information. The manufactured-wave fields kh_max, kh_rms, mode_count, and jitter_fraction were classified as DESIGN_ONLY and excluded from the future formal deployable feature set.",
        ("observability", "ca06"), "FROZEN_DEPLOYMENT_AUDIT", "Name the four prohibited design-only fields and their exclusion.",
        "Do not assume that any reference-free field is deployment-observable.")
    add("REDESIGN-P03", "8. Prospective observable redesign and fresh requalification", "Expanded representation",
        "CA-06 prospectively froze 30 reference-free descriptors spanning weighted second- to fourth-order particle moments, angular harmonics, observable-frame directional channels, and local quadratic reconstruction proxies. Dimensions, normalization, transformation behavior, conditioning, failure flags, context aggregation, and frame-degeneracy fallback were fixed before any fresh target was evaluated. " + citations["C04"]["placeholder"],
        ("ca06", "ca06_dictionary"), "FROZEN_PROSPECTIVE_CONTRACT_WITH_EXTERNAL_CONTEXT", "Describe the exact frozen descriptor groups and freeze order.",
        "Do not claim that an equivariant GNN was implemented or tested.", ("C04",))
    add("REQUAL-P01", "8. Prospective observable redesign and fresh requalification", "Freshness design",
        "DDO-02B generated 384 entirely new complete cases, balanced as 96 per F1-F4 family, using new deterministic phases and disorder realizations. The formal registry recorded zero field-lineage overlap with DDO-01D, and exactly 49,152 fresh particle samples entered the requalification.",
        ("fresh_registry", "fresh_metrics"), "FROZEN_FRESH_DESIGN", "State exact case balance, sample count, and zero lineage overlap.",
        "Do not reuse the 512 development cases as fresh formal evidence.")
    add("REQUAL-P02", "8. Prospective observable redesign and fresh requalification", "Fresh density result",
        "For density rate at the formal expanded C3/L3 combination, DNN P90 was 8.202 and the best fixed oracle NRMSE was 0.5481, exceeding the frozen limits of 0.60 and 0.50, respectively. Density rate therefore failed fresh H3 despite having previously passed H1 and the qualified H2 disorder scope.",
        ("fresh_metrics", "fresh_verdict"), "FROZEN_FRESH_H3_FAIL", "Report the exact density-rate failure metrics and distinguish H1/H2 from H3.",
        "Do not use H1/H2 PASS to repair the H3 verdict.")
    add("REQUAL-P03", "8. Prospective observable redesign and fresh requalification", "Fresh pressure result",
        "For pressure-gradient acceleration, DNN P90 was 45.54, conditional-variance upper95 was 1.070, and oracle NRMSE was 1.010. Each value exceeded its frozen H3 limit, and the component remained H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE on fresh evidence.",
        ("fresh_metrics", "fresh_verdict"), "FROZEN_FRESH_H3_FAIL", "Report the exact pressure metrics and component verdict.",
        "Do not attribute the failure to a single descriptor, disorder variable, or architecture.")
    add("REQUAL-P04", "8. Prospective observable redesign and fresh requalification", "Fresh viscosity result",
        "For viscosity-Laplacian acceleration, DNN median was 0.2773, DNN P90 was 26.88, conditional-variance upper95 was 0.4042, and oracle NRMSE was 1.049. These values exceeded their corresponding frozen limits, so viscosity also failed fresh H3.",
        ("fresh_metrics", "fresh_verdict"), "FROZEN_FRESH_H3_FAIL", "Report the exact viscosity metrics and fresh verdict.",
        "Do not generalize to every viscosity discretization or every observable representation.")
    add("REQUAL-P05", "8. Prospective observable redesign and fresh requalification", "Frame fallback and terminal implication",
        "The frozen observable-frame fallback was triggered in exactly 515,904 of 627,264 particle environments (82.246710%), documenting high directional degeneracy for this construction. Because all three primary mappings failed fresh H3, H4 remained NOT_QUALIFIED, no H5 component was authorized, and the tested online route was closed.",
        ("fresh_schema", "fresh_verdict", "final_status"), "FROZEN_FRESH_LIMITATION_AND_CLOSURE", "Report the exact fallback numerator/denominator and route-specific closure.",
        "Do not claim that all equivariant representations fail or that H4/H5 failed.")

    # 9 Discussion
    add("DISC-P01", "9. Discussion", "Core interpretation",
        "The evidence separates magnitude, systematic dependence, and observable determination. The defects were far above qualified uncertainty, and several components exhibited systematic scaling, yet neither the initial nor the expanded deployment-compatible instantaneous representation satisfied H3. The central result is therefore that resolvability and scaling do not imply identifiability from the tested observables.",
        ("h1", "h2", "initial_verdict", "fresh_verdict"), "FROZEN_CROSS_STAGE_SYNTHESIS", "Use the core manuscript statement within the tested scope.",
        "Do not state a universal theorem for SPH defects or inverse problems.")
    add("DISC-P02", "9. Discussion", "Failure interpretation",
        "Qualified coverage in both identifiability cycles makes a simple lack of nearby feature samples insufficient as the sole explanation. The remaining evidence is consistent with observable conditional ambiguity, expressed through heavy disagreement tails, component-dependent conditional variance, weak oracle performance, and family sensitivity. " + citations["C03"]["placeholder"],
        ("initial_metrics", "fresh_metrics", "failure_taxonomy"), "FROZEN_INTERPRETATION_WITH_EXTERNAL_CONTEXT", "Describe ambiguity as supported by the frozen diagnostics.",
        "Do not claim an architecture-independent impossibility result.", ("C03",))
    add("DISC-P03", "9. Discussion", "Disorder and component specificity",
        "The scaling and identifiability evidence are both component-specific. Density rate retained systematic scaling under the tested disorder scope but still failed fresh H3, whereas pressure and viscosity had regular-only formal H2 scope and different ambiguity signatures. This contrast shows why a single descriptor expansion or a total-acceleration diagnostic cannot stand in for componentwise qualification.",
        ("h2", "disorder", "fresh_metrics"), "FROZEN_COMPONENTWISE_SYNTHESIS", "Compare component scopes without changing their separate verdicts.",
        "Do not impose a shared mechanism or scaling exponent across components.")
    add("DISC-P04", "9. Discussion", "Redesign lesson",
        "The prospective redesign is informative precisely because development evidence and fresh qualification were separated. Directional and component-specific hypotheses were selected from consumed evidence, frozen in CA-06, and then tested on new lineages without post-target descriptor adjustment. The high frame-degeneracy rate limits that particular directional construction, while leaving other equivariant or temporal formulations untested. " + citations["C04"]["placeholder"],
        ("attribution", "ca06", "fresh_registry", "fresh_schema"), "FROZEN_REDESIGN_INTERPRETATION_WITH_EXTERNAL_CONTEXT", "Emphasize prospective separation and the construction-specific limitation.",
        "Do not claim that equivariant GNNs or temporal observables cannot help.", ("C04",))
    add("DISC-P05", "9. Discussion", "Methodological implication",
        "An upstream identifiability gate can prevent architecture search from being used to answer a question that the available inputs do not support. In this project, the gate led to disciplined closure before neural training, optimization, time integration, rollout, or solver-in-loop claims were attempted. " + citations["C05"]["placeholder"],
        ("final_status",), "FROZEN_GOVERNANCE_INTERPRETATION_WITH_EXTERNAL_CONTEXT", "State the project-specific value of prospective gating and closure.",
        "Do not claim that this exact hierarchy is the only valid workflow for computational science.", ("C05",))
    add("DISC-P06", "9. Discussion", "Limitations",
        "The evidence is restricted to fixed-time, two-dimensional, periodic, manufactured-field evaluations of the frozen SPH operators and observables. Boundary information, temporal history, latent state, alternative sensors, dynamic integration, learned representations, and solver feedback were not tested. The target SVD is an empirical covariance diagnostic only, and high-resolution SPH was not used as truth.",
        ("charter", "subspace", "final_status"), "FROZEN_LIMITATION", "List the untested domains and preserve the reference/subspace boundaries.",
        "Do not infer that temporal information cannot help or that the target manifold is two-dimensional.")
    add("DISC-P07", "9. Discussion", "Cross-paper separation",
        "SPH-DDO is a publication project distinct from SPH-PIO. The present study terminates at pre-learning identifiability, whereas SPH-PIO concerns a separate trained conservative-correction route and its optimizer and support evidence; shared static SPH foundations should be cross-referenced without merging primary evidence or claims.",
        ("cross_paper",), "FROZEN_PUBLICATION_BOUNDARY", "State the distinct questions and non-overlap rule.",
        "Do not merge the manuscripts or import SPH-PIO training results into SPH-DDO.")

    # 10 Conclusions
    add("CONC-P01", "10. Conclusions", "Evidence-chain conclusion",
        "This study qualified a fixed-time SPH spatial-defect reference, established signal resolvability, identified component- and disorder-dependent scaling, and then tested deployable-observable identifiability before learning. The first representation failed H3, and the prospectively redesigned representation again failed all three primary dynamic mappings on fresh evidence.",
        ("h1", "h2", "initial_verdict", "fresh_registry", "fresh_verdict"), "FROZEN_FINAL_SYNTHESIS", "Summarize the completed evidence chain and repeated fresh H3 failure.",
        "Do not extend the conclusion beyond the tested instantaneous online route.")
    add("CONC-P02", "10. Conclusions", "Core statement",
        "A spatial discretization defect can be numerically resolvable and exhibit systematic scaling without being identifiable from the tested deployment-compatible instantaneous observables. This distinction is the principal scientific result of SPH-DDO.",
        ("h1", "h2", "fresh_verdict", "final_status"), "FROZEN_CORE_CONCLUSION", "Use this sentence as the central manuscript statement.",
        "Do not rewrite it as a claim that all SPH defects are unlearnable.")
    add("CONC-P03", "10. Conclusions", "Closure state",
        "The final route status is ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED. H4 is NOT_QUALIFIED, H5 and H6 are NOT_AUTHORIZED, and no neural training was performed because the upstream H3 qualification prerequisite was not met. The evidence is frozen for publication, and no DDO-03 continuation is authorized.",
        ("final_hypotheses", "final_status"), "FROZEN_TERMINAL_STATE", "State the exact terminal and authorization vocabulary.",
        "Do not state that H4, H5, H6, neural SPH, GNNs, or Transformers failed.")

    # Render manuscript.
    title = "# Resolvable yet non-identifiable: pre-learning qualification of instantaneous SPH discretization-defect correction\n\n"
    title += "**Manuscript version:** v0.1 evidence-assembled skeleton  \n**Authors:** [TO BE COMPLETED]  \n**Target journal:** [TO BE SELECTED]\n\n"
    section_order = [
        "Abstract", "1. Introduction", "2. Spatial discretization-defect formulation and qualification hierarchy",
        "3. Analytical reference and numerical qualification", "4. Signal resolvability",
        "5. Componentwise scaling and disorder sensitivity", "6. Mechanism-stratified analytical defect atlas",
        "7. Deployable-observable identifiability", "8. Prospective observable redesign and fresh requalification",
        "9. Discussion", "10. Conclusions",
    ]
    rendered = [title]
    for section in section_order:
        rendered.append(f"## {section}\n")
        for item in [value for value in p if value.section == section]:
            rendered.append(item.text + "\n\n" + item.annotation() + "\n")
        if section == "2. Spatial discretization-defect formulation and qualification hierarchy":
            rendered.append("\n**[FIGURE 1 NEAR HERE: qualification hierarchy]**\n\n**[FIGURE 2 NEAR HERE: defect definition and firewall]**\n")
        if section == "4. Signal resolvability": rendered.append("\n**[FIGURE 3 NEAR HERE; TABLE 1 NEAR HERE]**\n")
        if section == "5. Componentwise scaling and disorder sensitivity": rendered.append("\n**[FIGURE 4 NEAR HERE; TABLE 2 NEAR HERE]**\n")
        if section == "6. Mechanism-stratified analytical defect atlas": rendered.append("\n**[FIGURE 5 NEAR HERE]**\n")
        if section == "7. Deployable-observable identifiability": rendered.append("\n**[FIGURE 6 NEAR HERE]**\n")
        if section == "8. Prospective observable redesign and fresh requalification": rendered.append("\n**[FIGURES 7-8 NEAR HERE; TABLE 3 NEAR HERE]**\n")
        if section == "9. Discussion": rendered.append("\n**[TABLE 4 NEAR HERE: failure taxonomy]**\n")
    manuscript_path = PUB / "manuscript_v0_1.md"
    manuscript_path.write_text("\n".join(rendered).rstrip() + "\n")

    # Paragraph evidence map.
    map_path = PUB / "paragraph_evidence_map.csv"
    fields = ("claim_id", "section", "paragraph_purpose", "claim_text_summary", "evidence_artifact",
              "evidence_sha256", "scientific_status", "permitted_wording", "prohibited_extrapolation", "citation_need_ids")
    with map_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for item in p:
            writer.writerow({
                "claim_id": item.claim_id, "section": item.section, "paragraph_purpose": item.purpose,
                "claim_text_summary": re.sub(r"\s+", " ", item.text)[:260],
                "evidence_artifact": item.artifact_paths, "evidence_sha256": item.artifact_hashes,
                "scientific_status": item.status, "permitted_wording": item.permitted,
                "prohibited_extrapolation": item.prohibited, "citation_need_ids": ";".join(item.citations),
            })

    # Figure map.
    figure_rows = [
        ("Figure 1", "Qualification hierarchy and final stop", "FORM-P04;REQUAL-P05;CONC-P03", ("final_hypotheses", "final_status"), "Show H3 stop; H4 not qualified; H5/H6 not authorized", "No neural-training visual or H4/H5/H6 failure symbol"),
        ("Figure 2", "Defect definition and observable/reference firewall", "FORM-P01;FORM-P03;FORM-P05;NUM-P01", ("charter", "defect", "initial_firewall", "fresh_schema"), "Show fixed-time equation and one-way target construction", "No high-resolution-SPH truth or reference-to-input arrow"),
        ("Figure 3", "H1 signal-to-uncertainty qualification", "SIGNAL-P01;SIGNAL-P02;SIGNAL-P03", ("h1",), "Show R_c and L95_c against frozen thresholds", "No scaling or learnability inference"),
        ("Figure 4", "H2 component/disorder scaling structure", "SCALE-P01;SCALE-P02;SCALE-P03;SCALE-P04", ("h2",), "Show density disorder PASS, momentum regular-only, interpolation FAIL", "No universal convergence order"),
        ("Figure 5", "Mechanism-stratified atlas", "ATLAS-P01;ATLAS-P02;ATLAS-P03", ("atlas", "atlas_report"), "Show 512 cases and F1-F4 balance with development label", "No fresh-test or H3 implication"),
        ("Figure 6", "Initial deployable-observable H3 failure", "ID-P01;ID-P02;ID-P03;ID-P04;ID-P05", ("initial_metrics", "initial_verdict", "ablation"), "Show all-gates failure and qualified coverage", "No replacement score or manifold claim"),
        ("Figure 7", "Failure attribution and prospective redesign", "REDESIGN-P01;REDESIGN-P02;REDESIGN-P03", ("attribution", "observability", "ca06"), "Separate consumed attribution from frozen redesign", "No DDO-02A H3 PASS"),
        ("Figure 8", "Fresh DDO-02B requalification and closure", "REQUAL-P01;REQUAL-P02;REQUAL-P03;REQUAL-P04;REQUAL-P05", ("fresh_registry", "fresh_metrics", "fresh_schema", "final_status"), "Show 384 fresh cases, exact metrics, fallback, and route closure", "No claim that neural/equivariant/temporal routes universally fail"),
    ]
    figure_path = PUB / "figure_to_claim_map.csv"
    with figure_path.open("w", newline="") as handle:
        fields_f = ("figure_id", "figure_purpose", "claim_ids", "evidence_artifact", "evidence_sha256", "scientific_status", "allowed_visual_message", "prohibited_visual_implication")
        writer = csv.DictWriter(handle, fieldnames=fields_f); writer.writeheader()
        for fid, purpose, claims, keys, allowed, prohibited in figure_rows:
            writer.writerow({"figure_id": fid, "figure_purpose": purpose, "claim_ids": claims,
                "evidence_artifact": ";".join(ARTIFACTS[k] for k in keys),
                "evidence_sha256": ";".join(sha256(ROOT / ARTIFACTS[k]) for k in keys),
                "scientific_status": "FROZEN_SOURCE_PLAN_NO_NEW_RESULT", "allowed_visual_message": allowed,
                "prohibited_visual_implication": prohibited})

    # Table map.
    table_rows = [
        ("Table 1", "Numerical qualification and H1 summary", "NUM-P02;SIGNAL-P01;SIGNAL-P02", ("h1", "h2"), "H1/H2 qualification counts and H1 exact metrics", "No H3 inference"),
        ("Table 2", "Componentwise H1-H6 ledger", "FORM-P04;SCALE-P02;SCALE-P03;SCALE-P04;CONC-P03", ("final_hypotheses",), "Exact PASS/FAIL/NOT_QUALIFIED/NOT_AUTHORIZED vocabulary", "No NOT_AUTHORIZED-to-FAIL collapse"),
        ("Table 3", "Initial and fresh H3 metrics", "ID-P03;ID-P04;REQUAL-P02;REQUAL-P03;REQUAL-P04", ("initial_metrics", "fresh_metrics"), "Full frozen thresholds and component outcomes", "No favorable-metric cherry-picking"),
        ("Table 4", "Failure taxonomy F0-F7", "SIGNAL-P03;ID-P04;ID-P05;REQUAL-P05;DISC-P02", ("failure_taxonomy",), "Frozen dispositions and evidence boundaries", "No cause beyond frozen evidence"),
        ("Table S1", "Exact H1 component ledger", "SIGNAL-P01;SIGNAL-P02", ("h1",), "T_c, U_c, R_c, L95_c, eligible/unexcited counts", "No inserted unexcited zeros"),
        ("Table S2", "Exact H2 track ledger", "SCALE-P01;SCALE-P02;SCALE-P03;SCALE-P04", ("h2",), "Regular/jitter and refinement/spectral gates", "No descriptive-slope formalization"),
        ("Table S3", "Deployment observability and descriptor dictionary", "REDESIGN-P02;REDESIGN-P03", ("observability", "ca06_dictionary"), "Runtime/direct/estimable/design-only classes and 30 descriptors", "No target-derived input"),
        ("Table S4", "Fresh fold/QC and frame fallback", "NUM-P04;REQUAL-P01;REQUAL-P05", ("fresh_schema", "fresh_metrics"), "49,152 samples, fold QC, 515904/627264 fallback", "No equivariant impossibility claim"),
    ]
    table_path = PUB / "table_to_claim_map.csv"
    with table_path.open("w", newline="") as handle:
        fields_t = ("table_id", "table_purpose", "claim_ids", "evidence_artifact", "evidence_sha256", "scientific_status", "allowed_table_content", "prohibited_table_implication")
        writer = csv.DictWriter(handle, fieldnames=fields_t); writer.writeheader()
        for tid, purpose, claims, keys, allowed, prohibited in table_rows:
            writer.writerow({"table_id": tid, "table_purpose": purpose, "claim_ids": claims,
                "evidence_artifact": ";".join(ARTIFACTS[k] for k in keys),
                "evidence_sha256": ";".join(sha256(ROOT / ARTIFACTS[k]) for k in keys),
                "scientific_status": "FROZEN_SOURCE_PLAN_NO_NEW_RESULT", "allowed_table_content": allowed,
                "prohibited_table_implication": prohibited})

    # Citation register.
    citation_path = PUB / "citation_need_register.csv"
    with citation_path.open("w", newline="") as handle:
        fields_c = ("citation_need_id", "placeholder", "manuscript_location", "topic", "required_support", "claim_boundary", "status")
        writer = csv.DictWriter(handle, fieldnames=fields_c); writer.writeheader()
        for cid, item in citations.items():
            writer.writerow({"citation_need_id": cid, "placeholder": item["placeholder"],
                "manuscript_location": item["section"], "topic": item["topic"],
                "required_support": item["support"], "claim_boundary": item["boundary"],
                "status": "OPEN_NO_REFERENCE_SELECTED"})

    # Claim audit.
    manuscript = manuscript_path.read_text()
    ids_in_text = re.findall(r"^CLAIM_ID: ([A-Z0-9-]+)$", manuscript, flags=re.MULTILINE)
    ids_expected = [item.claim_id for item in p]
    map_rows = list(csv.DictReader(map_path.open()))
    hash_errors = []
    for row in map_rows:
        if row["evidence_artifact"] == "EXTERNAL_CITATION_NOT_YET_SELECTED":
            continue
        paths = row["evidence_artifact"].split(";"); hashes = row["evidence_sha256"].split(";")
        for artifact, expected in zip(paths, hashes, strict=True):
            if sha256(ROOT / artifact) != expected: hash_errors.append(artifact)
    placeholders_in_text = set(re.findall(r"\[CITATION NEEDED: [^\]]+\]", manuscript))
    registered_placeholders = {item["placeholder"] for item in citations.values()}
    required_sections = [f"## {section}" for section in section_order]
    checks = {
        "required_sections_11_including_abstract": all(section in manuscript for section in required_sections),
        "paragraph_count": len(p), "annotation_count": len(ids_in_text),
        "unique_claim_ids": len(set(ids_expected)) == len(ids_expected),
        "annotation_ids_match_map": ids_in_text == ids_expected == [row["claim_id"] for row in map_rows],
        "evidence_hash_mismatch_count": len(hash_errors),
        "citation_placeholders_all_registered": placeholders_in_text == registered_placeholders,
        "citation_reference_count_selected": 0,
        "figure_map_rows": len(figure_rows), "table_map_rows": len(table_rows),
        "h4_exact_status_preserved": "H4 is NOT_QUALIFIED" in manuscript,
        "h5_h6_exact_status_preserved": "H5 and H6 are NOT_AUTHORIZED" in manuscript,
        "no_neural_training_reason_explicit": "no neural training was performed because the upstream H3 qualification prerequisite was not met" in manuscript,
        "core_statement_exact": "A spatial discretization defect can be numerically resolvable and exhibit systematic scaling without being identifiable from the tested deployment-compatible instantaneous observables." in manuscript,
    }
    audit_pass = (
        checks["required_sections_11_including_abstract"] and checks["unique_claim_ids"]
        and checks["annotation_ids_match_map"] and checks["evidence_hash_mismatch_count"] == 0
        and checks["citation_placeholders_all_registered"] and checks["citation_reference_count_selected"] == 0
        and checks["h4_exact_status_preserved"] and checks["h5_h6_exact_status_preserved"]
        and checks["no_neural_training_reason_explicit"] and checks["core_statement_exact"]
    )
    audit_path = PUB / "manuscript_v0_1_claim_audit.md"
    audit_path.write_text(f"""# Manuscript v0.1 claim audit

## Terminal state

`SPH_DDO_MANUSCRIPT_V01_EVIDENCE_ASSEMBLED`

Audit result: `{'PASS' if audit_pass else 'FAIL'}`.

## Completeness and provenance

- Required scientific sections plus abstract present: `{checks['required_sections_11_including_abstract']}`.
- Evidence-annotated paragraphs: `{len(p)}`.
- Inline annotation count: `{len(ids_in_text)}`.
- Unique CLAIM_ID values: `{checks['unique_claim_ids']}`.
- Manuscript/CSV CLAIM_ID order and membership match: `{checks['annotation_ids_match_map']}`.
- Evidence SHA-256 mismatches: `{len(hash_errors)}`.
- Figure-to-claim rows: `{len(figure_rows)}`.
- Table-to-claim rows: `{len(table_rows)}`.

## Scientific-status preservation

- H1 remains qualified over frozen scopes.
- H2 remains component- and disorder-dependent.
- H3 remains failed on fresh evidence for density rate, pressure gradient, and viscosity Laplacian.
- H4 is `NOT_QUALIFIED`.
- H5 and H6 are `NOT_AUTHORIZED`.
- The manuscript explicitly states that neural training was not performed because H3 was not met.
- SPH-DDO remains separate from SPH-PIO.

## Citation audit

- Unique external citation placeholders: `{len(placeholders_in_text)}`.
- All placeholders registered: `{checks['citation_placeholders_all_registered']}`.
- References selected or fabricated in P1: `0`.
- Every external-context paragraph is marked `EXTERNAL_CONTEXT_PENDING_CITATION` or an equivalent mixed-status label.

## Prohibited-claim audit

The manuscript does not affirm that all SPH defects are unlearnable, neural SPH or Transformers cannot work, temporal information cannot help, equivariant GNNs cannot help, H4/H5/H6 failed, the target manifold is two-dimensional, or high-resolution SPH is truth. Such phrases appear only as explicit prohibitions or negated claim boundaries in evidence annotations.

## Work boundary

P1 performed evidence assembly and provenance checks only. It created no descriptor, field lineage, numerical target, H3 analysis, neural model, optimizer, integrator, rollout, solver evidence, or new scientific result.
""")
    if not audit_pass:
        raise RuntimeError(f"manuscript claim audit failed: {checks}")
    print(json.dumps({
        "terminal_state": "SPH_DDO_MANUSCRIPT_V01_EVIDENCE_ASSEMBLED",
        "paragraph_count": len(p), "figure_map_rows": len(figure_rows), "table_map_rows": len(table_rows),
        "citation_needs": len(citations), "audit": "PASS",
        "manuscript_sha256": sha256(manuscript_path), "paragraph_map_sha256": sha256(map_path),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
