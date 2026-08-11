# CA-01 change record

## Change identity

- Amendment: CA-01 — Prospective Numerical Qualification and Uncertainty.
- Date frozen: 2026-08-10.
- Parent scientific status:
  `DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP`.
- DDO-00 contracts modified: no.
- Original DDO-01A report or manifest modified: no.

## Rule change

- Old rule: unspecified / incomplete.
- New rule: the numerical tolerances, characteristic scales, independent
  paths, additive uncertainty construction, float32 boundary, closure gate,
  fresh-case generation, and decision rules defined by CA-01.
- Reason: contract gap discovered during DDO-01A.
- Evidence already seen: yes.
- Retroactive qualification: prohibited.

The original DDO-01A result permanently remains
`DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP`. CA-01 creates a new,
prospectively registered verification-only evaluation, DDO-01A-R; it does not
reinterpret the original 24 cases.

## Evidence observed before the change

Before CA-01 was written, the following original DDO-01A outcomes were known:

- maximum derivative A/B discrepancy: `1.7763568394002505e-15`;
- deterministic repeat: `0`;
- neighbor-order discrepancy: `2.4868995751603507e-14`;
- float32/float64 diagnostic: `1.0730433520755867e-4`;
- acceleration-component closure: `0`.

They were not used to choose `C_fp = 128`, the additive uncertainty rule, the
fresh-case phases, or the fresh jitter seeds.

## Affected evidence and claim boundary

CA-01 applies only to DDO-01A-R and to later H1 work if DDO-01A-R requalifies.
It cannot alter any DDO-00 or original DDO-01A conclusion. Even a successful
DDO-01A-R result authorizes only the separately defined DDO-01B F1 micro-pilot;
it does not itself pass H1, authorize an atlas, select an architecture, or
authorize neural training.
