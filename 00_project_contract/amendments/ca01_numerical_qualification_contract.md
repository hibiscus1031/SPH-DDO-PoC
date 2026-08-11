# CA-01 prospective numerical qualification and uncertainty contract

## Status and scope

This amendment repairs numerical-qualification omissions discovered during
DDO-01A. It is prospective only. It does not edit DDO-00, does not replace the
original DDO-01A record, and cannot retroactively convert
`DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP` to PASS.

The following DDO-01A outcomes were observed before CA-01 was written:

| Previously observed diagnostic | Value |
|---|---:|
| maximum derivative A/B discrepancy | `1.7763568394002505e-15` |
| deterministic repeat discrepancy | `0` |
| neighbor-order discrepancy | `2.4868995751603507e-14` |
| float32/float64 diagnostic | `1.0730433520755867e-4` |
| acceleration-component closure | `0` |

These values did not select or calibrate any CA-01 threshold. The new
qualification set is registered and hash-frozen before its outcomes are
evaluated.

## Primary arithmetic and constants

Primary arithmetic is CPU float64. Define

\[
\epsilon_{64}=\operatorname{numpy.finfo}(\operatorname{float64}).\epsilon,
\qquad C_{fp}=128.
\]

`C_fp = 128` is a prospective conservative float64 allowance. It was not
selected from the observed DDO-01A discrepancies.

For case \(j\) and dimensionally homogeneous channel \(c\),

\[
U_{round}(j,c)=C_{fp}\epsilon_{64}S(j,c),
\]

\[
S(j,c)=\max\left(S_{frozen}(c),
\|L_{analytic}(j,c)\|_\infty,
\|L_{SPH}(j,c)\|_\infty\right).
\]

Channels with different physical dimensions are never combined. Target
statistics do not define or replace \(S_{frozen}\).

## Frozen characteristic scales

The existing dimensional-analysis contract freezes `rho0`, `L0`, `U0`, `c0`,
`P0 = rho0*c0^2`, `A0 = U0^2/L0`, and
`rho_dot0 = rho0*U0/L0`. DDO-01A-R binds `L0 = 1`, `rho0 = 1`, `c0 = 10`, and
`U0 = 0.1`. The declared nonzero velocity probe amplitude `U_probe = 0.1` is
used for density-only probes as required by the frozen dimensional-analysis
contract.

The resulting channel scales are:

| Channel | Frozen scale | Dimension |
|---|---:|---|
| density / interpolation / density summation | `rho0 = 1` | `M L^-2` |
| density gradient | `rho0/L0 = 1` | `M L^-3` |
| pressure | `P0 = 100` | `M T^-2` in 2-D |
| pressure gradient | `P0/L0 = 100` | `M L^-1 T^-2` in 2-D |
| velocity | `U0 = 0.1` | `L T^-1` |
| velocity gradient, divergence, vorticity, strain | `U0/L0 = 0.1` | `T^-1` |
| velocity Laplacian | `U0/L0^2 = 0.1` | `L^-1 T^-1` |
| density rate | `rho_dot0 = 0.1` | `M L^-2 T^-1` |
| pressure, viscosity, or total acceleration | `A0 = 0.01` | `L T^-2` |

## Independent derivative qualification

Evaluator A is the frozen closed-form analytical path. Evaluator B constructs
the F1 field independently and uses automatic differentiation; B must not call
A or reuse A's derivative expressions.

For every derivative or continuum channel,

\[
\delta_{ref}(j,c)=\|L_A(j,c)-L_B(j,c)\|_\infty,
\]

and

\[
U_{ref\_gate}(j,c)=C_{fp}\epsilon_{64}S(j,c).
\]

The channel passes only when

\[
\delta_{ref}(j,c)\le U_{ref\_gate}(j,c).
\]

Both absolute discrepancy and `delta_ref / S` are recorded. No tolerance may
be calibrated from any original DDO-01A case.

## Primary float64 uncertainty components

Each uncertainty term has the same physical units as its target channel.

For each case and component record:

1. `Delta_ref`: target change from replacing analytical continuum Evaluator A
   with independent Evaluator B while keeping the SPH side fixed.
2. `Delta_repeat`: target change under an exact deterministic repeat of the
   primary float64 computation.
3. `Delta_perm`: target change under a deterministic SHA-256-bound neighbor
   order permutation.
4. `Delta_comp`: target change when the primary `index_add` accumulation is
   replaced componentwise by Python `math.fsum` over the same float64 terms.
5. `Delta_accum = max(Delta_perm, Delta_comp)`.
6. `Delta_geometry`: target/operator-output change after rebuilding periodic
   minimum-image displacement and compact-support topology by an independent
   brute-force path using
   `delta - extent*floor(delta/extent + 0.5)` rather than the imported geometry
   routine. A raw position or displacement error is never added to acceleration
   uncertainty.
7. `Delta_identity`: for total acceleration,
   `||d_acc - d_pressure - d_viscosity||_inf`; for non-total target components,
   zero because no corresponding additive acceleration identity applies.

The unique primary uncertainty bound is

\[
U_{num}=U_{round}+\Delta_{ref}+\Delta_{repeat}
+\Delta_{accum}+\Delta_{geometry}+\Delta_{identity}.
\]

This additive rule is mandatory. It must not be replaced by quadrature, RMS,
maximum-only combination, fitted confidence limits, or post-outcome scaling
without a new prospective amendment.

## Float32 boundary

`FLOAT32_DIAGNOSTIC_IN_PRIMARY_UNCERTAINTY = false`.

The float32-versus-float64 target difference is reported only as
`precision_degradation_diagnostic`. It measures sensitivity to lowering
arithmetic precision and must not enter `U_num` or a later H1 ratio.

## Closure and sign gates

For

\[
r_{close}=\|d_{acc}-d_{pressure}-d_{viscosity}\|_\infty,
\]

the closure gate is

\[
r_{close}\le U_{acc}+U_{pressure}+U_{viscosity}.
\]

No unrelated absolute tolerance is allowed.

The positive-additive target sign is checked separately for each primary
target by

\[
r_{sign}=\|L_{SPH}+d-L_{analytic}\|_\infty.
\]

It qualifies when `r_sign <= U_num` for the same channel. This sign gate is an
arithmetic construction audit, not an H1 signal test.

## Fresh DDO-01A-R registry

The formal requalification matrix preserves the scientific axes `N = 16,32`,
`h/dx = 4`, modes `(1,0)` and `(1,1)`, three isolated F1 probes, and regular or
5% jittered layouts. It does not introduce F2, F3, or F4 atlas cases.

The canonical case identifier is

`F1|N=<N>|h_over_dx=4|mode=<nx>,<ny>|probe=<probe>|layout=<layout>`.

For each case, the phase digest input is

`DDO01A-R|<canonical_case_id>|phase`.

The phase is `2*pi*I/2^256`, where `I` is the full SHA-256 digest interpreted as
an unsigned big-endian integer. For each jittered case, the independent seed
digest input is

`DDO01A-R|<canonical_case_id>|jitter_seed`.

The jitter seed is the first eight digest bytes interpreted unsigned
big-endian and masked to 63 bits. Regular cases record a null jitter seed. The
complete registry is written and externally SHA-256-bound before any registered
case is numerically evaluated. No case may be removed after outcomes are seen.

## Requalification decision

Every registered case is mandatory. Requalification requires:

- imported-source hash match;
- all derivative/continuum channels passing the derivative gate;
- reciprocal, unique, in-bounds, complete periodic topology from both paths;
- identical primary and independent topology edge-key sets;
- finite, unit-matched uncertainty terms constructed by the unique additive
  rule;
- component closure passing the CA-01 closure gate;
- positive-additive sign identities passing their component `U_num` gates;
- float32 retained only as the separate precision-degradation diagnostic.

If every mandatory case passes, assign
`DDO01_ANALYTICAL_PREFLIGHT_REQUALIFIED` and authorize only DDO-01B. If any
mandatory case fails, assign
`DDO01_ANALYTICAL_PREFLIGHT_NUMERICAL_FAILURE`. If independent-path evidence or
implementation remains ambiguous, assign
`DDO01_ANALYTICAL_PREFLIGHT_REQUALIFICATION_UNRESOLVED`.

No H1 evaluation, pilot dataset, atlas, diagnostic regression, neural model,
optimizer, time integration, or rollout is part of DDO-01A-R.
