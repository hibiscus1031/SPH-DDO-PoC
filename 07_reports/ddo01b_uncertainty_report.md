# DDO-01B uncertainty report

## Status

`NOT_EVALUATED_DUE_TO_DDO01B_H1_UNRESOLVED_CONTRACT_GAP`

The CA-01 uncertainty contract was found and hash-bound. Its unique fresh-case
float64 rule remains:

\[
U_{num}=U_{round}+\Delta_{ref}+\Delta_{repeat}+\Delta_{accum}
+\Delta_{geometry}+\Delta_{identity},
\]

where `Delta_accum = max(Delta_perm, Delta_comp)`. Every term must share the
target channel's units. Float32-versus-float64 remains only a
`precision_degradation_diagnostic` and is excluded from primary uncertainty.

No DDO-01A-R `U_num` value was imported. No fresh DDO-01B uncertainty
diagnostic was run, because the mandatory H1 semantic precheck failed before
case registration and target evaluation. Thus this report contains no measured
DDO-01B uncertainty values and makes no numerical-qualification claim.

The unresolved issue is downstream of the valid per-case CA-01 construction:
the frozen contracts do not define how per-case `U_num(j,c)` values form the
component-level conservative uncertainty bound and bootstrap H1 statistic.
