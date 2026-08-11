# CA-01 final report

## Decision

CA-01 is frozen with terminal status:

`DDO_CA01_NUMERICAL_QUALIFICATION_CONTRACT_FROZEN`

This is a prospective contract result, not a numerical requalification result.
It does not alter the permanent original DDO-01A status
`DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP`.

## Repaired omissions

CA-01 freezes:

- CPU float64 primary arithmetic, `eps64 = numpy.finfo(float64).eps`, and
  `C_fp = 128`;
- channel-specific characteristic scales derived from the existing dimensional
  contract;
- the A/B derivative gate `delta_ref <= C_fp*eps64*S`;
- independent repeat, neighbor-order, compensated-accumulation, and periodic
  geometry paths;
- the unique additive float64 uncertainty rule
  `U_num = U_round + Delta_ref + Delta_repeat + Delta_accum + Delta_geometry + Delta_identity`;
- exclusion of float32 degradation from primary float64 uncertainty;
- the component-closure gate based on component uncertainty bounds;
- deterministic SHA-256 generation of a fresh, verification-only F1 matrix;
- pass, failure, and unresolved decision routes for DDO-01A-R.

The already observed original discrepancies are recorded in both the contract
and change record. They were not used to tune the new rules.

## Fresh-case freeze

The 24-case DDO-01A-R registry was created before numerical evaluation and is
bound by SHA-256
`403aedcc4cb9c4ac194d044850e7a698d11ff8331cffa5a9041907e9a60d83e7`.
It preserves the frozen F1 scientific axes while replacing phases and jitter
seeds through the prospective SHA-256 mapping. No registered case may be
removed after outcomes are observed.

## Authorization boundary

CA-01 authorizes only execution of DDO-01A-R against the frozen registry.
DDO-01B remains closed until and unless DDO-01A-R assigns
`DDO01_ANALYTICAL_PREFLIGHT_REQUALIFIED`. H1, atlas generation, diagnostic
regression, neural work, optimization, time integration, and rollout remain
prohibited.
