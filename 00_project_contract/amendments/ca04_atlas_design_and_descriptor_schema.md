# CA-04 prospective atlas sampling, roles, and descriptor schema

## Status and scope

CA-04 prospectively freezes the complete DDO-01D development-atlas design
before any fresh atlas target is evaluated. DDO-00 authorized finite parameter
pools but did not uniquely specify a complete F1-F4 registry, family quotas,
target-free down-selection, component roles, or physical dataset schemas.

CA-04 does not evaluate H3 or H4, fit a predictive model, select an
architecture, modify CA-01/CA-02/CA-03, or relabel any historical terminal
state. The 204 DDO-01C-R cases remain `HISTORICAL_H2_ANCHORS` and do not count
toward the fresh quota.

## Component roles

| Component | Frozen DDO-01D role | Historical H2 scope retained |
|---|---|---|
| density rate | `PRIMARY_DYNAMIC_TARGET` | `H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT` |
| pressure gradient acceleration | `PRIMARY_DYNAMIC_TARGET` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` |
| viscosity/Laplacian acceleration | `PRIMARY_DYNAMIC_TARGET` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` |
| total acceleration | `DERIVED_CLOSURE_DIAGNOSTIC` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` |
| interpolation/density | `ALGEBRAIC_DENSITY_DIAGNOSTIC` | `H2_SCALING_FAIL_REGULAR_SCOPE` |

The total defect must satisfy exactly, particlewise,
`d_total=d_pressure+d_viscosity`. It is not an independent physical mechanism.
Interpolation/density remains separate from dynamic RHS targets. No target is
divided by an empirical H2 power of `h`.

## Exact fresh-atlas budget

The fresh budget is exactly 512 complete static `DEVELOPMENT_ATLAS` cases:

| Macro-family | Quota | Target-free candidate count | Selection unit |
|---|---:|---:|---|
| F1 | 128 | 3888 | single complete case |
| F2 | 128 | 1872 | single complete case |
| F3 | 128 | 1872 | single complete case |
| F4 | 128 | 972 base candidates | eight 16-case matched blocks |

The normative exact numeric table is
`06_manifests/ddo01d_case_registry.json`, SHA-256
`b4365cd02cd56d917282a490712247a3a287ce405261c4e80c474cc09739d1df`.
It contains all 512 canonical IDs, numerical values, derived coordinates,
component roles, and deterministic neighbor-permutation mappings. No registry
case contains a target, H1 ratio, H2 slope, PCA/SVD quantity, or reference
field.

## Authorized candidate construction

Only the frozen DDO-00 pools are used:

- resolutions `N={16,24,32,48,64}`;
- `h/dx={2,3,4,5}`;
- F1 modes `(1,0),(2,0),(3,0),(1,1),(1,2),(2,1)`;
- F2 mode sets `[(1,0),(0,2)]`, `[(1,1),(2,-1)]`, and
  `[(1,0),(2,1),(0,3)]`;
- F3 modes `(1,1),(1,2),(2,1)`;
- density amplitudes `{0.0025,0.005,0.01,0.02}`;
- velocity amplitudes `{0.025,0.05,0.1,0.2}`;
- phases `{0,pi/4,pi/2}`;
- density, longitudinal, and transverse isolated probes;
- disorder fractions `{0,0.025,0.05,0.1}` and seeds
  `{20260811,20260817,20260823}`; and
- CPU float64 primary arithmetic with float32 diagnostic only.

F2 distributes the selected total active amplitude equally over its two or
three authorized modes. Its mode phases are cyclic permutations of the three
authorized phases. These are deterministic derived coefficients, not new
free parameter values. Candidate cases are rejected target-free when any mode
has fewer than eight points per wavelength or support is not strictly below
half the domain extent.

## Deterministic balance and down-selection

F1-F3 candidates are selected by the pure implementation
`08_scripts/ddo01d_registry_builder.py`. At each selection step it minimizes a
greedy marginal-imbalance score across resolution, `h/dx`, mode signature,
probe, active amplitude, phase signature, resolution-support strata,
probe-mode strata, and probe-amplitude strata. Exact ties are resolved by the
full SHA-256 digest of a family-domain string and canonical target-free design
metadata. Selection never uses any target or reference quantity.

F4 first selects eight target-free base continuum configurations with the same
algorithm over resolution, mode, probe, amplitude, and phase. Each base expands
to the Cartesian matched block:

`4 support ratios x 4 disorder states = 16 cases`.

Within a block, continuum field, mode, phase, resolution, amplitude, and
polarization are fixed. `h/dx` and disorder state vary. The three nonzero
disorder fractions receive authorized seeds by domain-separated SHA-256 block
ordering followed by a balanced cyclic assignment. A jitter seed remains
fixed across all four support ratios in its block. Changing `h/dx` also changes
support sampling and neighbor count; neither is claimed independently causal.

No quota deficit is reallocated because every macro-family supplies at least
128 valid configurations. No case may be replaced or removed after target
inspection.

## Dataset roles and physical separation

Every fresh case has only `DEVELOPMENT_ATLAS`. No sealed test or future H6
evidence is consumed.

The observable and reference sides are physically separate:

- `data/atlas/ddo01d_observable_atlas.json` indexes per-case compressed NumPy
  archives under `data/atlas/observable_cases/`;
- `data/atlas/ddo01d_reference_target_atlas.json` indexes separate per-case
  archives under `data/atlas/reference_cases/`; and
- `data/atlas/ddo01d_case_metadata.csv` and `.json` contain identifiers,
  target-free design metadata, numerical audit summaries, case/component RMS,
  uncertainty, roles, and historical H1/H2 labels.

Each index records every case-file SHA-256. The DDO-01D manifest binds the two
indexes, which transitively bind every archive.

`REFERENCE_IN_MODEL_INPUT=false`. Join fields are identifiers only and are not
declared deployable descriptors.

## Observable-side schema

All descriptor arrays use the `obs__` prefix. No absolute global coordinate is
stored as a default descriptor.

### Edge arrays — Layer G/P

- local `edge_row`, `edge_col` join indices;
- `obs__relative_position_over_h` using minimum-image displacement;
- `obs__distance_over_h`; and
- `obs__velocity_difference_over_U0`.

### Particle arrays — Layer G

- neighbor count and nominal-count normalization;
- `h/L0` and `h/dx`;
- kernel-weighted covariance tensor divided by `h^2`;
- covariance eigenvalues divided by `h^2`, eigenvalue ratio, and anisotropy;
- coefficient of neighbor-distance variation; and
- prescribed jitter fraction.

### Particle arrays — Layer C

- zeroth kernel-moment error `S0-1`;
- complete first-moment tensor error and Frobenius norm;
- discrete gradient-of-constant vector multiplied by `h` and its norm; and
- observed kernel volume and count-based support completeness.

The first moment is
`sum_j V_j (x_j-x_i) outer grad_i W_ij - I`, using the frozen displacement and
gradient sign convention.

### Particle arrays — Layer P

- `rho/rho0` and `(rho-rho0)/rho0`;
- `p/P0`;
- normalized SPH divergence and vorticity;
- normalized strain trace, Frobenius norm, and determinant; and
- baseline pressure, viscosity, and total acceleration contributions divided by
  `A0`.

### Particle arrays — Layer N

- `h/dx`, maximum and RMS `kh`, mode count;
- Mach, Reynolds-like number, jitter fraction; and
- float64 machine epsilon.

All normalizations are the previously frozen dimensional or prescribed
case-parameter normalizations. No target-derived normalization or dataset-fitted
standardization is created in DDO-01D.

## Reference-target schema

All reference arrays use the `target_ref__` prefix and are stored only in the
reference archive:

- continuum density, density rate, pressure acceleration, viscosity
  acceleration, and total acceleration;
- matching low-cost SPH counterparts retained for target audit;
- raw continuum-minus-SPH defects for interpolation/density, density rate,
  pressure, viscosity, and derived total acceleration; and
- authorized dimensionless defect normalizations.

Case/component metadata separately retains CA-01 `U_num`, CA-02-compatible case
RMS, continuum RMS, `E_rel=T/max(C,U_round)`, component role, H1 qualification,
and historical H2 scope. No empirical `h^p` normalization is stored.

## Numerical qualification and float32 provenance

Every case reruns all mandatory CA-01 audits. Invalid cases remain registered as
`NUMERICAL_INVALID` and are not replaced. Float32 remains non-gating. Each case
records exactly one `precision_diagnostic_topology_mode`:

- `INDEPENDENT_FLOAT32_REBUILD`; or
- `PRIMARY_TOPOLOGY_CAST_FLOAT32` when a float32 rebuild cannot preserve a
  reciprocal support graph.

These protocol classes are reported separately and neither enters `U_num`.

## Release and claim boundary

Release requires exact count and balance, canonical uniqueness, deterministic
registry replay, topology and closure audits, unit/sign checks, finite
descriptors, all file hashes, and a field-by-field firewall audit. Missing or
degenerate descriptors are reported without silent removal.

DDO-01D may claim only atlas construction, design scope, numerical validity,
mechanism/design category distribution, and deployable descriptor availability.
H3-H6, target PCA/SVD, nearest-neighbor target disagreement, conditional target
variance, prediction, regression, neural models, optimization, integration,
rollout, solver-in-the-loop, and improved-solver claims remain prohibited.
