# DDO-01B prospective F1 signal pilot — terminal contract precheck

## Terminal state

`DDO01B_H1_UNRESOLVED_CONTRACT_GAP`

DDO-01B stopped before creation of its prospective case registry, excitation
mask, SPH targets, fresh uncertainty evidence, or H1 outcomes. No DDO-01A or
DDO-01A-R case was reused as formal DDO-01B evidence.

## Frozen rule that was found

The hash-bound DDO-00 H1 rule requires, for each primary component:

- target RMS greater than a conservative uncertainty upper bound by at least
  10 times;
- a group-bootstrap 95% lower bound greater than 5 times; and
- passing continuum-derivative, float64-repeatability, decomposition-closure,
  and neighborhood audits.

CA-01 subsequently freezes a case/component scalar `U_num` as

`U_round + Delta_ref + Delta_repeat + max(Delta_perm, Delta_comp) + Delta_geometry + Delta_identity`.

It explicitly excludes the float32 diagnostic from `U_num`.

## Blocking ambiguity

The frozen documents do not uniquely define the component-level statistic to
which the 10-times and 5-times thresholds apply. In particular, they do not
freeze:

1. how the per-case scalar `U_num(j,c)` values become the component-level
   uncertainty upper bound `U_d(c)`;
2. whether component target RMS is pooled over particles and Cartesian entries,
   formed casewise and then aggregated, or paired casewise with `U_num`;
3. the statistic whose group-bootstrap distribution supplies the 95% lower
   bound;
4. the bootstrap stratification/resampling scheme, deterministic seed or exact
   enumeration rule, replicate count, and quantile convention; or
5. how a component-level gate is converted into the requested case/component
   `PASS`, `FAIL`, or `UNRESOLVED` labels and the componentwise aggregation.

The general statement that bootstrap samples are groups rather than particles
does not resolve these choices. Reasonable implementations can yield different
gate margins and even different classifications near the frozen thresholds.
Selecting one after inspecting DDO-01B outcomes would be a retrospective H1
contract repair, which is expressly prohibited.

## Scientific evidence status

No target norm, `U_num`, signal/uncertainty ratio, gate margin, lower-tail
diagnostic, cancellation diagnostic, or domination diagnostic was computed for
DDO-01B. Consequently, no component passed or failed H1, and no component was
classified `CLOSED_FOR_LEARNING_DDO01`.

The requested registry, excitation mask, and pilot dataset are intentionally
absent because the binding H1 semantic check precedes prospective evidence
construction and triggered the mandatory stop.

## Authorization boundary

H2-H6, F2-F4, atlas generation, target-geometry analysis, model fitting, neural
architectures, optimization, time integration, rollout, and solver-in-the-loop
work were not executed. DDO-01C is not authorized.
