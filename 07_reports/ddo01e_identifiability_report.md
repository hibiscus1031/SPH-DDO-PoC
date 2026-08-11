# DDO-01E observable identifiability report

## Formal result

`DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE`

The formal response uses C3/L3 and five lineage-held-out development folds.
Every complete case contributes exactly 128 target-blind particles and cases do
not receive resolution-dependent weight.

| Component | DNN median | DNN p90 | Cvar (upper95) | Best oracle NRMSE | Improvement | Worst family | Coverage | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Density rate | 0.001 | 2.653 | 0.075 (0.104) | 0.463 | 53.7% | 0.895 | 95.3% | `H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |
| Pressure | 0.016 | 3.665 | 1.105 (1.399) | 1.044 | -4.4% | 1.075 | 95.3% | `H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |
| Viscosity | 0.141 | 10.696 | 0.248 (0.329) | 1.049 | -4.9% | 1.038 | 95.3% | `H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |
| Interpolation | 0.011 | 2.621 | 0.215 (0.245) | 0.014 | 98.5% | 0.013 | 95.3% | `H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |

All four assessed mappings fail at least one mandatory H3 gate. Coverage passes
for every component, so the negative conclusion is not a simple absence of
feature-space support. The common failure is the DNN 90th-percentile tail. The
pressure mapping additionally fails Cvar, oracle, improvement, and worst-family
gates; viscosity passes Cvar but fails oracle/improvement/family gates. Density
rate passes Cvar and oracle point gates but fails the tail and worst-family gate.
Interpolation is highly regular for the simple oracle and Cvar, yet its DNN tail
still exceeds the frozen limit; it remains algebraic diagnostic evidence and
cannot authorize a dynamic RHS route.

No positive H3 result is inferred from low medians, isolated oracle success, or
nonzero R2. These are sampled-development-domain information diagnostics, not
model-performance or generalization claims.
