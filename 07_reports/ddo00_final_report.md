# DDO-00 final report

## Decision

The spatial discretization-defect and identifiability contract is frozen with terminal status:

`DDO_SPATIAL_DEFECT_AND_IDENTIFIABILITY_CONTRACT_FROZEN`

This is a specification-stage result. It is not evidence that H1–H6 pass, that a learned correction is feasible, or that any architecture is suitable.

## Completed scope

DDO-00 established:

- the fixed-time target \(d_h^*=R_h\mathcal L(q^*)-\mathcal L_h(R_hq^*)\), with no time integration, next-state target, or \(\Delta t\) scaling;
- component definitions for interpolation/density, density-rate, pressure-gradient, viscosity/Laplacian, and total spatial RHS defects;
- a barotropic WCSPH-compatible continuum/discrete pairing and a firewall against model-form mismatch;
- an explicit Layer G/C/P/N observable descriptor dictionary with dimensions and normalization rules;
- deterministic F1 single-mode, F2 multi-frequency, F3 oblique/anisotropic, and F4 particle-disorder field families;
- nearest-neighbor disagreement, conditional variance, simple non-neural oracle, target-SVD, scaling, transfer, and receptive-field diagnostics;
- prospective H1–H6 decision gates and R0–R4 representation tests;
- the conservation claim boundary separating linear momentum from angular momentum and energy;
- a machine-readable status ledger and complete DDO-00 artifact manifests.

No large sweep was executed. No target atlas, statistical baseline fit, model, optimizer, integrator, trajectory, or rollout was created.

## Historical baseline audit

The historical repository was inspected read-only at observed Git HEAD `ff86f5e0b99966ad6fa5896fe3d9a0c3f001cd57`. Its worktree already contained untracked project directories; none was modified.

The selected import is the smallest dependency-closed static subset that provides the DDO-01 operator ingredients with the strongest directly relevant historical code-verification evidence:

- `neighborhood.py` for deterministic periodic topology;
- `kernels.py` for Wendland C4, interpolation, consistency and differential candidates;
- `conservative_pressure.py` for the pressure pair operator;
- `conservative_viscosity.py` for the viscous pair operator;
- `__init__.py` as package marker.

The five files were copied byte-for-byte. Both historical and copied SHA-256 values are identical and recorded in `06_manifests/inherited_artifact_manifest.csv` and `inherited_artifact_sha256.txt`.

The import deliberately excludes support-design loaders tied to historical experiment paths, integrators, dynamic solvers, benchmark fixtures, training/model code, sealed tests, and historical reference trajectories. This minimizes dependency and prevents accidental temporal or sealed-test inheritance.

## Inherited qualification boundary

Stage 01C reported 18 passing static tests and a broad formula-specific matrix for reciprocal pressure/viscosity forces. The admissible inherited claims are limited to those static formulas and stated test domains. In particular:

- pressure pair antisymmetry and centrality are formula-specific;
- viscosity pair antisymmetry and nonpositive pair power do not imply angular-momentum conservation;
- kernel/consistency candidates do not establish universal convergence under disorder;
- static operator evidence does not qualify dynamic rollout or the complete solver.

The historical Stage01 full V2 qualification was not restored. Later historical evidence retained `V2_QUALIFICATION_FAIL`, including the independent shear hard-gate failure. DDO-00 inherits that limitation explicitly and does not convert high-resolution SPH into truth.

## Scientific risk register

1. Signal may sit near numerical/reference uncertainty, especially for symmetric regular layouts.
2. Similar local descriptors may correspond to different spectral mixtures, yielding irreducible conditional variance.
3. One-hop locality may fail even when regional/global summaries help.
4. Zero-net-force projection can discard a physically real externally balanced or boundary-related component; periodic internal-force cases must be distinguished.
5. Reciprocal pair representability may be algebraically easy yet poorly conditioned or nonregular across cases.
6. Apparent scaling can be confounded when \(h\), \(\Delta x\), \(kh\), neighbor count, and disorder change together.
7. EOS/model-form mismatch can masquerade as discretization defect if continuum and SPH terms are not bound identically.

The prospective gates route these risks before any architecture decision.

## Compliance audit

- `REFERENCE_IN_MODEL_INPUT = false`.
- `HIGH_RESOLUTION_SPH_IS_TRUTH = false`.
- No LCDF_03 or LCDF_10 decoding.
- No Stage09 creation.
- No historical modification.
- No neural training, optimizer, dynamic rollout, or sealed-test reuse.
- H1–H6 remain `NOT_EVALUATED_DDO00`.

## Authorized boundary

Only DDO-01 analytical spatial-defect atlas work is authorized. Architecture selection, neural implementation/training, solver-in-the-loop work, autonomous rollout, and performance claims remain closed.
