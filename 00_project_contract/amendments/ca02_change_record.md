# CA-02 change record

- Project: SPH-DDO-PoC
- Amendment: CA-02 — Prospective H1 Signal-Qualification Semantics
- Date: 2026-08-10
- Preferred terminal state: `DDO_CA02_H1_SIGNAL_SEMANTICS_FROZEN`

## Motivation

The permanent stopped DDO-01B precheck found that DDO-00 and CA-01 did not
uniquely map per-case target/uncertainty evidence to the component point and
group-bootstrap H1 decision. No DDO-01B target outcome had been observed.

## Prospective repair

CA-02 freezes case RMS, equal-case component RMS, maximum-case uncertainty,
case diagnostic ratios, the component point statistic, stratified complete-case
bootstrap, full-digest deterministic PCG64 seeding, inverted-CDF lower bound,
minimum eligible count, and component verdict semantics.

The frozen scientific thresholds `10` and `>5` are unchanged. The CA-01
additive `U_num` construction and float32 exclusion are unchanged.

## Evidence boundary

Only synthetic values were used to qualify the implementation. The original
DDO-01B terminal state remains `DDO01B_H1_UNRESOLVED_CONTRACT_GAP`; it is not
relabelled. CA-02 may authorize only a separately named, freshly registered
DDO-01B-R signal pilot after all synthetic tests pass and all CA-02 artifacts
are hash-frozen.

No H1 scientific result, H2-H6 result, atlas, model fit, optimizer, time
integration, rollout, or high-resolution-SPH truth claim is created by CA-02.
