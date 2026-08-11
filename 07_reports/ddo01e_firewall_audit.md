# DDO-01E observable-feature firewall audit

`REFERENCE_IN_MODEL_INPUT=false` — pass.

- All 39 unique derived-feature source fields are `obs__*` or
  permitted connectivity/count identifiers; invalid source fields: none.
- The observable feature and reference target caches occupy separate files and
  carry separate schemas/hashes.
- All 80 fold checkpoints were searched for reference/target field names in
  standardization exclusions; failures: none.
- `U_num`, target RMS, H1 ratio, H2 slope, relative defect, analytical labels,
  and `target_ref__*` never enter a feature matrix.
- `obs__eps64`, `obs__mach`, and `obs__reynolds` remain in provenance and are
  excluded from metric matrices; other zero-IQR channels are excluded per
  training fold only.
- Scaling is fitted from the other four observable folds only. No target-side
  statistic scales an input.

The machine-readable audit is `data/identifiability/ddo01e_firewall_audit.json`.
