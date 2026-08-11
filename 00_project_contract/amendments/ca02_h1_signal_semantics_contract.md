# CA-02 prospective H1 signal-qualification semantics contract

## Status and scope

CA-02 prospectively repairs only the statistical mapping from a fresh
case/component target and the already frozen CA-01 `U_num(j,c)` to the frozen
DDO-00 component H1 decision. It does not alter the DDO-00 thresholds, CA-01,
or the permanent `DDO01B_H1_UNRESOLVED_CONTRACT_GAP` result. No real DDO-01B-R
target was observed before this contract and its synthetic implementation were
frozen.

The point threshold remains `10`; the group-bootstrap 95% lower-bound threshold
remains strictly greater than `5`.

## Case and component statistics

For scalar target values `d_ji`, define

\[
T_{jc}=\sqrt{N_j^{-1}\sum_i d_{jic}^2}.
\]

For vector target values, define

\[
T_{jc}=\sqrt{N_j^{-1}\sum_i\lVert\mathbf d_{jic}\rVert_2^2}.
\]

Vector targets are not divided by the number of Cartesian components. Let
`E_c` contain only analytically excited, valid complete cases and let
`M_c=|E_c|`. Equal case weighting is mandatory:

\[
T_c=\sqrt{M_c^{-1}\sum_{j\in E_c}T_{jc}^2}.
\]

Particles are never pooled across cases. The conservative component uncertainty
is

\[
U_c=\max_{j\in E_c}U_{num}(j,c),
\]

where `U_num` is unchanged from CA-01. Define `R_c=T_c/U_c` and point margin
`M_point,c=R_c/10`. The point criterion is `R_c >= 10`.

For an excited valid case, `r_jc=T_jc/U_num(j,c)`. Its diagnostic label is
`CASE_SIGNAL_PASS` for `r_jc >= 10` and `CASE_SIGNAL_LOW` otherwise. An invalid
mandatory numerical/reference audit gives `CASE_UNRESOLVED`. An analytically
unexcited pair gives `CASE_NOT_APPLICABLE_UNEXCITED`. These labels never replace
the component gate and low-signal cases are retained.

## Analytically unexcited pairs

Analytically unexcited pairs are excluded from `E_c`, `T_c`, `U_c`, and every
bootstrap replicate. They are not inserted as zero targets and are neither H1
PASS nor H1 FAIL. Their identities and count remain reported. The mask must be
hash-frozen before any SPH target evaluation.

## Stratified group bootstrap

The bootstrap unit is one complete registered simulation case. Before
resampling, exclude analytically unexcited pairs. Stratify using registry-only
metadata by `resolution x layout_class`. Within every nonempty stratum of size
`n_s`, sample `n_s` cases with replacement, preserving all stratum sizes.

Use exactly `B=10000` replicates. For replicate `b`,

\[
T_c^{(b)}=\sqrt{\operatorname{mean}_{j\ in\ resample}(T_{jc}^2)},
\qquad R_c^{(b)}=T_c^{(b)}/U_c.
\]

The denominator is the fixed `U_c` from all original eligible cases and is
never recomputed from a resample.

For canonical component name `c`, form the UTF-8 input

`DDO01B-H1-BOOTSTRAP|<c>`.

Compute its SHA-256 digest and interpret the full 32 digest bytes as one
unsigned big-endian integer. Pass that integer to `numpy.random.PCG64`, wrapped
by `numpy.random.Generator`. No user-selected seed is permitted.

The lower bound is exactly

`numpy.quantile(R_bootstrap, 0.05, method="inverted_cdf")`.

Call it `L95_c`; the second criterion is strictly `L95_c > 5`. Define
`M_boot,c=L95_c/5`.

## Verdict and minimum evidence

At least eight eligible complete cases are required.

- `H1_SIGNAL_PASS` iff `M_c >= 8`, every mandatory numerical/reference audit
  is valid, `R_c >= 10`, and `L95_c > 5`.
- `H1_SIGNAL_FAIL` iff `M_c >= 8`, every mandatory audit is valid, and either
  `R_c < 10` or `L95_c <= 5`.
- `H1_SIGNAL_UNRESOLVED` iff `M_c < 8`, a mandatory audit is invalid, or a
  required uncertainty/statistic is not uniquely constructible.

Only `H1_SIGNAL_FAIL` may trigger `CLOSED_FOR_LEARNING_DDO01`. A case-level
label alone cannot close a component.

## Frozen implementation and qualification

The normative implementation is `08_scripts/h1_signal_semantics.py`. Before
CA-02 freeze, `08_scripts/test_h1_signal_semantics.py` must pass all ten
synthetic-only tests registered in
`06_manifests/ca02_synthetic_expected_outputs.json`: obvious PASS, point FAIL,
bootstrap-lower FAIL, unexcited exclusion, unequal-particle equal-case
weighting, `[3,4] -> 5` vector RMS, insufficient eligible groups, invalid audit,
fixed bootstrap denominator, and deterministic repeat.

No historical or real SPH target value may appear in those tests.
