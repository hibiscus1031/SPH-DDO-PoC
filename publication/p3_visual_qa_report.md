# P3 visual QA report

## Disposition

**Result:** PASS  
**Backend:** Python/Matplotlib only  
**Main-figure count:** 6  
**Final width:** 183 mm for every figure

All visual outputs were generated directly from frozen source ledgers or metric files. No manual raster edit, external graphics editor, alternative visual backend, scientific recomputation, or post hoc value adjustment was used.

## Figure contracts and review risks

| Figure | Archetype | Core visual conclusion | Principal review risk controlled |
|---|---|---|---|
| 1 | Schematic-led composite | The fixed-time target passes through an ordered pre-learning qualification chain that stops at fresh H3 | H4–H6 are shown as prerequisite states, not failed experiments; reference information is blocked from observables |
| 2 | Asymmetric quantitative grid | Resolvability is universal over qualified scopes, while scaling is component- and disorder-dependent | H1 is not labelled physical signal-to-noise; slopes are not convergence orders; adverse interpolation/disorder cells remain visible |
| 3 | Schematic-led quantitative composite | Balanced development evidence and lineage-held-out diagnostics precede the initial all-gates decision | The atlas occupies only part of the figure; scientific family names replace internal family codes; favorable criteria remain visible |
| 4 | Quantitative grid | Initial ambiguity is component-, family-, and disorder-structured, and simple consistency augmentation is not a uniform rescue | Low medians are retained beside failing tails; display-normalized panels expose their frozen limits; diagnostic oracles are not presented as trained corrections |
| 5 | Schematic-led composite | Consumed diagnosis, prospective descriptor freeze, and fresh evidence are separated | The 49,152 formal-sample population is distinct from the 627,264 full-environment frame audit; frame fallback is not an equivariant-GNN claim |
| 6 | Quantitative hero matrix | None of the three primary mappings satisfies every fresh operational-identifiability criterion | Every applicable metric and limit appears; P/N labels preserve grayscale interpretation; no neural-performance implication is shown |

## Frozen source integrity

| Plot source | SHA-256 | Use |
|---|---|---|
| `07_reports/ddo01br_component_h1_ledger.csv` | `d6c7fe5885bd878409350b6acdde71f106a43e171775b745d8e6a15fe81199b1` | Figure 2 H1 values |
| `07_reports/ddo01cr_component_h2_ledger.csv` | `6c423e899fa055e198af0290668317df25f4ac07bf0a80de1def8328ef879cde` | Figure 2 H2 qualification and monotonicity |
| `data/scaling_f1/ddo01cr_scaling_evidence.csv` | `be73d219362f0f8c791f8cbe4ebbf6c47eff1b866c96ddb9c26d04de4e241eb6` | Figure 2 density-rate refinement tracks |
| `data/identifiability/ddo01e_metrics.json` | `871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb` | Figures 3–4 initial formal metrics |
| `data/identifiability/ddo01e_figure_source_data.csv` | `3619a8928aae81cffa105688fc767315f6a27baddb5dd029e2aedad2cde866c8` | Figure 4 family and consistency diagnostics |
| `data/ddo02b_identifiability/ddo02b_metrics.json` | `551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582` | Figures 5–6 fresh formal metrics and sample count |
| `data/ddo02b_identifiability/ddo02b_observable_feature_schema.json` | `3abde8010d1eb99112af74406fffab164ecaa20aa8ba4df3e3c8d907440c28d5` | Figure 5 full-particle frame audit |
| `08_scripts/publication_p3_figures.py` | `27943463d5efb1fdb3bd9c1b48abd2c9dc20d89117e16b2ba84f17c53544c9bf` | Exclusive plotting and export provenance |

Every listed source exists and matches its recorded SHA-256. The script reads the frozen artifacts directly. No mock, imputed, or newly simulated value is present.

## Authorized display transformations

- Figure 2 uses logarithmic axes for H1 separation ratios and frozen scaling responses.
- Figure 4b divides conditional-variance upper bounds and oracle NRMSE by their respective frozen upper limits to share one plotting axis. Untransformed values are printed on the bars.
- Figure 4d divides conditional variance by its frozen point limit of 0.25 for display.
- Figure 5c partitions the frozen frame-audit denominator into fallback and non-fallback counts; the non-fallback count is the arithmetic complement shown only to complete the stacked population display.
- Figure 6 colors individual criteria by direct comparison with their preregistered limits and prints both the frozen value and limit in each cell.

These are traceable publication encodings, not new scientific metrics or qualification decisions.

## Export audit

| Figure | Width × height | PNG preview | TIFF submission raster | SVG | PDF |
|---|---|---|---|---|---|
| 1 | 183 × 125 mm | 2161 × 1476 px, 300 dpi | 4322 × 2952 px, 600 dpi | readable; editable text | readable; one vector page |
| 2 | 183 × 145 mm | 2161 × 1712 px, 300 dpi | 4322 × 3425 px, 600 dpi | readable; editable text | readable; one vector page |
| 3 | 183 × 135 mm | 2161 × 1594 px, 300 dpi | 4322 × 3188 px, 600 dpi | readable; editable text | readable; one vector page |
| 4 | 183 × 150 mm | 2161 × 1771 px, 300 dpi | 4322 × 3543 px, 600 dpi | readable; editable text | readable; one vector page |
| 5 | 183 × 135 mm | 2161 × 1594 px, 300 dpi | 4322 × 3188 px, 600 dpi | readable; editable text | readable; one vector page |
| 6 | 183 × 135 mm | 2161 × 1594 px, 300 dpi | 4322 × 3188 px, 600 dpi | readable; editable text | readable; one vector page |

All 24 requested exports exist, are nonempty, and reopen successfully. SVG files retain text nodes, PDFs contain one readable page, and TIFF metadata records 600 dpi.

## Visual inspection

The six PNG previews were inspected after rendering. A first pass identified crowded schematic labels in Figures 3 and 5, one clipped value label in Figure 4, and a grayscale-readability opportunity in Figure 6. The Python source was patched locally, and all four formats were regenerated. The second pass confirmed:

- white backgrounds and consistent sans-serif typography;
- visible lowercase panel labels;
- no overlapping scientific labels or clipped quantitative values;
- restrained color-blind-readable blue, teal, purple, orange, and neutral palette;
- symbols, line styles, P/N letter codes, and printed values that remain interpretable without color;
- threshold lines distinct from the data but not visually dominant;
- no gradients, three-dimensional decoration, or stage-dashboard styling;
- no redundant per-panel legends where direct labels or a shared key were sufficient;
- explicit evidence scope and interpretation boundaries in the captions.

## Final visual determination

The six-figure set satisfies the P3 figure contract. It visualizes only frozen evidence and supports the route-specific conclusion without introducing a new analysis or implying failure of untested neural, equivariant, temporal, or solver-integrated routes.
