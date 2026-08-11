# Pre-learning qualification of SPH spatial discretization defects: resolvability, scaling, and limits of instantaneous observable identifiability

**Manuscript version:** v0.2 literature-integrated evidence skeleton  
**Title status:** provisional after L1 literature audit  
**Authors:** [TO BE COMPLETED]  
**Target journal:** [TO BE SELECTED]


## Abstract

Learned corrections are meaningful only if the correction target is inferable from information available at deployment. Here we ask whether a fixed-time smoothed particle hydrodynamics (SPH) spatial discretization defect can be identified from low-cost instantaneous observables before a learned correction operator is introduced. We qualified the analytical reference, separated signal resolvability from scaling and identifiability, and applied prospectively frozen non-neural H3 gates to an initial and a redesigned observable representation.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ABSTRACT-P01
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json;data/identifiability/ddo01e_metrics.json;06_manifests/ca06_manifest.json;data/ddo02b_identifiability/ddo02b_metrics.json
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb;9b238af878ae9a8bb64166631abd99e30ca2c5d66d3535781085de86953f033f;551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582
SCIENTIFIC_STATUS: FROZEN_SYNTHESIS
PERMITTED_WORDING: State the pre-learning question and the prospective qualification sequence.
PROHIBITED_EXTRAPOLATION: Do not imply that neural training, temporal prediction, or solver-in-loop evaluation occurred.
-->

All frozen defect components were resolvable above qualified float64 numerical and reference uncertainty, while spatial scaling was component- and disorder-dependent. The first deployable representation failed H3, and a prospectively expanded representation again failed all three primary dynamic mappings on 384 entirely fresh cases. Thus, a spatial discretization defect can be numerically resolvable and exhibit systematic scaling without being identifiable from the tested deployment-compatible instantaneous observables; no neural training was performed because the upstream H3 prerequisite was not met.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ABSTRACT-P02
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json;data/identifiability/ddo01e_formal_verdicts.json;data/ddo02b_identifiability/ddo02b_metrics.json;06_manifests/ddo02b_manifest.json;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e;551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582;56fb9259a9abbc702684028485cce61b3f00fada37febe56778bc35492fc334d;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_CORE_CONCLUSION
PERMITTED_WORDING: Use the exact route-specific conclusion and state why training was not performed.
PROHIBITED_EXTRAPOLATION: Do not claim fundamental unlearnability, neural failure, global H4 failure, or H5/H6 failure.
-->

## 1. Introduction

SPH represents continuum fields on moving particles through compact-support kernel approximations, so its spatial operators depend on resolution, support, particle arrangement, and local consistency. These dependencies can produce component-specific spatial discretization defects, particularly when the particle configuration departs from regularity. (Quinlan et al., 2006; Litvinov et al., 2015; Sigalotti et al., 2016).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: INTRO-P01
EVIDENCE_ARTIFACT: publication/literature/verified_reference_register.csv;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: 6d33739d36d1ef7d27d2c9c375d8478eacf6fabf72c1a09cf53b832281589cb2;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: VERIFIED_EXTERNAL_LITERATURE_CONTEXT
PERMITTED_WORDING: Retain only as literature-supported background after citation verification.
PROHIBITED_EXTRAPOLATION: Do not present this paragraph as project evidence or claim universal behavior for all SPH formulations.
-->

Data-driven correction operators have been proposed as one route for compensating numerical error in particle and mesh-based solvers. However, architecture selection and optimization cannot resolve a more basic information question: whether the desired correction is determined by quantities that remain available when the model is deployed. (Bar-Sinai et al., 2019; Um et al., 2020; Woodward et al., 2023; Amato et al., 2024; Winchenbach and Thuerey, 2026).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: INTRO-P02
EVIDENCE_ARTIFACT: publication/literature/verified_reference_register.csv;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: 6d33739d36d1ef7d27d2c9c375d8478eacf6fabf72c1a09cf53b832281589cb2;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: VERIFIED_EXTERNAL_LITERATURE_CONTEXT
PERMITTED_WORDING: Use as motivation for an upstream observability test once suitable literature is supplied.
PROHIBITED_EXTRAPOLATION: Do not imply that any neural architecture was evaluated in SPH-DDO.
-->

A target may be large relative to numerical uncertainty and may vary systematically with discretization parameters, yet still be conditionally ambiguous given the observable input. This distinction motivates separate tests of signal, scaling, and identifiability rather than treating predictive model fitting as the first qualification step. (Bellman and Åström, 1970; Stuart, 2010).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: INTRO-P03
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: FROZEN_PROJECT_LOGIC_WITH_VERIFIED_EXTERNAL_CONTEXT
PERMITTED_WORDING: Separate H1, H2, and H3 as distinct questions.
PROHIBITED_EXTRAPOLATION: Do not turn the empirical diagnostics into a general inverse-problem theorem.
-->

We therefore formulate SPH-DDO around the question: is the instantaneous spatial discretization defect of a low-cost SPH operator identifiable from deployment-compatible observables before a learned correction is introduced? The contribution is a prospective evidence chain spanning reference qualification, signal resolvability, componentwise scaling, mechanism-stratified atlas construction, observable identifiability, failure attribution, observable redesign, and fresh requalification. The chain terminates when all three primary dynamic mappings fail fresh H3.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: INTRO-P04
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_PROJECT_SCOPE
PERMITTED_WORDING: Present the scientific logic and terminal boundary.
PROHIBITED_EXTRAPOLATION: Do not describe the work as an architecture comparison, a trained correction method, or SPH-PIO continuation.
-->

## 2. Spatial discretization-defect formulation and qualification hierarchy

For a smooth manufactured continuum state q*(x), continuum spatial operator L, sampling map R_h, and corresponding SPH semi-discrete operator L_h, the fixed-time defect is defined as d_h* = R_h L(q*) - L_h(R_h q*). The sign convention is positive-additive: adding the defect to the low-cost spatial operator recovers the sampled continuum operator within the qualified numerical uncertainty.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: FORM-P01
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;02_defect_definitions/spatial_defect_definition.md
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;f986d2e8adbfa5ee65d2c06dff7c3b372f23bcfe075646a009347de07902ab8e
SCIENTIFIC_STATUS: FROZEN_DEFINITION
PERMITTED_WORDING: Use the frozen fixed-time defect equation and positive-additive sign convention.
PROHIBITED_EXTRAPOLATION: Do not include time-integration, next-state, rollout, or division-by-dt error in the target.
-->

The independently tested primary dynamic components are density rate, pressure-gradient acceleration, and viscosity-Laplacian acceleration. Total acceleration is retained only as the derived pressure-plus-viscosity closure diagnostic, while interpolation density is an algebraic density diagnostic. Component roles remain fixed throughout the qualification chain.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: FORM-P02
EVIDENCE_ARTIFACT: 02_defect_definitions/operator_decomposition.md;publication/final_hypothesis_ledger.csv
EVIDENCE_SHA256: 13c01a36aecfd977fa8d2666db0a1aa57c1bad53b1d1c768752ec207a1f4162b;694841a5ff154ebaefa39207a526739eee619a8db6fb53d02447b92d92ba0743
SCIENTIFIC_STATUS: FROZEN_COMPONENT_ROLES
PERMITTED_WORDING: Distinguish primary mappings from derived and algebraic diagnostics.
PROHIBITED_EXTRAPOLATION: Do not report total acceleration as an independently fitted H3 route or interpolation density as a primary dynamic target.
-->

Analytical and manufactured information is used only to construct or audit targets. Candidate deployable descriptors, normalization, neighborhood construction, data routing, and diagnostic inputs are prohibited from using reference-minus-low-cost quantities or any equivalent target-derived proxy. Observable and reference fields are stored separately and audited before each identifiability analysis.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: FORM-P03
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;data/identifiability/ddo01e_firewall_audit.json;data/ddo02b_identifiability/ddo02b_observable_feature_schema.json
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;5e32db365620c8d8d621d3ccabc502aaffe1f83bda542e533541daf235e20d8b;3abde8010d1eb99112af74406fffab164ecaa20aa8ba4df3e3c8d907440c28d5
SCIENTIFIC_STATUS: FROZEN_FIREWALL
PERMITTED_WORDING: State the strict separation of deployable inputs and reference targets.
PROHIBITED_EXTRAPOLATION: Do not equate reference-free with deployment-observable or imply that manufactured metadata is automatically deployable.
-->

The hierarchy tests H1 signal resolvability, H2 systematic scaling, H3 observable identifiability, H4 bounded locality conditional on H3, H5 structure-compatible representation conditional on upstream qualification, and H6 generalization. A downstream stage is not interpreted when its prerequisite is absent. In the final ledger, H4 is NOT_QUALIFIED and H5 and H6 are NOT_AUTHORIZED, rather than failed.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: FORM-P04
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;publication/final_hypothesis_ledger.csv;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;694841a5ff154ebaefa39207a526739eee619a8db6fb53d02447b92d92ba0743;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_HYPOTHESIS_GOVERNANCE
PERMITTED_WORDING: Use the exact final status vocabulary.
PROHIBITED_EXTRAPOLATION: Do not collapse NOT_QUALIFIED or NOT_AUTHORIZED into FAIL.
-->

Closed-form analytical derivatives are the primary reference and are cross-checked by an independent automatic-differentiation route. Refining the same SPH discretization is not treated as truth. This hierarchy confines the study to analytical fixed-time spatial defects and avoids conflating discretization refinement with an independent continuum reference.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: FORM-P05
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;06_manifests/ddo01br_manifest.json;06_manifests/ddo01d_manifest.json
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8
SCIENTIFIC_STATUS: FROZEN_REFERENCE_HIERARCHY
PERMITTED_WORDING: State the analytical-reference hierarchy and high-resolution-SPH boundary.
PROHIBITED_EXTRAPOLATION: Do not claim that high-resolution SPH is truth.
-->


**[FIGURE 1 NEAR HERE: qualification hierarchy]**

**[FIGURE 2 NEAR HERE: defect definition and firewall]**

## 3. Analytical reference and numerical qualification

Analytical derivatives and continuum components were independently evaluated and compared under float64 discrepancy gates. The SPH graph was audited for periodic topology, reciprocity, support completeness, and deterministic reconstruction, while repeat evaluation, neighbor permutation, compensated accumulation, sign recovery, and component closure were retained as explicit numerical checks.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: NUM-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json;06_manifests/ddo01d_manifest.json;data/ddo02b_atlas/ddo02b_case_metadata.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8;1e89221d7d13c1933d2ebb89452c4f1c3273e7ec15b9e2bf9557e3b2cea01a9e
SCIENTIFIC_STATUS: FROZEN_METHOD
PERMITTED_WORDING: Describe only the audits recorded in the frozen stage artifacts.
PROHIBITED_EXTRAPOLATION: Do not infer dynamic stability, conservation of a learned correction, or solver convergence.
-->

All 24 fresh H1 cases passed the mandatory analytical, topology, uncertainty, sign, and closure audits; the maximum analytical-route derivative discrepancy was 1.776357e-15 and the maximum component-closure residual was zero. All 204 fresh H2 cases likewise passed mandatory qualification, with a maximum derivative discrepancy of 1.421086e-14 and admissible formal log responses throughout.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: NUM-P02
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef
SCIENTIFIC_STATUS: FROZEN_QUALIFIED_RESULT
PERMITTED_WORDING: Report the exact H1/H2 numerical qualification counts and discrepancies.
PROHIBITED_EXTRAPOLATION: Do not treat these cases as balanced F1-F4 H3 evidence.
-->

The 512-case DDO-01D development atlas passed numerical qualification without post-target replacement or failure deletion. Its observable and reference-target archives were physically separated, and no empirical target normalization based on fitted powers of h was created.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: NUM-P03
EVIDENCE_ARTIFACT: 06_manifests/ddo01d_manifest.json;07_reports/ddo01d_atlas_report.md
EVIDENCE_SHA256: aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8;34287fad5e29fec9cafd9f66899a4ba1069095d9b8d19d495aacfd4f1c21fd9c
SCIENTIFIC_STATUS: FROZEN_DEVELOPMENT_ATLAS_QUALIFICATION
PERMITTED_WORDING: State 512/512 qualification and storage separation.
PROHIBITED_EXTRAPOLATION: Do not call the DDO-01D cases fresh DDO-02B requalification evidence.
-->

All 384 DDO-02B cases passed the same fixed-time mandatory numerical qualification before formal H3 aggregation. The release audit passed all 13 frozen gates, and the fresh observable feature schema records that no reference archive was opened during observable feature construction.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: NUM-P04
EVIDENCE_ARTIFACT: data/ddo02b_atlas/ddo02b_case_metadata.json;data/ddo02b_identifiability/ddo02b_observable_feature_schema.json;06_manifests/ddo02b_manifest.json
EVIDENCE_SHA256: 1e89221d7d13c1933d2ebb89452c4f1c3273e7ec15b9e2bf9557e3b2cea01a9e;3abde8010d1eb99112af74406fffab164ecaa20aa8ba4df3e3c8d907440c28d5;56fb9259a9abbc702684028485cce61b3f00fada37febe56778bc35492fc334d
SCIENTIFIC_STATUS: FROZEN_FRESH_QUALIFICATION
PERMITTED_WORDING: State 384/384 validity, firewall preservation, and release completion.
PROHIBITED_EXTRAPOLATION: Do not interpret release qualification as H3, H5, rollout, or solver qualification.
-->

## 4. Signal resolvability

H1 compares a componentwise target scale T_c with qualified numerical/reference uncertainty U_c through R_c = T_c/U_c and a stratified bootstrap lower bound L95_c. The frozen criteria require R_c >= 10 and strictly L95_c > 5; analytically unexcited component-case pairs are excluded rather than inserted as zeros.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SIGNAL-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875
SCIENTIFIC_STATUS: FROZEN_H1_METHOD
PERMITTED_WORDING: State the frozen H1 thresholds and unexcited-case rule.
PROHIBITED_EXTRAPOLATION: Do not redefine H1 using average target magnitude or include unexcited zeros.
-->

All five frozen components passed H1 over their qualified excited-case scopes. R_c ranged from 2.455e11 for interpolation density to 2.194e12 for pressure-gradient acceleration, and L95_c ranged from 2.284e11 to 1.643e12. These margins place the fixed-time defects far above the qualified float64 uncertainty floor.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SIGNAL-P02
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875
SCIENTIFIC_STATUS: FROZEN_H1_PASS
PERMITTED_WORDING: Report componentwise H1 PASS and the frozen numerical range.
PROHIBITED_EXTRAPOLATION: Do not infer scaling, identifiability, learnability, or deployment performance from H1.
-->

The H1 evidence rejects insufficient signal amplitude as the reason that the project later stopped. It does not establish that the same signals are uniquely determined by deployable observables; that question remains H3 and requires separate evidence.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SIGNAL-P03
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;publication/failure_taxonomy.md
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;0af5609d7ee6603f001e0260ea70959394096ff81d4b051a5f081d02b991a69f
SCIENTIFIC_STATUS: FROZEN_INTERPRETATION
PERMITTED_WORDING: State that weak signal was rejected within the tested scopes and distinguish H1 from H3.
PROHIBITED_EXTRAPOLATION: Do not describe H1 PASS as proof of predictability.
-->


**[FIGURE 3 NEAR HERE; TABLE 1 NEAR HERE]**

## 5. Componentwise scaling and disorder sensitivity

H2 was evaluated prospectively on refinement and spectral tracks at the canonical formal support ratio h/dx = 4. Formal decisions used monotonicity and dispersion gates; reported local slopes were descriptive and were not fitted convergence orders.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SCALE-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo01cr_manifest.json
EVIDENCE_SHA256: 44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef
SCIENTIFIC_STATUS: FROZEN_H2_METHOD
PERMITTED_WORDING: State the frozen H2 design and decision variables.
PROHIBITED_EXTRAPOLATION: Do not report descriptive slopes as universal convergence orders.
-->

Density rate passed the refinement and spectral gates in both regular and tested jittered scopes, yielding H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT. Within the frozen design, density rate therefore retained systematic scaling under the tested disorder perturbation.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SCALE-P02
EVIDENCE_ARTIFACT: 06_manifests/ddo01cr_manifest.json
EVIDENCE_SHA256: 44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef
SCIENTIFIC_STATUS: FROZEN_H2_PASS
PERMITTED_WORDING: Restrict density-rate scaling to the frozen F1 and canonical-support scope.
PROHIBITED_EXTRAPOLATION: Do not extrapolate to all disorder types, support ratios, boundaries, or H3 identifiability.
-->

Pressure-gradient acceleration, viscosity-Laplacian acceleration, and the derived total acceleration passed the formal regular scope but failed the jitter refinement requirement. Their final H2 status is therefore regular-scope-only, consistent with a component- and disorder-dependent scaling structure.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SCALE-P03
EVIDENCE_ARTIFACT: 06_manifests/ddo01cr_manifest.json
EVIDENCE_SHA256: 44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef
SCIENTIFIC_STATUS: FROZEN_H2_REGULAR_ONLY
PERMITTED_WORDING: Use regular-scope-only wording for pressure, viscosity, and total acceleration.
PROHIBITED_EXTRAPOLATION: Do not claim disorder-robust momentum scaling or a common component exponent.
-->

Interpolation density failed the regular and jitter scaling scopes and remains an algebraic diagnostic. Taken together, the H2 results show that systematic scaling is neither uniform across components nor sufficient to establish H3.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: SCALE-P04
EVIDENCE_ARTIFACT: 06_manifests/ddo01cr_manifest.json;publication/final_hypothesis_ledger.csv
EVIDENCE_SHA256: 44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;694841a5ff154ebaefa39207a526739eee619a8db6fb53d02447b92d92ba0743
SCIENTIFIC_STATUS: FROZEN_H2_FAIL_DIAGNOSTIC
PERMITTED_WORDING: State interpolation H2 failure and the componentwise H2 conclusion.
PROHIBITED_EXTRAPOLATION: Do not infer that interpolation H2 failure forces H3 failure in another component.
-->


**[FIGURE 4 NEAR HERE; TABLE 2 NEAR HERE]**

## 6. Mechanism-stratified analytical defect atlas

A mechanism-stratified analytical atlas was constructed to expose identifiability to multiple spatial-defect mechanisms rather than to a single refinement track. The exact registry was frozen before target evaluation and contained 512 complete static cases balanced as F1 = F2 = F3 = F4 = 128.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ATLAS-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo01d_manifest.json;07_reports/ddo01d_atlas_report.md
EVIDENCE_SHA256: aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8;34287fad5e29fec9cafd9f66899a4ba1069095d9b8d19d495aacfd4f1c21fd9c
SCIENTIFIC_STATUS: FROZEN_ATLAS_DESIGN
PERMITTED_WORDING: State the prospective registry and exact balance.
PROHIBITED_EXTRAPOLATION: Do not imply that the atlas itself evaluated H3 or constituted a sealed test.
-->

The families span single-mode, multimode, directional/mechanism, and controlled-disorder configurations under the frozen analytical-field specification. F4 includes matched blocks across support ratio and disorder, retaining difficult strata without failure deletion.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ATLAS-P02
EVIDENCE_ARTIFACT: 06_manifests/ddo01d_manifest.json;07_reports/ddo01d_atlas_report.md;07_reports/ddo01e_disorder_mechanism_report.md
EVIDENCE_SHA256: aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8;34287fad5e29fec9cafd9f66899a4ba1069095d9b8d19d495aacfd4f1c21fd9c;42c5c0dace911df53b3c03ff8c4c446bcd4c8d016dd85039b45b860ead67bf3a
SCIENTIFIC_STATUS: FROZEN_ATLAS_SCOPE
PERMITTED_WORDING: Describe the mechanism and matched-block organization at the frozen level.
PROHIBITED_EXTRAPOLATION: Do not attribute an independent causal effect to support ratio or neighbor count when they co-vary.
-->

DDO-01D is permanently labeled DEVELOPMENT_ATLAS and later CONSUMED_OBSERVABLE_DESIGN_EVIDENCE. Its 512 cases support initial identifiability analysis and redesign attribution, but they cannot be relabeled as fresh formal requalification evidence.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ATLAS-P03
EVIDENCE_ARTIFACT: 06_manifests/ddo01d_manifest.json;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_DATA_ROLE
PERMITTED_WORDING: Maintain the development/consumed role of all 512 cases.
PROHIBITED_EXTRAPOLATION: Do not count DDO-01D cases toward the DDO-02B fresh quota.
-->

The atlas qualifies construction, balance, numerical validity, descriptor availability, and the reference firewall. It does not by itself establish predictability, locality, representation suitability, target manifold dimension, or solver improvement.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ATLAS-P04
EVIDENCE_ARTIFACT: 07_reports/ddo01d_atlas_report.md
EVIDENCE_SHA256: 34287fad5e29fec9cafd9f66899a4ba1069095d9b8d19d495aacfd4f1c21fd9c
SCIENTIFIC_STATUS: FROZEN_CLAIM_BOUNDARY
PERMITTED_WORDING: Use the atlas only for its qualified design and data roles.
PROHIBITED_EXTRAPOLATION: Do not claim H3-H6, manifold structure, training success, or solver correction from atlas construction.
-->


**[FIGURE 5 NEAR HERE]**

## 7. Deployable-observable identifiability

H3 asks whether particles that are close in a deployment-compatible observable space also have sufficiently similar defects, and whether simple fixed non-neural oracles can predict held-out field lineages. The formal diagnostics combine nearest-neighbor target disagreement, conditional target variance, oracle NRMSE and improvement, family robustness, and feature-space coverage.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ID-P01
EVIDENCE_ARTIFACT: data/identifiability/ddo01e_metrics.json
EVIDENCE_SHA256: 871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb
SCIENTIFIC_STATUS: FROZEN_H3_METHOD
PERMITTED_WORDING: Describe the preregistered H3 diagnostic classes without presenting them as production models.
PROHIBITED_EXTRAPOLATION: Do not call kNN, ridge, or polynomial ridge trained correction architectures.
-->

The initial analysis used 65,536 SHA-selected particle samples from the 512-case development atlas. Five folds were separated by field lineage, feature scaling was fitted only on each training fold using median and interquartile range, and zero-IQR channels were excluded fold-locally.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ID-P02
EVIDENCE_ARTIFACT: data/identifiability/ddo01e_metrics.json;data/identifiability/ddo01e_firewall_audit.json
EVIDENCE_SHA256: 871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb;5e32db365620c8d8d621d3ccabc502aaffe1f83bda542e533541daf235e20d8b
SCIENTIFIC_STATUS: FROZEN_INITIAL_H3_EXECUTION
PERMITTED_WORDING: State sample count, lineage isolation, and train-only preprocessing.
PROHIBITED_EXTRAPOLATION: Do not describe the development evidence as fresh DDO-02B evidence.
-->

At the formal C3/L3 combination, density rate, pressure-gradient acceleration, and viscosity-Laplacian acceleration all received H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE. Favorable averages in selected diagnostics did not override failed tail, conditional-variance, oracle, or family gates because H3 required all frozen criteria.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ID-P03
EVIDENCE_ARTIFACT: data/identifiability/ddo01e_metrics.json;data/identifiability/ddo01e_formal_verdicts.json
EVIDENCE_SHA256: 871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb;478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e
SCIENTIFIC_STATUS: FROZEN_INITIAL_H3_FAIL
PERMITTED_WORDING: Report the componentwise all-gates verdict.
PROHIBITED_EXTRAPOLATION: Do not recompute a favorable replacement score or describe H3 failure as fundamental unlearnability.
-->

Formal feature-space coverage was approximately 0.953, above the 0.90 minimum, while H3 still failed. Insufficient coverage was therefore not a sufficient explanation for the initial result; the evidence instead supported observable conditional ambiguity through component-specific disagreement tails, variance, and oracle failures.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ID-P04
EVIDENCE_ARTIFACT: data/identifiability/ddo01e_metrics.json;publication/failure_taxonomy.md
EVIDENCE_SHA256: 871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb;0af5609d7ee6603f001e0260ea70959394096ff81d4b051a5f081d02b991a69f
SCIENTIFIC_STATUS: FROZEN_FAILURE_ATTRIBUTION_BOUNDARY
PERMITTED_WORDING: State that coverage passed but did not remove conditional ambiguity.
PROHIBITED_EXTRAPOLATION: Do not claim that coverage proves deployment generalization or that one ambiguity metric alone proves impossibility.
-->

Within matched F4 blocks, adding simple consistency descriptors did not uniformly reduce pressure or viscosity ambiguity across disorder strata. A post-verdict target SVD remained a covariance diagnostic only and did not alter the formal H3 result or establish a two-dimensional physical manifold.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: ID-P05
EVIDENCE_ARTIFACT: 07_reports/ddo01e_descriptor_ablation_report.md;data/identifiability/ddo01e_target_subspace_diagnostic.json
EVIDENCE_SHA256: 750e84a502035f35cf0b9ee67390be92b2863b9def8b28950ab839cf9e85ae62;e2a06889a503390a47e3e19b7164ad09135dd9575cc643d32a508bf55a381d58
SCIENTIFIC_STATUS: FROZEN_DIAGNOSTIC_BOUNDARY
PERMITTED_WORDING: Report no uniform consistency rescue and preserve the SVD diagnostic label.
PROHIBITED_EXTRAPOLATION: Do not claim a two-dimensional target manifold or use target coordinates as inputs.
-->


**[FIGURE 6 NEAR HERE]**

## 8. Prospective observable redesign and fresh requalification

DDO-02A used the consumed 512-case evidence only to diagnose why the initial representation failed; it was not an H3 requalification. Directional/equivariant augmentation and component-specific combinations were supported for a fresh test, whereas higher-order moments and derivative proxies were individually inconclusive.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REDESIGN-P01
EVIDENCE_ARTIFACT: data/ddo02a/attribution_metrics.json
EVIDENCE_SHA256: f2dca85e6c0e1db38aed3f32eca90a12375bc60af21a8dd544acc07b2d4c1a10
SCIENTIFIC_STATUS: FROZEN_CONSUMED_ATTRIBUTION
PERMITTED_WORDING: Use the diagnostic statuses only to motivate prospective testing.
PROHIBITED_EXTRAPOLATION: Do not present DDO-02A reductions as a new H3 PASS.
-->

The redesign distinguished runtime-direct, runtime-estimable, and design-only information. The manufactured-wave fields kh_max, kh_rms, mode_count, and jitter_fraction were classified as DESIGN_ONLY and excluded from the future formal deployable feature set.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REDESIGN-P02
EVIDENCE_ARTIFACT: data/ddo02a/deployment_observability_ledger.csv;06_manifests/ca06_manifest.json
EVIDENCE_SHA256: d2b80a2ae350e62afbcac7e1a6e037915ccd78240461548c3dd931fac5dd298b;9b238af878ae9a8bb64166631abd99e30ca2c5d66d3535781085de86953f033f
SCIENTIFIC_STATUS: FROZEN_DEPLOYMENT_AUDIT
PERMITTED_WORDING: Name the four prohibited design-only fields and their exclusion.
PROHIBITED_EXTRAPOLATION: Do not assume that any reference-free field is deployment-observable.
-->

CA-06 prospectively froze 30 reference-free descriptors spanning weighted second- to fourth-order particle moments, angular harmonics, observable-frame directional channels, and local quadratic reconstruction proxies. Dimensions, normalization, transformation behavior, conditioning, failure flags, context aggregation, and frame-degeneracy fallback were fixed before any fresh target was evaluated. (Satorras et al., 2021).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REDESIGN-P03
EVIDENCE_ARTIFACT: 06_manifests/ca06_manifest.json;06_manifests/ca06_descriptor_dictionary.json;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: 9b238af878ae9a8bb64166631abd99e30ca2c5d66d3535781085de86953f033f;591a9826b7560b5a8865b3b4b7d540efd7791deeba80cff9751e357b3908c262;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: FROZEN_PROSPECTIVE_CONTRACT_WITH_VERIFIED_EXTERNAL_CONTEXT
PERMITTED_WORDING: Describe the exact frozen descriptor groups and freeze order.
PROHIBITED_EXTRAPOLATION: Do not claim that an equivariant GNN was implemented or tested.
-->

DDO-02B generated 384 entirely new complete cases, balanced as 96 per F1-F4 family, using new deterministic phases and disorder realizations. The formal registry recorded zero field-lineage overlap with DDO-01D, and exactly 49,152 fresh particle samples entered the requalification.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REQUAL-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo02b_case_registry.json;data/ddo02b_identifiability/ddo02b_metrics.json
EVIDENCE_SHA256: 5588bcc92c0db124481187c17c1e313ef308cddfc75968f152107a4abb1264b4;551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582
SCIENTIFIC_STATUS: FROZEN_FRESH_DESIGN
PERMITTED_WORDING: State exact case balance, sample count, and zero lineage overlap.
PROHIBITED_EXTRAPOLATION: Do not reuse the 512 development cases as fresh formal evidence.
-->

For density rate at the formal expanded C3/L3 combination, DNN P90 was 8.202 and the best fixed oracle NRMSE was 0.5481, exceeding the frozen limits of 0.60 and 0.50, respectively. Density rate therefore failed fresh H3 despite having previously passed H1 and the qualified H2 disorder scope.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REQUAL-P02
EVIDENCE_ARTIFACT: data/ddo02b_identifiability/ddo02b_metrics.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json
EVIDENCE_SHA256: 551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c
SCIENTIFIC_STATUS: FROZEN_FRESH_H3_FAIL
PERMITTED_WORDING: Report the exact density-rate failure metrics and distinguish H1/H2 from H3.
PROHIBITED_EXTRAPOLATION: Do not use H1/H2 PASS to repair the H3 verdict.
-->

For pressure-gradient acceleration, DNN P90 was 45.54, conditional-variance upper95 was 1.070, and oracle NRMSE was 1.010. Each value exceeded its frozen H3 limit, and the component remained H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE on fresh evidence.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REQUAL-P03
EVIDENCE_ARTIFACT: data/ddo02b_identifiability/ddo02b_metrics.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json
EVIDENCE_SHA256: 551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c
SCIENTIFIC_STATUS: FROZEN_FRESH_H3_FAIL
PERMITTED_WORDING: Report the exact pressure metrics and component verdict.
PROHIBITED_EXTRAPOLATION: Do not attribute the failure to a single descriptor, disorder variable, or architecture.
-->

For viscosity-Laplacian acceleration, DNN median was 0.2773, DNN P90 was 26.88, conditional-variance upper95 was 0.4042, and oracle NRMSE was 1.049. These values exceeded their corresponding frozen limits, so viscosity also failed fresh H3.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REQUAL-P04
EVIDENCE_ARTIFACT: data/ddo02b_identifiability/ddo02b_metrics.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json
EVIDENCE_SHA256: 551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c
SCIENTIFIC_STATUS: FROZEN_FRESH_H3_FAIL
PERMITTED_WORDING: Report the exact viscosity metrics and fresh verdict.
PROHIBITED_EXTRAPOLATION: Do not generalize to every viscosity discretization or every observable representation.
-->

The frozen observable-frame fallback was triggered in exactly 515,904 of 627,264 particle environments (82.246710%), documenting high directional degeneracy for this construction. Because all three primary mappings failed fresh H3, H4 remained NOT_QUALIFIED, no H5 component was authorized, and the tested online route was closed.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: REQUAL-P05
EVIDENCE_ARTIFACT: data/ddo02b_identifiability/ddo02b_observable_feature_schema.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 3abde8010d1eb99112af74406fffab164ecaa20aa8ba4df3e3c8d907440c28d5;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_FRESH_LIMITATION_AND_CLOSURE
PERMITTED_WORDING: Report the exact fallback numerator/denominator and route-specific closure.
PROHIBITED_EXTRAPOLATION: Do not claim that all equivariant representations fail or that H4/H5 failed.
-->


**[FIGURES 7-8 NEAR HERE; TABLE 3 NEAR HERE]**

## 9. Discussion

The evidence separates magnitude, systematic dependence, and observable determination. The defects were far above qualified uncertainty, and several components exhibited systematic scaling, yet neither the initial nor the expanded deployment-compatible instantaneous representation satisfied H3. The central result is therefore that resolvability and scaling do not imply identifiability from the tested observables.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json;data/identifiability/ddo01e_formal_verdicts.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c
SCIENTIFIC_STATUS: FROZEN_CROSS_STAGE_SYNTHESIS
PERMITTED_WORDING: Use the core manuscript statement within the tested scope.
PROHIBITED_EXTRAPOLATION: Do not state a universal theorem for SPH defects or inverse problems.
-->

Qualified coverage in both identifiability cycles makes a simple lack of nearby feature samples insufficient as the sole explanation. The remaining evidence is consistent with observable conditional ambiguity, expressed through heavy disagreement tails, component-dependent conditional variance, weak oracle performance, and family sensitivity. (Bellman and Åström, 1970; Stuart, 2010).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P02
EVIDENCE_ARTIFACT: data/identifiability/ddo01e_metrics.json;data/ddo02b_identifiability/ddo02b_metrics.json;publication/failure_taxonomy.md;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: 871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb;551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582;0af5609d7ee6603f001e0260ea70959394096ff81d4b051a5f081d02b991a69f;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: FROZEN_INTERPRETATION_WITH_VERIFIED_EXTERNAL_CONTEXT
PERMITTED_WORDING: Describe ambiguity as supported by the frozen diagnostics.
PROHIBITED_EXTRAPOLATION: Do not claim an architecture-independent impossibility result.
-->

The scaling and identifiability evidence are both component-specific. Density rate retained systematic scaling under the tested disorder scope but still failed fresh H3, whereas pressure and viscosity had regular-only formal H2 scope and different ambiguity signatures. This contrast shows why a single descriptor expansion or a total-acceleration diagnostic cannot stand in for componentwise qualification.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P03
EVIDENCE_ARTIFACT: 06_manifests/ddo01cr_manifest.json;07_reports/ddo01e_disorder_mechanism_report.md;data/ddo02b_identifiability/ddo02b_metrics.json
EVIDENCE_SHA256: 44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;42c5c0dace911df53b3c03ff8c4c446bcd4c8d016dd85039b45b860ead67bf3a;551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582
SCIENTIFIC_STATUS: FROZEN_COMPONENTWISE_SYNTHESIS
PERMITTED_WORDING: Compare component scopes without changing their separate verdicts.
PROHIBITED_EXTRAPOLATION: Do not impose a shared mechanism or scaling exponent across components.
-->

The prospective redesign is informative precisely because development evidence and fresh qualification were separated. Directional and component-specific hypotheses were selected from consumed evidence, frozen in CA-06, and then tested on new lineages without post-target descriptor adjustment. The high frame-degeneracy rate limits that particular directional construction, while leaving other equivariant or temporal formulations untested. (Satorras et al., 2021).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P04
EVIDENCE_ARTIFACT: data/ddo02a/attribution_metrics.json;06_manifests/ca06_manifest.json;06_manifests/ddo02b_case_registry.json;data/ddo02b_identifiability/ddo02b_observable_feature_schema.json;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: f2dca85e6c0e1db38aed3f32eca90a12375bc60af21a8dd544acc07b2d4c1a10;9b238af878ae9a8bb64166631abd99e30ca2c5d66d3535781085de86953f033f;5588bcc92c0db124481187c17c1e313ef308cddfc75968f152107a4abb1264b4;3abde8010d1eb99112af74406fffab164ecaa20aa8ba4df3e3c8d907440c28d5;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: FROZEN_REDESIGN_INTERPRETATION_WITH_VERIFIED_EXTERNAL_CONTEXT
PERMITTED_WORDING: Emphasize prospective separation and the construction-specific limitation.
PROHIBITED_EXTRAPOLATION: Do not claim that equivariant GNNs or temporal observables cannot help.
-->

An upstream identifiability gate can prevent architecture search from being used to answer a question that the available inputs do not support. In this project, the gate led to disciplined closure before neural training, optimization, time integration, rollout, or solver-in-loop claims were attempted. (Ioannidis, 2022; Sandve et al., 2013).

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P05
EVIDENCE_ARTIFACT: 06_manifests/ddo02z_final_status_ledger.json;publication/literature/citation_claim_map.csv
EVIDENCE_SHA256: 0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a;ee11699c64ce05fe80719f01baf494d672d892f8b45dbe5c107fe3e769ce388c
SCIENTIFIC_STATUS: FROZEN_GOVERNANCE_INTERPRETATION_WITH_VERIFIED_EXTERNAL_CONTEXT
PERMITTED_WORDING: State the project-specific value of prospective gating and closure.
PROHIBITED_EXTRAPOLATION: Do not claim that this exact hierarchy is the only valid workflow for computational science.
-->

The evidence is restricted to fixed-time, two-dimensional, periodic, manufactured-field evaluations of the frozen SPH operators and observables. Boundary information, temporal history, latent state, alternative sensors, dynamic integration, learned representations, and solver feedback were not tested. The target SVD is an empirical covariance diagnostic only, and high-resolution SPH was not used as truth.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P06
EVIDENCE_ARTIFACT: 00_project_contract/ddo_project_charter.md;data/identifiability/ddo01e_target_subspace_diagnostic.json;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 73695788de6a093db17dd016ef67906098a3cef40dc2b8bf96a68058f41c2db6;e2a06889a503390a47e3e19b7164ad09135dd9575cc643d32a508bf55a381d58;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_LIMITATION
PERMITTED_WORDING: List the untested domains and preserve the reference/subspace boundaries.
PROHIBITED_EXTRAPOLATION: Do not infer that temporal information cannot help or that the target manifold is two-dimensional.
-->

SPH-DDO is a publication project distinct from SPH-PIO. The present study terminates at pre-learning identifiability, whereas SPH-PIO concerns a separate trained conservative-correction route and its optimizer and support evidence; shared static SPH foundations should be cross-referenced without merging primary evidence or claims.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: DISC-P07
EVIDENCE_ARTIFACT: publication/cross_paper_relation_memo.md
EVIDENCE_SHA256: 7a5681c710e5a899f14cb5df66e8d41cdd9ab5d094f96823239ecab7579537aa
SCIENTIFIC_STATUS: FROZEN_PUBLICATION_BOUNDARY
PERMITTED_WORDING: State the distinct questions and non-overlap rule.
PROHIBITED_EXTRAPOLATION: Do not merge the manuscripts or import SPH-PIO training results into SPH-DDO.
-->


**[TABLE 4 NEAR HERE: failure taxonomy]**

## 10. Conclusions

This study qualified a fixed-time SPH spatial-defect reference, established signal resolvability, identified component- and disorder-dependent scaling, and then tested deployable-observable identifiability before learning. The first representation failed H3, and the prospectively redesigned representation again failed all three primary dynamic mappings on fresh evidence.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: CONC-P01
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json;data/identifiability/ddo01e_formal_verdicts.json;06_manifests/ddo02b_case_registry.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e;5588bcc92c0db124481187c17c1e313ef308cddfc75968f152107a4abb1264b4;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c
SCIENTIFIC_STATUS: FROZEN_FINAL_SYNTHESIS
PERMITTED_WORDING: Summarize the completed evidence chain and repeated fresh H3 failure.
PROHIBITED_EXTRAPOLATION: Do not extend the conclusion beyond the tested instantaneous online route.
-->

A spatial discretization defect can be numerically resolvable and exhibit systematic scaling without being identifiable from the tested deployment-compatible instantaneous observables. This distinction is the principal scientific result of SPH-DDO.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: CONC-P02
EVIDENCE_ARTIFACT: 06_manifests/ddo01br_manifest.json;06_manifests/ddo01cr_manifest.json;data/ddo02b_identifiability/ddo02b_formal_verdicts.json;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875;44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef;6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_CORE_CONCLUSION
PERMITTED_WORDING: Use this sentence as the central manuscript statement.
PROHIBITED_EXTRAPOLATION: Do not rewrite it as a claim that all SPH defects are unlearnable.
-->

The final route status is ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED. H4 is NOT_QUALIFIED, H5 and H6 are NOT_AUTHORIZED, and no neural training was performed because the upstream H3 qualification prerequisite was not met. The evidence is frozen for publication, and no DDO-03 continuation is authorized.

<!-- EVIDENCE_ANNOTATION
CLAIM_ID: CONC-P03
EVIDENCE_ARTIFACT: publication/final_hypothesis_ledger.csv;06_manifests/ddo02z_final_status_ledger.json
EVIDENCE_SHA256: 694841a5ff154ebaefa39207a526739eee619a8db6fb53d02447b92d92ba0743;0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a
SCIENTIFIC_STATUS: FROZEN_TERMINAL_STATE
PERMITTED_WORDING: State the exact terminal and authorization vocabulary.
PROHIBITED_EXTRAPOLATION: Do not state that H4, H5, H6, neural SPH, GNNs, or Transformers failed.
-->

## References

1. Quinlan, N. J., Basa, M. & Lastiwka, M. Truncation error in mesh-free particle methods. *International Journal for Numerical Methods in Engineering* **66**, 2064-2085 (2006). https://doi.org/10.1002/nme.1617
2. Sigalotti, L. Di G., Klapp, J., Rendón, O., Vargas, C. A. & Peña-Polo, F. On the kernel and particle consistency in smoothed particle hydrodynamics. *Applied Numerical Mathematics* **108**, 242-255 (2016). https://doi.org/10.1016/j.apnum.2016.05.007
3. Litvinov, S., Hu, X. Y. & Adams, N. A. Towards consistence and convergence of conservative SPH approximations. *Journal of Computational Physics* **301**, 394-401 (2015). https://doi.org/10.1016/j.jcp.2015.08.041
4. Bar-Sinai, Y., Hoyer, S., Hickey, J. & Brenner, M. P. Learning data-driven discretizations for partial differential equations. *Proceedings of the National Academy of Sciences* **116**, 15344-15349 (2019). https://doi.org/10.1073/pnas.1814058116
5. Um, K., Brand, R., Fei, Y. (R.), Holl, P. & Thuerey, N. Solver-in-the-Loop: Learning from Differentiable Physics to Interact with Iterative PDE-Solvers. *Advances in Neural Information Processing Systems* **33**, 6111-6122 (2020). https://proceedings.neurips.cc/paper/2020/hash/43e4e6a6f341e00671e123714de019a8-Abstract.html
6. Woodward, M. *et al.* Physics-informed machine learning with smoothed particle hydrodynamics: Hierarchy of reduced Lagrangian models of turbulence. *Physical Review Fluids* **8**, 054602 (2023). https://doi.org/10.1103/PhysRevFluids.8.054602
7. Amato, E., Zago, V. & Del Negro, C. A physically consistent AI-based SPH emulator for computational fluid dynamics. *Nonlinear Engineering* **13**, 20220359 (2024). https://doi.org/10.1515/nleng-2022-0359
8. Winchenbach, R. & Thuerey, N. diffSPH: Differentiable smoothed particle hydrodynamics for hybrid machine learning solutions in fluid mechanics. *Journal of Computational Physics* **555**, 114769 (2026). https://doi.org/10.1016/j.jcp.2026.114769
9. Bellman, R. & Åström, K. J. On structural identifiability. *Mathematical Biosciences* **7**, 329-339 (1970). https://doi.org/10.1016/0025-5564(70)90132-X
10. Stuart, A. M. Inverse problems: A Bayesian perspective. *Acta Numerica* **19**, 451-559 (2010). https://doi.org/10.1017/S0962492910000061
11. Satorras, V. G., Hoogeboom, E. & Welling, M. E(n) Equivariant Graph Neural Networks. *Proceedings of the 38th International Conference on Machine Learning*, PMLR **139**, 9323-9332 (2021). https://proceedings.mlr.press/v139/satorras21a.html
12. Ioannidis, J. P. A. Pre-registration of mathematical models. *Mathematical Biosciences* **345**, 108782 (2022). https://doi.org/10.1016/j.mbs.2022.108782
13. Sandve, G. K., Nekrutenko, A., Taylor, J. & Hovig, E. Ten Simple Rules for Reproducible Computational Research. *PLoS Computational Biology* **9**, e1003285 (2013). https://doi.org/10.1371/journal.pcbi.1003285
