# Manuscript v0.3 table shells

All entries below are transcribed from frozen artifacts. Paper-facing values use the approved rounding policy; full precision remains in the cited source ledgers.

## Table 1. Numerical qualification and signal resolvability

**Caption.** Qualification counts and H1 signal metrics for the fixed-time analytical defect. Unexcited pairs are excluded from component aggregation. H1 requires \(R_c\geq10\) and \(L_{95,c}>5\).

| Component or evidence set | Eligible cases | Unexcited cases | \(R_c\) | \(L_{95,c}\) | Qualification |
|---|---:|---:|---:|---:|---|
| Interpolation density | 24 | 0 | \(2.455\times10^{11}\) | \(2.284\times10^{11}\) | H1 pass |
| Density rate | 8 | 16 | \(1.615\times10^{12}\) | \(9.177\times10^{11}\) | H1 pass |
| Pressure-gradient acceleration | 8 | 16 | \(2.194\times10^{12}\) | \(1.643\times10^{12}\) | H1 pass |
| Viscosity-Laplacian acceleration | 16 | 8 | \(1.405\times10^{12}\) | \(1.170\times10^{12}\) | H1 pass |
| Total acceleration | 24 | 0 | \(1.267\times10^{12}\) | \(7.910\times10^{11}\) | H1 pass |
| H1 numerical audit | 24 passed | 0 failed | Maximum derivative discrepancy \(1.776357\times10^{-15}\) | Maximum closure residual 0 | Qualified |
| H2 numerical audit | 204 passed | 0 failed | Maximum derivative discrepancy \(1.421086\times10^{-14}\) | All formal log responses admissible | Qualified |
| Development atlas | 512 passed | 0 failed | Four balanced families | 65,536 formal samples | Development evidence |
| Fresh requalification | 384 passed | 0 failed | Zero lineage overlap | 49,152 formal samples | Fresh evidence |

## Table 2. Componentwise qualification hierarchy

**Caption.** Frozen H1–H6 status and scope by component. `NOT_QUALIFIED` and `NOT_AUTHORIZED` must not be replaced by `FAIL`.

| Component | Role | H1 signal | H2 scaling | H3 identifiability | H4 locality | H5 representation | H6 generalization |
|---|---|---|---|---|---|---|---|
| Interpolation density | Algebraic diagnostic | PASS | FAIL, regular and jittered | Diagnostic fail, not primary route | NOT_QUALIFIED | NOT_AUTHORIZED | NOT_AUTHORIZED |
| Density rate | Primary dynamic | PASS | PASS, regular and tested disorder | FAIL after fresh requalification | NOT_QUALIFIED | NOT_AUTHORIZED | NOT_AUTHORIZED |
| Pressure-gradient acceleration | Primary dynamic | PASS | PASS, regular scope only | FAIL after fresh requalification | NOT_QUALIFIED | NOT_AUTHORIZED | NOT_AUTHORIZED |
| Viscosity-Laplacian acceleration | Primary dynamic | PASS | PASS, regular scope only | FAIL after fresh requalification | NOT_QUALIFIED | NOT_AUTHORIZED | NOT_AUTHORIZED |
| Total acceleration | Derived diagnostic | PASS | PASS, regular scope only | Not independently evaluated | Not applicable as derived diagnostic | NOT_AUTHORIZED | NOT_AUTHORIZED |

## Table 3. Initial and fresh identifiability metrics

**Caption.** Formal C3/L3 metrics for the three primary dynamic mappings. Limits are disagreement median \(\leq0.25\), disagreement 90th percentile \(\leq0.60\), conditional-variance upper bound \(\leq0.35\), oracle normalized root-mean-square error \(\leq0.50\), and coverage \(\geq0.90\). Every applicable gate must pass.

| Evidence cycle | Component | DNN median | DNN P90 | Conditional variance upper95 | Best oracle NRMSE | Coverage | H3 outcome |
|---|---|---:|---:|---:|---:|---:|---|
| Development | Density rate | 0.0006954 | 2.653 | 0.1036 | 0.4634 | 0.9526 | Did not satisfy all criteria |
| Development | Pressure-gradient acceleration | 0.01600 | 3.665 | 1.399 | 1.044 | 0.9526 | Did not satisfy all criteria |
| Development | Viscosity-Laplacian acceleration | 0.1408 | 10.70 | 0.3287 | 1.049 | 0.9526 | Did not satisfy all criteria |
| Fresh | Density rate | 0.001276 | 8.202 | 0.1489 | 0.5481 | 0.9358 | Did not satisfy all criteria |
| Fresh | Pressure-gradient acceleration | 0.0008044 | 45.54 | 1.070 | 1.010 | 0.9358 | Did not satisfy all criteria |
| Fresh | Viscosity-Laplacian acceleration | 0.2773 | 26.88 | 0.4042 | 1.049 | 0.9358 | Did not satisfy all criteria |

## Table 4. Evidence-based failure taxonomy

**Caption.** Alternative explanations and their frozen dispositions. These entries classify evidence within the tested route and do not establish universal causes.

| Code | Question | Frozen disposition | Evidence boundary |
|---|---|---|---|
| F0 | Numerical/reference implementation uncertainty | Resolved and qualified | Mandatory fixed-time audits passed; no dynamic-solver claim follows. |
| F1 | Defect signal too weak | Rejected by H1 evidence | Every component passed both signal gates over its excited-case scope. |
| F2 | No systematic scaling | Component-dependent | Density rate passed tested disorder; pressure, viscosity, and total were regular-only; interpolation failed. |
| F3 | Insufficient feature-space coverage | Not sufficient | Coverage was 0.9526 and 0.9358, above 0.90, while H3 criteria were not satisfied. |
| F4 | Observable conditional ambiguity | Supported within tested scope | Disagreement tails, conditional variance, oracle error, and family sensitivity persisted componentwise. |
| F5 | Simple consistency descriptors rescue disorder ambiguity | Not supported | Matched ablations showed no uniform pressure or viscosity rescue. |
| F6 | Tested directional-frame augmentation rescues the route | Not supported as a complete route | Fresh H3 failed; fallback occurred in 515,904/627,264 environments. |
| F7 | Expanded deployment-compatible observables identify the defects | Fresh requalification failed | The frozen redesign was tested on 384 new cases with zero lineage overlap. |

## Table S1. Full-precision H1 component ledger shell

| Component | Eligible cases | Unexcited cases | \(T_c\) | \(U_c\) | \(R_c\) | \(L_{95,c}\) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Interpolation density | [frozen ledger] | [frozen ledger] | [full precision] | [full precision] | [full precision] | [full precision] | [frozen verdict] |
| Density rate | [frozen ledger] | [frozen ledger] | [full precision] | [full precision] | [full precision] | [full precision] | [frozen verdict] |
| Pressure-gradient acceleration | [frozen ledger] | [frozen ledger] | [full precision] | [full precision] | [full precision] | [full precision] | [frozen verdict] |
| Viscosity-Laplacian acceleration | [frozen ledger] | [frozen ledger] | [full precision] | [full precision] | [full precision] | [full precision] | [frozen verdict] |
| Total acceleration | [frozen ledger] | [frozen ledger] | [full precision] | [full precision] | [full precision] | [full precision] | [frozen verdict] |

## Table S2. Controlled scaling track ledger shell

| Component | Refinement regular | Refinement jitter | Spectral regular | Spectral jitter | Formal scope | Descriptive slopes |
|---|---|---|---|---|---|---|
| Interpolation density | FAIL | FAIL | FAIL | FAIL | Not qualified | [frozen descriptive values] |
| Density rate | PASS | PASS | PASS | PASS | Regular and tested disorder | [frozen descriptive values] |
| Pressure-gradient acceleration | PASS | FAIL | PASS | PASS | Regular only | [frozen descriptive values] |
| Viscosity-Laplacian acceleration | PASS | FAIL | PASS | PASS | Regular only | [frozen descriptive values] |
| Total acceleration | PASS | FAIL | PASS | PASS | Regular only, derived diagnostic | [frozen descriptive values] |

## Table S3. Deployment-observability and descriptor dictionary shell

| Group | Classification or content | Dimensions/transformation | Conditioning or fallback | Use boundary |
|---|---|---|---|---|
| Legacy fields | Runtime-direct, runtime-estimable, design-only | [frozen ledger] | [not applicable] | Design-only fields excluded |
| Weighted moments | Orders 2–4 | [frozen dictionary] | [frozen conditioning] | Reference-free only |
| Angular harmonics | Frozen angular channels | [frozen dictionary] | [frozen fallback] | No target-derived orientation |
| Observable-frame channels | Directional observables | [frozen dictionary] | Frame-degeneracy fallback | Tested construction only |
| Quadratic reconstruction | Local reference-free proxies | [frozen dictionary] | Failure flags retained | No analytical derivatives |

## Table S4. Fresh fold quality control and frame fallback shell

| Item | Frozen value | Interpretation boundary |
|---|---:|---|
| Fresh cases | 384 | 96 per family |
| Formal samples | 49,152 | Lineage-separated folds |
| Development-lineage overlap | 0 | Fresh formal evidence |
| Mandatory numerical qualification | 384/384 | Fixed-time qualification only |
| Directional-frame fallback | 515,904/627,264 | 82.246710%; tested frame degeneracy only |
