# DDO-01E locality report

## Decision

No component receives a positive H4 locality claim because H4 is conditional on
formal H3 support and all three primary mappings fail H3. Consequently no
"smallest sufficient" rung is selected.

| Component | L0 NRMSE/Cvar | L1 | L2 | L3 | H4 status |
|---|---|---|---|---|---|
| Density rate | 0.463/0.236 | 0.463/0.071 | 0.463/0.075 | 0.463/0.075 | `OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |
| Pressure | 1.011/1.007 | 1.044/1.108 | 1.044/1.085 | 1.044/1.105 | `OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |
| Viscosity | 1.025/0.381 | 1.048/0.334 | 1.044/0.275 | 1.049/0.248 | `OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |

The locality ladder remains useful descriptive evidence, but improvements at a
single rung cannot override the complete H3 bundle. L3 is a broad observable
summary diagnostic only; it is not a Transformer, architecture, or final
nonlocality theorem.
