# DDO-01A analytical and provenance preflight report

## Decision

DDO-01A is **not qualified to PASS**. The terminal preflight status is:

`DDO01_ANALYTICAL_PREFLIGHT_UNRESOLVED_CONTRACT_GAP`

All executable numerical and provenance checks completed without an observed
failure, but the frozen DDO-00 record does not specify the numerical derivative
tolerance, the dtype-scaled component-closure tolerance, or the unique rule for
combining the required uncertainty diagnostics into a conservative uncertainty
upper bound. Assigning any of those rules now would invent a prospective gate
after DDO-00 was frozen.

Consequently:

- `DDO01_ANALYTICAL_PREFLIGHT_PASS` is not assigned;
- atlas expansion is not authorized;
- DDO-01B through DDO-01Z are not evaluated;
- no pilot dataset, atlas dataset, diagnostic fit, neural model, optimizer,
  integrator, trajectory, or rollout was created.

## Frozen-contract binding

The preflight loaded and SHA-256-bound all required DDO-00 contracts. Full
hashes are recorded in `06_manifests/ddo01a_manifest.json`. Every DDO-00 file
whose digest is listed inside `ddo00_manifest.json` was independently checked
against that manifest before execution; no mismatch was observed.

The five imported Stage01C source files were rehashed. All copied digests match
both `inherited_artifact_manifest.csv` and `inherited_artifact_sha256.txt`:

| Imported source | SHA-256 check |
|---|---:|
| `structure_preserving/__init__.py` | MATCH |
| `structure_preserving/neighborhood.py` | MATCH |
| `structure_preserving/kernels.py` | MATCH |
| `structure_preserving/conservative_pressure.py` | MATCH |
| `structure_preserving/conservative_viscosity.py` | MATCH |

The scientific root is not a Git work tree, so no project commit identifier
exists to bind. This fact is recorded rather than replaced with a synthetic
identifier. The historical read-only evidence repository was observed at HEAD
`ff86f5e0b99966ad6fa5896fe3d9a0c3f001cd57`, equal to the DDO-00 ledger. Its
previously documented untracked project directories remain present; none was
modified by DDO-01A.

## Execution environment

| Item | Bound value |
|---|---|
| OS / architecture | macOS 26.5.2, arm64 |
| Python | 3.13.9, `/opt/miniconda3/bin/python3` |
| PyTorch | 2.10.0 |
| NumPy | 1.26.4 |
| SciPy | 1.17.1 |
| Device | CPU |
| Primary dtype | `torch.float64` |
| PyTorch intra-op / inter-op threads during preflight | 1 / 1 |
| Deterministic algorithms during preflight | enabled |
| PyTorch default dtype during preflight | `torch.float64` |

Before the script-local deterministic configuration, PyTorch reported 4
intra-op threads, 8 inter-op threads, deterministic algorithms disabled, and
default dtype `torch.float32`. No thread-count environment variable or
`PYTHONHASHSEED` was set. The preflight overrides are process-local and fully
recorded in the manifest.

## Executed F1 preflight matrix

The preflight used only the frozen pilot axes:

- periodic domain `[0,1)^2`;
- resolutions 16 and 32 particles per axis;
- compact support ratio `h/dx = 4`;
- modes `(1,0)` and `(1,1)`;
- density, longitudinal-velocity, and transverse-velocity F1 probes;
- regular and 5% jittered layouts;
- jitter seed `20260811`;
- `rho0 = 1`, `c0 = 10`, `nu = 0.01`, density amplitude 0.01, and velocity
  amplitude 0.1;
- float64 as the primary computation, with float32 used only as a diagnostic.

This gives 24 static preflight cases. It is not an expanded atlas.

## Independent continuum derivative evaluators

Evaluator A implements the frozen closed-form single-mode expressions.
Evaluator B rebuilds the F1 field values and obtains first and second
derivatives through PyTorch automatic differentiation. B does not call A and
does not reuse A's derivative expressions.

Across density, pressure, velocity-gradient, divergence, vorticity, strain,
and vector-Laplacian channels:

| Diagnostic | Maximum absolute discrepancy |
|---|---:|
| Evaluator A vs B, all derivative channels | `1.7763568394002505e-15` |
| Continuum component values from A vs B | `1.7763568394002505e-15` |

These values are consistent with float64 roundoff, but the result is recorded
as `MEASURED_NOT_GATE_QUALIFIED`, not PASS, because DDO-00 gives no numerical
derivative tolerance or uniquely defined dtype-scaling multiplier.

## Periodic geometry and deterministic topology

Every case was checked against the imported chunked all-pairs reference. The
maximum observed audit values were:

| Audit item | Maximum |
|---|---:|
| duplicate directed edges | 0 |
| missing self edges | 0 |
| nonreciprocal nonself edges | 0 |
| out-of-bounds edges | 0 |
| omitted strict-support edges | 0 |
| unexpected out-of-support edges | 0 |
| minimum-image displacement error | `1.1102230246251565e-16` |

All edge-key sets were unchanged by deterministic random edge permutation.
The float32 diagnostic graph also had the same edge-key set as the float64
primary graph in all 24 cases.

## Sign, operator, dimensions, and closure audit

The target was constructed only as continuum minus SPH:

`d_h = R_h L(q*) - L_h(R_h q*)`.

The identity `SPH RHS + d_h = continuum RHS` had a maximum absolute residual of
`2.220446049250313e-16`, confirming the positive-additive correction sign in
the implemented arithmetic.

The paired channels were:

| Target channel | Continuum side | SPH side | Dimension in 2-D |
|---|---|---|---|
| interpolation / density | sampled density | raw kernel interpolation and density summation | `M L^-2` |
| density rate | `-rho div(v)` | `-rho div_h(v)` | `M L^-2 T^-1` |
| pressure | `-(1/rho) grad(p)` | imported conservative pressure acceleration | `L T^-2` |
| viscosity | `nu laplacian(v)` | imported conservative viscosity acceleration | `L T^-2` |
| total acceleration | pressure + viscosity | pressure + viscosity | `L T^-2` |

The same barotropic EOS `p = c0^2 (rho-rho0)`, constant kinematic viscosity,
domain, sampled field, particle layout, and compact-support convention were
used on both sides. Density reconstruction was not added to the RHS. Scalar
density-rate and vector acceleration channels were not concatenated.

The exact implemented acceleration-component identity
`d_acceleration = d_pressure + d_viscosity` had zero residual in every case.
This is strong arithmetic evidence, but it is not labeled a formal frozen-gate
PASS because DDO-00 does not state the required dtype-scaled closure tolerance.

## Numerical implementation diagnostics

| Diagnostic | Maximum absolute discrepancy across 24 cases |
|---|---:|
| deterministic float64 repeat | `0.0` |
| permuted neighbor accumulation order | `2.4868995751603507e-14` |
| float32 vs float64 SPH operator | `1.0730433520755867e-4` |
| float32 vs float64 raw defect target | `1.0730433520755867e-4` |
| acceleration component closure | `0.0` |
| positive-correction identity | `2.220446049250313e-16` |

Float32 is a diagnostic only; the frozen pilot primary dtype is float64. The
float32 comparison is not silently substituted for a float64 uncertainty
floor. The measured raw target RMS ranges were retained as preflight evidence:

| Raw target | RMS range over all preflight cases |
|---|---:|
| interpolation density | `4.1575e-4` to `1.2488e-2` |
| density summation | `4.1575e-4` to `1.2488e-2` |
| density rate | `0` to `7.8568e-2` |
| pressure acceleration | `0` to `5.9767e-1` |
| viscosity acceleration | `0` to `3.0034e-3` |
| total acceleration | `2.0080e-4` to `5.9767e-1` |

Zeros are expected in isolated F1 probes and are not treated as componentwise
H1 evidence. No cancellation in total acceleration was used to qualify a
component.

## Mandatory contract gap and stop

The following required rules cannot be recovered from the frozen DDO-00 files:

1. `analytical_field_family_spec.md` requires a dtype-scaled derivative
   tolerance, but provides neither an absolute/relative formula nor a numerical
   multiplier.
2. `operator_decomposition.md` requires per-case closure tolerances based on
   dtype and accumulation uncertainty, but provides no construction rule or
   numerical multiplier.
3. `identifiability_metrics.md` names derivative, dtype, accumulation-order,
   and identity diagnostics for the uncertainty floor, but does not specify how
   to combine them, which statistic is the conservative upper confidence bound,
   or how to construct that bound for the pilot hierarchy.

The user instruction requires the **exact frozen** gate and procedure and
forbids inventing, relaxing, reinterpreting, or retrospectively replacing a
frozen gate. Therefore the observed small discrepancies cannot be converted
into a formal PASS by choosing a new tolerance or uncertainty rule.

Execution stops at DDO-01A. A prospective contract amendment may define the
missing rules, but it cannot retroactively qualify this original preflight and
must record that these results have already been observed.

## Compliance

- `REFERENCE_IN_MODEL_INPUT = false`; no model-input dataset was created.
- `HIGH_RESOLUTION_SPH_IS_TRUTH = false`.
- No F2/F3/F4 atlas expansion was performed; the pilot `(1,1)` and jitter
  combinations were used only for the authorized preflight audit.
- No LCDF_03, LCDF_10, Stage09, historical sealed test, or historical source
  modification occurred.
- No neural network, optimizer, diagnostic model fit, temporal integration,
  rollout, solver-in-the-loop, or architecture claim occurred.
