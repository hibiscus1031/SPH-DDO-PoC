# CA-02 final report

## Terminal state

`DDO_CA02_H1_SIGNAL_SEMANTICS_FROZEN`

CA-02 prospectively and only repairs the missing statistical semantics between
fresh case/component target plus CA-01 `U_num` evidence and the frozen DDO-00
H1 component decision. The DDO-00 thresholds remain `R_c >= 10` and
`L95_c > 5`; CA-01 is unchanged.

The permanent original result remains:

`DDO01B_H1_UNRESOLVED_CONTRACT_GAP`

No historical or real SPH target value was used to select or test CA-02.

## Frozen semantics

- scalar and vector case RMS follow the registered formulas, without a vector
  Cartesian-component divisor;
- component target RMS gives each eligible case equal weight;
- component uncertainty is the maximum eligible-case CA-01 `U_num`;
- case ratios and labels are diagnostic only;
- analytically unexcited pairs are excluded, never inserted as zeros;
- complete cases are stratified by `resolution x layout_class`;
- 10,000 within-stratum replacement replicates are used;
- the full original eligible-set maximum uncertainty is fixed in every
  replicate;
- PCG64 receives the unsigned big-endian integer represented by the full
  SHA-256 digest of `DDO01B-H1-BOOTSTRAP|<canonical_component_name>`;
- the lower bound uses NumPy `quantile(..., 0.05, method="inverted_cdf")`; and
- fewer than eight eligible complete cases or any invalid mandatory audit gives
  `H1_SIGNAL_UNRESOLVED`.

## Synthetic qualification

Command:

`python3 08_scripts/test_h1_signal_semantics.py`

Environment: Python `3.13.9`, NumPy `1.26.4`.

Result: `10 tests`, `10 passed`, `0 failed`, `0 errors`.

The tests cover obvious PASS, point-threshold FAIL, bootstrap-lower-bound FAIL,
unexcited exclusion, unequal particle-count equal-case weighting, vector RMS
`[3,4] -> 5`, insufficient eligible cases, invalid mandatory audit, fixed
bootstrap denominator, and deterministic repeated execution.

## Authorization

CA-02 authorizes only `DDO-01B-R — Fresh Prospective H1 Signal Pilot`, starting
with a new registry and excitation mask hash-frozen before any target
calculation. H2-H6, F2-F4, the balanced atlas, model fitting, neural models,
optimization, time integration, rollout, and high-resolution-SPH truth remain
prohibited.
