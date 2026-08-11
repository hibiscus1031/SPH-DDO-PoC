# DDO-01E F1-F4 family-stratified report

Formal C3/L3 diagnostics remain separated by analytical family:

| Component | Family | Best-oracle NRMSE | DNN p90 |
|---|---|---:|---:|
| Density rate | F1 | 0.455 | 1.265 |
| Density rate | F2 | 0.415 | 0.424 |
| Density rate | F3 | 0.364 | 0.572 |
| Density rate | F4 | 0.895 | 1.198 |
| Pressure | F1 | 1.004 | 0.812 |
| Pressure | F2 | 1.001 | 0.647 |
| Pressure | F3 | 1.001 | 0.689 |
| Pressure | F4 | 1.075 | 12.077 |
| Viscosity | F1 | 1.004 | 15.417 |
| Viscosity | F2 | 1.003 | 3.829 |
| Viscosity | F3 | 1.003 | 5.453 |
| Viscosity | F4 | 1.038 | 2.134 |

The project verdict uses the worst required family gate; a favorable F1 or any
other single-family value cannot hide ambiguity in F2, F3, or F4. These are
development-domain strata, not transfer or H6 results.
