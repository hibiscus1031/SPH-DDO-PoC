# DDO-01B next-stage decision

## Decision

Assign:

`DDO01B_H1_UNRESOLVED_CONTRACT_GAP`

DDO-01C is not authorized. No component is recommended for controlled
spatial-defect scaling analysis, because no component received a valid H1
qualification.

## Required prospective repair before DDO-01B can be restarted

A new amendment must be frozen before any DDO-01B target outcome is inspected.
At minimum it must specify:

1. the exact component target-RMS statistic, including vector handling and
   weighting across unequal particle counts;
2. the exact aggregation from per-case CA-01 `U_num(j,c)` to component `U_d`;
3. the exact signal/uncertainty statistic and gate-margin definitions;
4. the grouping, stratification, resampling statistic, deterministic randomness
   or exact enumeration, replicate count, and 95% quantile convention;
5. the mapping from the component-level gate to case/component labels and the
   componentwise aggregation rule; and
6. treatment of analytically unexcited pairs within both the point statistic
   and bootstrap resamples.

That amendment may not use DDO-01B target magnitudes, ratios, or uncertainty
outcomes for calibration. After it is hash-frozen, DDO-01B must start with a
new prospective registry and excitation mask generated before any SPH target
evaluation.

## Closed work

H2-H6, F2-F4, the balanced atlas, identifiability/locality/target-geometry
analysis, representations R0-R4, regression, MLP, GNN, Transformer, optimizer,
time integration, rollout, and solver-in-the-loop remain closed.
