# DDO-01A-R next-stage decision

## Decision

DDO-01A-R assigns:

`DDO01_ANALYTICAL_PREFLIGHT_REQUALIFIED`

Authorize **DDO-01B — F1 micro-pilot** under the unchanged DDO-00 contracts and
the prospective CA-01 numerical uncertainty contract.

The original DDO-01A status permanently remains
`DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP`; this authorization comes
only from the fresh DDO-01A-R result.

## DDO-01B boundary

DDO-01B may execute only the frozen small F1 pilot matrix, keep observable and
reference sides physically separated, audit
`REFERENCE_IN_MODEL_INPUT = false`, and apply H1 componentwise using the CA-01
float64 `U_num`. The float32 precision-degradation diagnostic must not enter H1.

Interpolation/density, density rate, pressure, viscosity, and total RHS must be
reported separately. Total-RHS cancellation cannot qualify an unresolved
component. H1 FAIL closes that component; H1 UNRESOLVED stops it
prospectively.

## Still closed

This decision does not execute DDO-01B and does not authorize atlas expansion,
H2–H6 claims, diagnostic regression outside the frozen later stages, neural
models, optimizers, time integration, rollout, high-resolution SPH truth,
LCDF_03, LCDF_10, or Stage09.
