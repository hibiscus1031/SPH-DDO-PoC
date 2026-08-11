# DDO-01E descriptor-content ablation report

This target-blind preregistered comparison holds locality at L1 and contrasts G
against G+C within the eight matched F4 field blocks. Negative deltas indicate
reduced ambiguity/error after consistency descriptors are added.

| Component | Disorder | Metric | G (C0) | G+C (C1) | C1-C0 |
|---|---|---|---:|---:|---:|
| Pressure | regular | cvar | 0.093 | 0.260 | +0.167 |
| Pressure | regular | oracle_nrmse | 1.000 | 1.002 | +0.002 |
| Pressure | jitter_0.025 | cvar | 2.985 | 2.985 | +0.000 |
| Pressure | jitter_0.025 | oracle_nrmse | 1.000 | 1.005 | +0.005 |
| Pressure | jitter_0.05 | cvar | 4.005 | 4.006 | +0.001 |
| Pressure | jitter_0.05 | oracle_nrmse | 1.000 | 1.005 | +0.005 |
| Pressure | jitter_0.1 | cvar | 6.706 | 6.705 | -0.000 |
| Pressure | jitter_0.1 | oracle_nrmse | 1.000 | 1.002 | +0.002 |
| Viscosity | regular | cvar | 0.152 | 0.157 | +0.006 |
| Viscosity | regular | oracle_nrmse | 1.000 | 1.002 | +0.002 |
| Viscosity | jitter_0.025 | cvar | 2.799 | 2.799 | +0.000 |
| Viscosity | jitter_0.025 | oracle_nrmse | 1.001 | 1.002 | +0.001 |
| Viscosity | jitter_0.05 | cvar | 3.849 | 3.849 | +0.000 |
| Viscosity | jitter_0.05 | oracle_nrmse | 1.001 | 1.001 | +0.001 |
| Viscosity | jitter_0.1 | cvar | 7.037 | 7.037 | +0.000 |
| Viscosity | jitter_0.1 | oracle_nrmse | 1.001 | 1.006 | +0.005 |

Layer C does not provide a uniform pressure/viscosity rescue across disorder
strata. These effects are mechanism diagnostics only; they neither change the
formal C3/L3 verdict nor identify either support ratio or neighbor count as an
independent cause.
