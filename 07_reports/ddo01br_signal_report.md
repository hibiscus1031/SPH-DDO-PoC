# DDO-01B-R prospective F1 spatial-defect signal report

## Terminal state

`DDO01BR_SPATIAL_DEFECT_SIGNAL_QUALIFIED`

All 24 freshly registered DDO-01B-R cases passed the mandatory analytical,
reference, topology, float64 uncertainty/sign, and component-closure audits.
All five preregistered components passed both frozen CA-02 H1 criteria.

The permanent earlier state remains unchanged:

`DDO01B_H1_UNRESOLVED_CONTRACT_GAP`

No DDO-01A or DDO-01A-R case contributed formal evidence.

## Component H1 results

| Component | Eligible | Unexcited | `T_c` | `U_c` | `R_c` | `L95_c` | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| interpolation/density | 24 | 0 | 7.631394e-3 | 3.108268e-14 | 2.455192e11 | 2.283679e11 | `H1_SIGNAL_PASS` |
| density rate | 8 | 16 | 4.339104e-2 | 2.686777e-14 | 1.614985e12 | 9.177052e11 | `H1_SIGNAL_PASS` |
| pressure-gradient acceleration | 8 | 16 | 5.474324e-1 | 2.495471e-13 | 2.193704e12 | 1.642658e12 | `H1_SIGNAL_PASS` |
| viscosity/Laplacian acceleration | 16 | 8 | 2.789142e-3 | 1.984764e-15 | 1.405277e12 | 1.170251e12 | `H1_SIGNAL_PASS` |
| total acceleration/RHS | 24 | 0 | 3.160684e-1 | 2.495471e-13 | 1.266568e12 | 7.910277e11 | `H1_SIGNAL_PASS` |

The fixed point requirement is `R_c >= 10`; the fixed bootstrap requirement is
strictly `L95_c > 5`. The table values exceed both criteria by large margins.
Every excited case received `CASE_SIGNAL_PASS`; no excited case was low-signal
or unresolved. Unexcited pairs were excluded from `T_c`, `U_c`, and bootstrap
and were not inserted as zeros.

The interpolation target is the frozen density interpolation target. For
`f=rho`, its discrete expression equals density summation algebraically because
`(m_j/rho_j) rho_j = m_j`; it is evaluated only once as the canonical
`interpolation_density` component.

## Numerical prerequisites

- mandatory cases passed: `24/24`;
- maximum A/B derivative discrepancy: `1.776357e-15`;
- maximum derivative-gate fraction: `1.117735e-2`;
- maximum component-closure residual: `0`;
- primary float64 `U_num` range over all case/components:
  `2.842171e-16` to `2.495471e-13`; and
- maximum float32 degradation diagnostic: `1.109128e-4`, excluded from `U_num`.

## Total versus components

The isolated F1 probes make the descriptive boundary explicit. Across all 24
cases, the cancellation index was exactly zero and the domination share was
exactly one. Pressure dominated the 8 density-probe cases; viscosity dominated
the 16 velocity-probe cases. This does not let total acceleration qualify a
component: pressure and viscosity each independently passed their own H1 gate.
No scaling claim follows from these diagnostics.

## Scope

Only H1 was evaluated. H2-H6, F2-F4, a balanced atlas, PCA/SVD, regression,
neural models, optimization, time integration, rollout, solver-in-the-loop,
high-resolution-SPH truth, LCDF_03, and LCDF_10 were not executed.
