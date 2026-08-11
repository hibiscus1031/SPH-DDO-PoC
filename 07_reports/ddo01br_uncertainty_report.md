# DDO-01B-R numerical uncertainty report

## Result

All 24 fresh cases passed the frozen CA-01 numerical/reference qualification.
For every case/component,

`U_num = U_round + Delta_ref + Delta_repeat + max(Delta_perm, Delta_comp) + Delta_geometry + Delta_identity`.

All terms used matching physical units. Float32 degradation remained a separate
diagnostic and never entered `U_num` or H1.

| Component | `U_num` minimum | `U_num` maximum / CA-02 `U_c` | max `Delta_ref` | max `Delta_perm` | max `Delta_comp` | max `Delta_geometry` | max float32 diagnostic |
|---|---:|---:|---:|---:|---:|---:|---:|
| interpolation/density | 2.887761e-14 | 3.108268e-14 | 0 | 1.110223e-15 | 8.881784e-16 | 8.881784e-16 | 1.061919e-6 |
| density rate | 2.842171e-15 | 2.686777e-14 | 2.220446e-16 | 7.771561e-16 | 5.551115e-16 | 8.881784e-16 | 1.214058e-6 |
| pressure-gradient acceleration | 2.842171e-16 | 2.495471e-13 | 1.776357e-15 | 2.131628e-14 | 2.009504e-14 | 4.618528e-14 | 1.109128e-4 |
| viscosity/Laplacian acceleration | 2.842171e-16 | 1.984764e-15 | 2.081668e-17 | 1.665335e-16 | 1.292369e-16 | 2.636780e-16 | 1.455824e-6 |
| total acceleration | 1.170569e-15 | 2.495471e-13 | 1.776357e-15 | 2.131628e-14 | 2.009504e-14 | 4.618528e-14 | 1.109128e-4 |

`Delta_repeat` was zero for every case/component. `Delta_identity` and the
maximum acceleration component-closure residual were zero. All positive-
additive sign identities passed their own `U_num` gates. Independent brute-force
geometry reproduced the primary edge-key sets in every case.

The CA-02 component denominator was the maximum `U_num` over the full original
eligible set and remained fixed in all 10,000 bootstrap replicates. No
DDO-01A-R uncertainty value was imported.
