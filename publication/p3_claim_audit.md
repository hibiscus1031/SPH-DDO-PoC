# Publication P3 claim audit

## Audit disposition

**Result:** PASS  
**Final status:** `SPH_DDO_PUBLICATION_FIGURES_TABLES_AND_METHODS_COMPLETE`  
**Authorized scope:** publication reconstruction only

The Methods patch, six-figure set, reduced table set, v0.4 manuscript pair, captions, and claim maps preserve the frozen SPH-DDO scientific state. No SPH calculation, new descriptor, H3 analysis, scientific metric, model, optimizer, rollout, time integration, or solver result was created.

## Interrupted-run recovery

The continuation audit reused the following valid artifacts after confirming existence, readability, source traceability, scientific consistency, and visual integrity:

- `supplementary_methods_v0_1.md` and `method_definition_audit.md`;
- the six figures in SVG, PDF, TIFF, and PNG formats;
- `manuscript_v0_4_figure_integrated.md` and its annotated counterpart;
- `p3_main_figure_captions.md` and `p3_main_tables.md`.

Only the unfinished figure-panel claim map, table-row claim map, visual QA report, claim audit, and final cross-artifact checks were resumed after the interruption. Valid rendered figures were not deleted or regenerated during continuation.

## Required-output completeness

| Required output | Audit result |
|---|---|
| Six main figures × SVG/PDF/TIFF/PNG | 24/24 present and readable |
| `supplementary_methods_v0_1.md` | Present; ten required definitions |
| `method_definition_audit.md` | Present; source hashes verified |
| `manuscript_v0_4_figure_integrated.md` | Present |
| `manuscript_v0_4_figure_integrated_annotated.md` | Present |
| `p3_main_figure_captions.md` | Present; six captions |
| `p3_main_tables.md` | Present; two required and one optional main table |
| `p3_figure_panel_claim_map.csv` | Present; 30 claim bindings covering 22 panels |
| `p3_table_claim_map.csv` | Present; 34 claim bindings covering 15 table rows |
| `p3_visual_qa_report.md` | Present |
| `p3_claim_audit.md` | Present |

## Evidence and claim integrity

| Audit | Result |
|---|---|
| Figure panel coverage | 22/22 panels |
| Figure-panel claim bindings | 30 |
| Figure-map artifact/SHA-256 pairs | 56/56 verified |
| Main-table row coverage | 15/15 rows |
| Table-row claim bindings | 34 |
| Table-map artifact/SHA-256 pairs | 59/59 verified |
| Missing evidence files | 0 |
| Evidence SHA-256 mismatches | 0 |
| Claim IDs outside the frozen 49-ID set | 0 |
| Unique frozen claim IDs used in P3 maps | 24 |

Every panel and every main-table row has at least one binding to a frozen claim ID, evidence artifact, artifact SHA-256, permitted wording, and prohibited extrapolation. Multiple bindings are retained where one visual panel or row combines separately bounded claims.

## Frozen scientific-state audit

| State | Required P3 disposition | Audit result |
|---|---|---|
| H1 | qualified over frozen scopes | Preserved |
| H2 | component- and disorder-dependent | Preserved |
| H3 | fresh failure for all three primary dynamic mappings | Preserved |
| H4 | not qualified / not interpreted | Preserved; never recoded as failure |
| H5/H6 | not authorized / not initiated | Preserved; never recoded as failure |
| Neural training | none because the H3 prerequisite was unmet | Preserved explicitly |
| Final route | instantaneous observable route not supported | Preserved in reader-facing language |

The principal conclusion remains: a spatial discretization defect may be numerically resolvable and exhibit systematic scaling without satisfying identifiability from the tested deployment-compatible instantaneous observables.

## Methods completeness audit

The Supplementary Methods defines:

1. operational identifiability and its distinction from classical structural-identifiability proof;
2. the additive CA-01 float64 numerical/reference uncertainty;
3. H1 case RMS, equal-case component RMS, (U_c), (R_c), and bootstrap (L_{95,c});
4. H2 local log slopes, propagated intervals, monotonicity fraction, and replicate-dispersion gate;
5. H3 nearest-neighbour disagreement, median and P90, conditional variance, oracle NRMSE and improvement, coverage, family robustness, and all-gates decision;
6. target-free lineage folds and equal-case/equal-fold weighting;
7. deterministic sampling of 128 particles per case;
8. the distinction between 49,152 formal fresh H3 samples and 627,264 full particle environments;
9. the normalized-eigenvalue-gap frame-degeneracy definition and deterministic fallback;
10. consumed development evidence versus fresh formal evidence.

All frozen thresholds are unchanged. H1 ratios are explicitly described as separation from qualified numerical/reference uncertainty, not physical signal-to-noise.

## Figure audit

- Figures 1–6 match the required six-figure structure.
- All captions state evidence scope, statistical meaning, and qualification boundaries where applicable.
- Figure 2 slopes are labelled descriptive rather than convergence orders.
- Figure 3 uses scientific family names and retains favorable initial criteria.
- Figure 4 retains favorable medians and displays only frozen attribution evidence.
- Figure 5 states `515,904 / 627,264 = 82.246710%` and distinguishes the full frame audit from the 49,152-sample H3 population.
- Figure 6 displays all seven applicable frozen H3 criteria and limits for every primary mapping.
- SVG text remains editable; PDFs are vector and readable; TIFFs are 600 dpi; PNG previews are 300 dpi.
- No manual raster edit or non-Python visual backend was used.

## Table-value audit

Main Table 1 uses reader-facing prerequisite language: passed, did not satisfy criteria, not interpreted, and not initiated. Main Table 2 transcribes all initial and fresh disagreement, conditional-variance, oracle-error, oracle-improvement, family-robustness, and coverage values at approved publication precision. Thirty-nine representative numeric transcription tokens were reconciled with the frozen metric files with zero omission or mismatch. Main Table 3 separates evidence-set purpose and role and does not mix H1 metric values into evidence design.

The detailed H1 ledger, H2 track ledger, failure taxonomy, descriptor dictionary, fold quality control, support-ratio diagnostics, and target singular-value diagnostic are assigned to supplementary material.

## Manuscript-pair audit

| Check | Result |
|---|---|
| Reader and annotated scientific prose after annotation removal | Identical |
| Annotated claim mappings | 49/49 unique and unchanged from v0.3 |
| Figure placeholders | Exactly Figures 1–6 in order |
| Main-table placeholders | Exactly Tables 1–3 in order |
| Operational-identifiability sentence | Present |
| H1 uncertainty-meaning clarification | Present |
| 49,152 versus 627,264 population clarification | Present |
| SHA-256 values in reader manuscript | Absent |

## Prohibited-claim audit

| Prohibited implication | Result |
|---|---|
| H4, H5, or H6 described as failed experiments | Absent |
| Trained-model or neural-performance implication | Absent |
| Universal non-identifiability or unlearnability | Absent |
| Classical structural-identifiability proof | Explicitly disclaimed |
| Target-manifold or intrinsic-dimension claim | Absent |
| High-resolution SPH treated as truth | Absent |
| Equivariant or graph-neural failure inferred from frame fallback | Absent |
| Temporal, rollout, boundary, or solver qualification | Absent |
| SPH-DDO merged with SPH-PIO | Absent |
| Unsupported priority claim | Absent |

## Final determination

All required P3 artifacts exist and pass source-hash, source-to-panel, table-value, manuscript-consistency, prohibited-claim, and visual-export audits. Publication P3 is complete without changing the frozen scientific state.
