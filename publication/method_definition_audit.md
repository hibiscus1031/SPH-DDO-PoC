# Method-definition audit

## Disposition

**Result:** PASS  
**Scope:** publication Methods completion from frozen contracts only

The supplement adds definitions and reporting boundaries; it does not add a method, threshold, metric, case, descriptor, or scientific result.

## Definition traceability

| Required definition | Frozen source | SHA-256 | Audit result |
|---|---|---|---|
| Operational identifiability and interpretation boundary | `04_identifiability_contract/identifiability_metrics.md`; `00_project_contract/amendments/ca05_h3_h4_identifiability_locality_semantics.md` | `eae94ab070824918fed537e330e666645e99d4c35b69bccbd26dd87679e75ccc`; `a940562ed2a589bb4864c40d8674ce57940ee03c2a75206b2724dc747d639da3` | Complete; explicitly distinguished from structural-identifiability proof |
| Numerical/reference uncertainty | `00_project_contract/amendments/ca01_numerical_qualification_contract.md` | `8029eee814efac3cf8dc82de7e60495ee33352890ca60a0944de50991b3c2a70` | Complete additive construction; float32 retained as non-gating |
| H1 case RMS, component RMS, (U_c), (R_c), and bootstrap (L_{95,c}) | `00_project_contract/amendments/ca02_h1_signal_semantics_contract.md` | `284fe579ff8445a9a3efdbd1bcc36060f15071cfd131ec18719e698640f11756` | Complete; equal-case weighting and unexcited exclusion stated |
| H2 slopes, propagated interval, monotonicity, and replicate dispersion | `00_project_contract/amendments/ca03_h2_scaling_semantics_and_design.md` | `17afe22369d020041142e8b72a27696fbfcbca7a70bcd30781dcd099277a1355` | Complete; slopes remain descriptive |
| H3 disagreement, Cvar, oracle diagnostics, improvement, coverage, and all-gates decision | `00_project_contract/amendments/ca05_h3_h4_identifiability_locality_semantics.md`; `04_identifiability_contract/prospective_gates.md` | `a940562ed2a589bb4864c40d8674ce57940ee03c2a75206b2724dc747d639da3`; `cb83636e0595d89b9f87bbb79b55b1042634ab528e499db82784271057e3ca17` | Complete; every frozen threshold retained |
| Lineage-fold construction and equal-case weighting | `00_project_contract/amendments/ca05_h3_h4_identifiability_locality_semantics.md` | `a940562ed2a589bb4864c40d8674ce57940ee03c2a75206b2724dc747d639da3` | Complete; field-level separation stated |
| 128-particle-per-case formal sample | `00_project_contract/amendments/ca05_h3_h4_identifiability_locality_semantics.md`; `06_manifests/ddo02b_particle_sample_registry.json` | `a940562ed2a589bb4864c40d8674ce57940ee03c2a75206b2724dc747d639da3`; `092b6ad937621ced65bab808841950ca3dd4ef4cdf73f41738cce0116210cf08` | Complete |
| 49,152 formal samples versus 627,264 frame-audit environments | `data/ddo02b_identifiability/ddo02b_metrics.json`; `data/ddo02b_identifiability/ddo02b_observable_feature_schema.json` | `551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582`; `3abde8010d1eb99112af74406fffab164ecaa20aa8ba4df3e3c8d907440c28d5` | Complete; populations and purposes are distinct |
| Frame-degeneracy definition | `00_project_contract/amendments/ca06_expanded_observable_contract.md` | `3591222d22bcc1c6a47f151961bcd7cd15710f96ad50e8cd5692de278d97b0e9` | Complete; normalized eigengap (<10^{-6}) and identity fallback stated |
| Fresh versus consumed evidence roles | `00_project_contract/amendments/ca06_expanded_observable_contract.md`; `06_manifests/ddo02b_manifest.json` | `3591222d22bcc1c6a47f151961bcd7cd15710f96ad50e8cd5692de278d97b0e9`; `56fb9259a9abbc702684028485cce61b3f00fada37febe56778bc35492fc334d` | Complete; zero lineage overlap and 96 cases per family stated |

## Threshold audit

| Qualification | Frozen limits retained |
|---|---|
| H1 | (R_c\geq10); (L_{95,c}>5); at least 8 eligible complete cases |
| H2 | (M_{\mathrm{family}}\geq0.75); (D_t<C_t) for every mandatory track; at least 2 tracks, 3 levels, and 3 matched replicates |
| H3 disagreement | median (leq0.25); P90 (leq0.60) |
| H3 conditional variance | point (leq0.25); upper 95% bound (leq0.35) |
| H3 oracle | NRMSE (leq0.50); mean-baseline improvement (geq0.20); every family NRMSE (leq0.75) |
| H3 coverage | (geq0.90) |
| Frame degeneracy | normalized eigenvalue gap (<10^{-6}) |

## Boundary audit

- No classical structural-identifiability proof is claimed.
- No physical signal-to-noise interpretation is assigned to (R_c).
- No H2 slope is called a convergence order.
- No diagnostic oracle is described as a production model.
- No H4 result is inferred after H3 failed.
- No neural training, representation-learning result, generalization result, time integration, or rollout is introduced.
- The 515,904/627,264 fallback statistic is limited to the tested observable-defined directional frame.
