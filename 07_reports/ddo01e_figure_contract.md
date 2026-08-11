# DDO-01E Python figure contract

Core conclusion: The frozen observable descriptor and context ladders do not
satisfy the joint H3 gates, and the unresolved ambiguity is structured by
component, disorder state, and field family.

- Figure archetype: quantitative grid.
- Backend: Python exclusively for drawing, preview, export, and visual QA.
- Target output: journal-ready double-column figures, 183 mm width, white
  background, editable SVG text, PDF, 600-dpi TIFF, and PNG QA preview.
- Evidence hierarchy: formal C3/L3 joint-gate evidence is primary; locality,
  G-to-G+C consistency ablation, matched F4 disorder strata, and F1-F4 strata
  are supporting/robustness evidence.
- Statistics: 512 development cases, 128 target-blind particles per case, five
  lineage-held-out folds; particles reduce within case and cases/folds receive
  equal formal weight. Cvar intervals use 2,000 lineage bootstrap replicates.
- Source data: frozen DDO-01E metric JSON and case-diagnostic CSV; the plotting
  source table is generated from those artifacts.
- Image integrity: no microscopy or raster measurement; plots are generated
  directly from source values without manual edits. PNG is QA only.
- Reviewer risk: a low DNN median can coexist with a failing tail; no panel may
  hide DNN p90, Cvar uncertainty, worst-family NRMSE, or coverage. L3 is an
  information-scope diagnostic and is not presented as a neural architecture.

Panel map:

- `identifiability_ladder`: oracle NRMSE and Cvar across C0-C3/L0-L3 for the
  three primary components, with frozen thresholds.
- `locality_ladder`: C3 evidence over L0-L3, showing why no positive H4 claim is
  available when formal H3 fails.
- `consistency_ablation`: matched F4 C0 versus C1 at L1, separating pressure and
  viscosity and all four disorder states.
- `disorder_stratified_ambiguity`: formal C3/L3 DNN tail and Cvar by F4 disorder
  state.
- `family_stratified_metrics`: formal C3/L3 best-oracle NRMSE and DNN tail for
  F1-F4 without allowing F1 to mask other families.

