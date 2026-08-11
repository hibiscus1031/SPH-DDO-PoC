# DDO-01A-R prospective requalification report

## Decision

All 24 mandatory, prospectively registered fresh cases pass CA-01. The terminal
status is:

`DDO01_ANALYTICAL_PREFLIGHT_REQUALIFIED`

This is a new prospective result. It does not alter or retroactively qualify
the original DDO-01A status
`DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP`.

DDO-01B is authorized as the next stage but was not executed here.

## Prospective integrity

Before any registered numerical case was evaluated:

- CA-01 was frozen as
  `DDO_CA01_NUMERICAL_QUALIFICATION_CONTRACT_FROZEN`;
- the complete 24-case registry was written and bound at SHA-256
  `403aedcc4cb9c4ac194d044850e7a698d11ff8331cffa5a9041907e9a60d83e7`;
- phases and jitter seeds were derived only from the frozen SHA-256 mapping;
- the original DDO-01A report and manifest remained byte-identical.

No registered case was removed. The original 24 DDO-01A outcomes were not used
as the formal qualification set.

## Bound execution

The run used CPU float64, `C_fp = 128`,
`eps64 = 2.220446049250313e-16`, one PyTorch intra-op thread, one inter-op
thread, and deterministic algorithms. The five imported Stage01C sources all
matched their frozen SHA-256 values.

The registered matrix contains:

- `N = 16, 32`;
- `h/dx = 4`;
- modes `(1,0)` and `(1,1)`;
- density, longitudinal-velocity, and transverse-velocity F1 probes;
- regular and 5% jittered layouts;
- new per-case analytical phases and new jitter seeds.

No F2, F3, F4 atlas, pilot dataset, H1 evaluation, regression, neural model,
optimizer, time integration, or rollout was executed.

## Qualification summary

| Gate or diagnostic | Result |
|---|---:|
| mandatory cases passed / failed | `24 / 0` |
| maximum derivative A/B discrepancy | `1.7763568394002505e-15` |
| maximum derivative gate fraction | `0.011110805637915012` |
| maximum continuum A/B discrepancy | `1.7763568394002505e-15` |
| deterministic-repeat target discrepancy | `0` |
| neighbor-permutation target discrepancy | `1.7763568394002505e-14` |
| compensated-accumulation target discrepancy | `1.709743457922741e-14` |
| independent-geometry target discrepancy | `3.907985046680551e-14` |
| component-closure residual | `0` |
| minimum component-closure bound | `2.5963406984639898e-15` |
| primary `U_num` range | `2.842170943040401e-16` to `2.38808436074034e-13` |
| float32 precision-degradation diagnostic maximum | `1.1634107703795138e-4` |

All primary and independent topology audits pass. Every independent brute-force
edge-key set equals the imported-path set; all sets are reciprocal, unique, and
in bounds. The independent geometry path recomputed target/operator outputs,
so raw position error was not inserted into an acceleration uncertainty.

## Independent derivative qualification

Evaluator A used the closed-form F1 expressions. Evaluator B independently
constructed each registered field and differentiated it through PyTorch
automatic differentiation. Every derivative and continuum channel satisfied

`delta_ref <= 128*eps64*S`.

The worst channel consumed about 1.11% of its frozen allowance. Absolute and
scale-normalized values for every channel and case are retained in
`ddo01ar_manifest.json`.

## Float64 uncertainty construction

For each target and case the manifest records, in matching physical units:

- `U_round`;
- `Delta_ref`;
- `Delta_repeat`;
- `Delta_perm`;
- `Delta_comp` from componentwise Python `math.fsum`;
- `Delta_accum = max(Delta_perm, Delta_comp)`;
- `Delta_geometry` from the independent target-output path;
- `Delta_identity` where applicable;
- the frozen additive `U_num`.

Observed component ranges were:

| Target | `U_num` range | max `Delta_accum` | max `Delta_geometry` |
|---|---:|---:|---:|
| interpolation density | `2.8878e-14`–`3.1251e-14` | `1.1102e-15` | `8.8818e-16` |
| density summation | `2.8878e-14`–`3.1251e-14` | `1.1102e-15` | `8.8818e-16` |
| density rate | `2.8422e-15`–`2.6800e-14` | `7.7716e-16` | `7.7716e-16` |
| pressure acceleration | `2.8422e-16`–`2.3881e-13` | `1.7764e-14` | `3.9080e-14` |
| viscosity acceleration | `2.8422e-16`–`2.0539e-15` | `1.9429e-16` | `3.6082e-16` |
| total acceleration | `1.1561e-15`–`2.3881e-13` | `1.7764e-14` | `3.9080e-14` |

The float32 comparison is stored only as
`precision_degradation_diagnostic`. It is not included in any `U_num` and is
not available for a later H1 ratio.

## Sign, dimensions, decomposition, and closure

Every target retained the frozen positive-additive convention
`SPH + defect = analytical`. Each component sign residual passed against its
own CA-01 `U_num`.

Density/interpolation, density rate, and acceleration channels remained
dimensionally separate. Pressure and viscosity used the same EOS, physical
viscosity, field, domain, support convention, and sampled state on continuum
and SPH sides.

For every case,

`d_acceleration = d_pressure + d_viscosity`

had zero residual and passed the CA-01 bound
`U_acc + U_pressure + U_viscosity`.

## Claim boundary

This result establishes validity of the registered analytical target pipeline
under CA-01. It does not evaluate target signal, scaling, identifiability,
locality, representation, generalization, or architecture performance.

`REFERENCE_IN_MODEL_INPUT = false` remains in force. No high-resolution SPH
truth, LCDF_03, LCDF_10, Stage09, neural training, optimizer, temporal target,
or rollout was used.
