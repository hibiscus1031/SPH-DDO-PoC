# P3 main tables

## Table 1. Final componentwise qualification hierarchy

**Caption.** Reader-facing qualification state over the frozen evidence scopes. Internal hypothesis labels are given parenthetically for cross-reference. “Not interpreted” and “not initiated” are prerequisite states and must not be read as failed experiments.

| Component | Scientific role | Signal resolvability (H1) | Controlled scaling (H2) | Operational identifiability (H3) | Locality (H4) | Representation learning (H5) | Generalization (H6) |
|---|---|---|---|---|---|---|---|
| Interpolation density | Algebraic diagnostic | Passed over the qualified excited-case scope | Did not satisfy regular or tested-disorder criteria | Diagnostic mapping did not satisfy criteria; not a primary dynamic route | Not interpreted | Not initiated | Not initiated |
| Density rate | Primary dynamic component | Passed over the qualified excited-case scope | Passed in regular and tested-disorder scopes | Did not satisfy fresh criteria | Not interpreted | Not initiated | Not initiated |
| Pressure-gradient acceleration | Primary dynamic component | Passed over the qualified excited-case scope | Passed in the regular scope only | Did not satisfy fresh criteria | Not interpreted | Not initiated | Not initiated |
| Viscosity-Laplacian acceleration | Primary dynamic component | Passed over the qualified excited-case scope | Passed in the regular scope only | Did not satisfy fresh criteria | Not interpreted | Not initiated | Not initiated |
| Total acceleration | Derived pressure-plus-viscosity diagnostic | Passed over the qualified scope | Passed in the regular scope only | Not independently evaluated | Not applicable as an independent route | Not initiated | Not initiated |

## Table 2. Initial versus fresh operational-identifiability metrics

**Caption.** Frozen C3/L3 metrics for the three primary dynamic mappings. Limits are nearest-neighbour disagreement median (leq0.25), P90 (leq0.60), conditional-variance upper 95% (leq0.35), diagnostic-oracle NRMSE (leq0.50), mean-baseline improvement (geq0.20), worst-family NRMSE (leq0.75), and coverage (geq0.90). Every applicable criterion must pass. Values are shown at approved publication precision.

| Evidence cycle | Component | NN median | NN P90 | Cvar upper 95% | Oracle NRMSE | Improvement | Worst-family NRMSE | Coverage | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Development | Density rate | 0.0006954 | 2.653 | 0.1036 | 0.4634 | 0.5366 | 0.8948 | 0.9526 | Did not satisfy all criteria |
| Development | Pressure-gradient acceleration | 0.01600 | 3.665 | 1.399 | 1.044 | -0.04397 | 1.075 | 0.9526 | Did not satisfy all criteria |
| Development | Viscosity-Laplacian acceleration | 0.1408 | 10.70 | 0.3287 | 1.049 | -0.04905 | 1.038 | 0.9526 | Did not satisfy all criteria |
| Fresh | Density rate | 0.001276 | 8.202 | 0.1489 | 0.5481 | 0.4519 | 1.067 | 0.9358 | Did not satisfy all criteria |
| Fresh | Pressure-gradient acceleration | 0.0008044 | 45.54 | 1.070 | 1.010 | -0.009726 | 1.004 | 0.9358 | Did not satisfy all criteria |
| Fresh | Viscosity-Laplacian acceleration | 0.2773 | 26.88 | 0.4042 | 1.049 | -0.04904 | 1.265 | 0.9358 | Did not satisfy all criteria |

## Table 3. Evidence-set design

**Caption.** Frozen evidence sets and their distinct publication roles. H1 and H2 use complete-case target statistics rather than the later 128-particle formal H3 subsampling rule.

| Evidence set | Cases | Purpose | Family structure | Formal particle samples | Evidence role |
|---|---:|---|---|---:|---|
| H1 pilot/requalification | 24 | Numerical/reference and component signal qualification | F1 isolated probes across resolution, mode, and layout | Not applicable; complete-case RMS | Qualified signal evidence |
| H2 scaling | 204 | Refinement, spectral, and disorder-scope qualification | F1 scientific tracks with regular/jitter matched replicates | Not applicable; complete-case RMS | Qualified componentwise scaling evidence |
| Development atlas | 512 | Initial operational-identifiability assessment and failure attribution | 128 cases in each of four mechanism families | 65,536 | Development evidence; consumed after redesign diagnosis |
| Fresh requalification | 384 | Prospective test of the frozen 30-descriptor expansion | 96 cases in each of four mechanism families; zero development-lineage overlap | 49,152 | Fresh formal evidence |

## Supplementary-table allocation

The detailed H1 component ledger, full H2 track ledger, failure taxonomy, descriptor dictionary, fold quality control, support-ratio diagnostics, and target singular-value diagnostic are assigned to the Supplementary Information. The target singular-value analysis remains an empirical covariance diagnostic and is not a manifold or intrinsic-dimension claim.
