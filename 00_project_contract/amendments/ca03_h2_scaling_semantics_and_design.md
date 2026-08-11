# CA-03 prospective H2 scaling semantics and registry design

## Status and scope

This amendment prospectively repairs the H2 executability gaps recorded by
`DDO01C_H2_UNRESOLVED_CONTRACT_GAP`. The stopped DDO-01C status is permanent.
No DDO-01C-R registry, target, slope, figure, or classification was observed
before this contract, its pure implementation, and its synthetic tests were
frozen.

CA-03 does not modify the DDO-00 qualitative H2 thresholds, CA-01 `U_num`,
CA-02 case-RMS semantics, or any historical terminal state. It authorizes only
a fresh DDO-01C-R fixed-time F1 scaling execution after synthetic
qualification.

## Frozen components and response

The formal components are:

1. `interpolation_density`, with `S_c = rho0 = 1`;
2. `density_rate`, with `S_c = rho_dot0 = 0.1`;
3. `pressure_gradient_acceleration`, with `S_c = A0 = 0.01`;
4. `viscosity_laplacian_acceleration`, with `S_c = A0 = 0.01`; and
5. `total_acceleration`, with `S_c = A0 = 0.01`.

These scales are uniquely inherited from `dimensional_analysis.md` and CA-01.
For the unchanged CA-02 scalar/vector case RMS `T_jc`, define

`Y_jc = T_jc/S_c`, `u_jc = U_num(j,c)/S_c`,

`Y_minus = (T_jc-U_num(j,c))/S_c`, and
`Y_plus = (T_jc+U_num(j,c))/S_c`.

A formal point is log-admissible only when every CA-01 mandatory audit is valid
and `T_jc-U_num(j,c) > 0`. Otherwise it is
`LOG_RESPONSE_UNRESOLVED`; no epsilon, imputation, or case deletion is allowed.
No target-derived normalization is used.

## Formal and diagnostic families

- `REFINEMENT_H`: formal coordinate `x=h`; expected local log-slope sign
  positive. This is interpreted only as a complete refinement path.
- `SPECTRAL_KH`: formal coordinate `x=kh`; expected local log-slope sign
  positive.
- `SUPPORT_RATIO_HDX`: coordinate `x=h/dx`; no expected sign and no H2 gate;
  every result is `DESCRIPTIVE_SCOPE_DIAGNOSTIC`.
- `REGULAR_VS_DISORDER`: matched regular/jitter robustness analysis; it maps
  the two formal-family layout verdicts but is not a third independent H2
  family.

## Exact numeric coordinate tables

The domain has `L=1`, so `dx=1/N` and `h=(h/dx)/N`.

### REFINEMENT_H

Mode `(1,0)`, `h/dx=4`, and every selected continuum field, phase, layout
realization, and non-scanned numerical parameter remain fixed within a path.

| level | N | dx | h | h/dx | mode | kh | points/wavelength |
|---:|---:|---:|---:|---:|---|---:|---:|
| 0 | 16 | 0.0625 | 0.25 | 4 | (1,0) | 1.5707963267948966 | 16 |
| 1 | 24 | 0.041666666666666664 | 0.16666666666666666 | 4 | (1,0) | 1.0471975511965976 | 24 |
| 2 | 32 | 0.03125 | 0.125 | 4 | (1,0) | 0.7853981633974483 | 32 |
| 3 | 48 | 0.020833333333333332 | 0.08333333333333333 | 4 | (1,0) | 0.5235987755982988 | 48 |
| 4 | 64 | 0.015625 | 0.0625 | 4 | (1,0) | 0.39269908169872414 | 64 |

### SPECTRAL_KH

`N=64`, `dx=0.015625`, `h/dx=4`, and `h=0.0625`. The direction family is
positive x and only wave-number magnitude varies.

| level | mode | k | kh | points/wavelength |
|---:|---|---:|---:|---:|
| 0 | (1,0) | 6.283185307179586 | 0.39269908169872414 | 64 |
| 1 | (2,0) | 12.566370614359172 | 0.7853981633974483 | 32 |
| 2 | (3,0) | 18.84955592153876 | 1.1780972450961724 | 21.333333333333332 |

### SUPPORT_RATIO_HDX

This diagnostic uses `N=64`, `dx=0.015625`, mode `(1,0)`, and the `D010` and
`V100` track templates below.

| level | h/dx | h | kh |
|---:|---:|---:|---:|
| 0 | 2 | 0.03125 | 0.19634954084936207 |
| 1 | 3 | 0.046875 | 0.2945243112740431 |
| 2 | 4 | 0.0625 | 0.39269908169872414 |
| 3 | 5 | 0.078125 | 0.4908738521234052 |

Every level satisfies at least eight points per wavelength and compact support
strictly below half the domain extent.

## Exact scientific track templates

All cases use F1, direction family `(+,0)`, `rho0=1`, `c0=10`, `nu=0.01`,
CPU float64, and phase/jitter mappings below. The inactive amplitude column is
retained as a declared formula parameter but is not an active field channel.

| track | probe | polarization | density amplitude | velocity amplitude | formal use |
|---|---|---|---:|---:|---|
| D005 | density | none | 0.005 | 0.1 | refinement, spectral |
| D010 | density | none | 0.01 | 0.1 | refinement, spectral, support ratio |
| V050 | longitudinal | longitudinal | 0.01 | 0.05 | refinement, spectral |
| V100 | longitudinal | longitudinal | 0.01 | 0.1 | refinement, spectral, support ratio |

Mandatory component/track membership for each formal family and layout is:

| component | mandatory tracks |
|---|---|
| interpolation_density | D005, D010 |
| density_rate | V050, V100 |
| pressure_gradient_acceleration | D005, D010 |
| viscosity_laplacian_acceleration | V050, V100 |
| total_acceleration | D005, D010, V050, V100 |

Amplitude changes create independent scientific tracks. Phase and jitter seed
changes are replicates only. Formal families are evaluated separately for
`regular` and `jitter_0.05`. Jitter fraction `0.05` is selected prospectively
as the single controlled-disorder scope and is not chosen from a DDO-01C-R
outcome.

## Replicates and deterministic mapping

Each track/coordinate/layout point has exactly three matched replicates. The
allowed phase pool is `[0, pi/4, pi/2]`, represented numerically as
`[0.0, 0.7853981633974483, 1.5707963267948966]`. The allowed jitter-seed pool
is `[20260811, 20260817, 20260823]`.

Define the canonical pair-track identifier, which intentionally excludes
layout and scanned coordinate, as

`F1|track=<track>|probe=<probe>|polarization=<polarization>|direction=1,0|density_amplitude=<A_rho>|velocity_amplitude=<A_v>|rho0=1|c0=10|nu=0.01|dtype=float64`.

For each pool, first sort values by their canonical JSON token. For replicate
`r=0,1,2`, hash the UTF-8 string

`DDO01CR|PHASE|<pair_track_id>|r=<r>`

or

`DDO01CR|JITTER|<pair_track_id>|r=<r>`.

Interpret the full SHA-256 digest as an unsigned big-endian integer, select
index `digest mod len(remaining_pool)`, remove that value, and continue. Thus
all three distinct authorized values are used without replacement. The same
phase replicate is used for the regular and jitter member of a pair; only the
jitter member uses its mapped seed.

The canonical case identifier is

`F1|track=<track>|N=<N>|h_over_dx=<ratio>|mode=<nx>,<ny>|replicate=<r>|phase=<17g>|layout=<layout>|jitter_fraction=<17g>|jitter_seed=<seed-or-null>|dtype=float64`.

Neighbor-permutation seed input is
`DDO01CR|NEIGHBOR_PERMUTATION|<canonical_case_id>`; the first eight digest
bytes are interpreted unsigned big-endian and masked to 63 bits.

The exact unique registry contains 204 cases: 34 unique numerical/field
configurations crossed with two layouts and three replicates. D005 and V050
have seven coordinate configurations each; D010 and V100 have ten each.
Overlapping `(N=64, mode=(1,0), h/dx=4)` points are single cases carrying all
applicable family labels.

## Local slopes and classifications

Sort levels by increasing formal coordinate. For matched replicate `r` and
adjacent levels `a,b`, define

`p = [log(Y_b)-log(Y_a)]/[log(x_b)-log(x_a)]`,

`p_minus = [log(Y_minus_b)-log(Y_plus_a)]/log(x_b/x_a)`,

`p_plus = [log(Y_plus_b)-log(Y_minus_a)]/log(x_b/x_a)`.

- `p_minus > 0`: `EXPECTED_SIGN_SUPPORTED`;
- `p_plus < 0`: `OPPOSITE_SIGN`;
- `p_minus <= 0 <= p_plus`: `PLATEAU_OR_UNCERTAINTY_OVERLAP`.

All intervals are retained. No regression replaces local slopes. The median
central local slope is descriptive only.

## Monotonicity and dispersion gates

For track `t`, `m_t` is the number of required adjacent replicate intervals
with `p_minus>0` divided by all required valid adjacent replicate intervals.
Plateau/overlap and opposite-sign intervals are non-supporting. Scientific
tracks have equal weight:

`M_family = mean_t(m_t)` and the unchanged threshold is
`M_family >= 0.75`.

In log-response space, for track `t`, replicate `r`, level `l`, define
`z_minus=log(Y_minus)` and `z_plus=log(Y_plus)`. Then

`D_tl=max_r z_plus(t,r,l)-min_r z_minus(t,r,l)`,
`D_t=median_l D_tl`,

`C_trl=max(0,z_minus(b)-z_plus(a),z_minus(a)-z_plus(b))`, and
`C_t=median_(r,l) C_trl`.

Every mandatory track must satisfy `D_t < C_t`. No H2 bootstrap is used.

## Formal verdicts

A component/family/layout is `PASS` only with at least two independent
mandatory tracks, at least three levels per track, three matched replicates per
level, valid CA-01 audits, admissible log responses, finite slopes,
`M_family>=0.75`, and `D_t<C_t` for every mandatory track.

It is `FAIL` when the design and numerical evidence are complete but
`M_family<0.75` or any mandatory track has `D_t>=C_t`. It is `UNRESOLVED` for
insufficient tracks/levels/replicates, invalid audit, nonpositive lower log
response, nonfinite slope, or registry/pairing failure.

For a layout, both `REFINEMENT_H` and `SPECTRAL_KH` must PASS. Any formal-family
FAIL makes the layout scope FAIL; otherwise any non-PASS makes it UNRESOLVED.

Component mapping:

- regular PASS + jitter PASS: `H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT`;
- regular PASS + jitter FAIL: `H2_SCALING_PASS_REGULAR_SCOPE_ONLY`;
- regular PASS + jitter UNRESOLVED:
  `H2_SCALING_PASS_REGULAR_SCOPE_DISORDER_UNRESOLVED`;
- regular FAIL: `H2_SCALING_FAIL_REGULAR_SCOPE`;
- regular UNRESOLVED: `H2_SCALING_UNRESOLVED`.

Every PASS claim is restricted to canonical formal support `h/dx=4`.
Support-ratio diagnostics cannot change this mapping.

Project mapping:

- all five canonical-support PASS:
  `DDO01CR_SPATIAL_DEFECT_SCALING_QUALIFIED`;
- at least one full or regular-only qualified scope and at least one differing
  component: `DDO01CR_COMPONENTWISE_SCALING_PARTIALLY_QUALIFIED`;
- all five valid regular-scope FAIL:
  `DDO01CR_SCALING_NOT_SUPPORTED`;
- otherwise: `DDO01CR_SCALING_EVIDENCE_MIXED_OR_UNRESOLVED`.

## Descriptive diagnostics

Support-ratio output reports response, local descriptive slopes, uncertainty
intervals, and regular/jitter differences as
`DESCRIPTIVE_SCOPE_DIAGNOSTIC`, with no expected sign or H2 threshold.

For each case/component, let `C_jc` be the continuum-side scalar/vector RMS
under the CA-02 convention. Define

`E_rel(j,c)=T_jc/max(C_jc,U_round(j,c))`.

It is always `DESCRIPTIVE_NOT_H2_GATE`; no performance threshold is allowed.

## Authorization boundary

Only after all registered synthetic-only tests pass and CA-03 is hash-frozen
may the exact deterministic DDO-01C-R registry be materialized and independently
hash-frozen before target computation. H3-H6, F2-F4 balanced-atlas work,
PCA/SVD, prediction, regression, neural models, optimization, time integration,
rollout, solver-in-the-loop, high-resolution SPH truth, LCDF_03, and LCDF_10
remain prohibited.
