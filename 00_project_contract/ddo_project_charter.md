# DDO project charter

## Identity and primary question

- Project: SPH-DDO — Learning Structure-Preserving Discretization-Defect Operators for Smoothed Particle Hydrodynamics.
- Stage: DDO-00, discretization-defect definition and identifiability contract.
- New root: `/Users/xiejinbo/Documents/SPH-DDO-PoC`.
- Historical evidence root: `/Users/xiejinbo/Documents/SPH-PIO-PoC`, read-only.
- Primary question: can the spatial discretization defect of a low-cost SPH operator be inferred from quantities available from the low-cost SPH state itself?

This is a scientifically independent project. It is not Stage09 and does not continue the historical stage sequence. LCDF_03 and LCDF_10 are outside the evidence scope and must not be decoded.

## Frozen object of learning

For a sufficiently smooth manufactured continuum state \(q^*(x)\), continuum spatial operator \(\mathcal L\), sampling map \(R_h\), and the corresponding SPH semi-discrete spatial operator \(\mathcal L_h\), the primary target is

\[
d_h^* = R_h\mathcal L(q^*)-\mathcal L_h(R_hq^*).
\]

This target is evaluated at a fixed instant. It contains no time-integration error, next-state error, dynamic rollout error, or division by \(\Delta t\). Component targets and sign conventions are frozen in `02_defect_definitions/`.

## Information firewall

`REFERENCE_IN_MODEL_INPUT = false`.

Analytical/manufactured reference information may be used only to construct or audit targets. It may not enter candidate deployable descriptors, their normalization statistics, neighborhood selection, train/development/test routing, or any proxy derived from reference-minus-low-cost differences. Prohibited inputs include \(q_h-q_{ref}\), \(\rho_h-\rho_{ref}\), \(v_h-v_{ref}\), \(a_h-a_{ref}\), \(d_h^*\), and all equivalents requiring reference access.

Absolute global particle coordinates are not default features. Periodic DDO-01 descriptors use relative minimum-image geometry. A later boundary study may authorize boundary-relative coordinates only through an amended, prospective contract.

## Reference hierarchy

1. Closed-form analytical derivatives of manufactured fields.
2. Independently evaluated symbolic or automatic derivatives, cross-checked against closed form.
3. Independently converged numerical continuum references, only after a separate uncertainty qualification.

`HIGH_RESOLUTION_SPH_IS_TRUTH = false`. Refining the same SPH scheme does not create truth and is not permitted as the primary DDO-01 target reference.

## Scientific scope

DDO-00 freezes definitions, descriptors, field families, prospective diagnostics, gates, representation hypotheses, inheritance boundaries, and provenance. DDO-01 may generate an analytical spatial-defect atlas under these contracts.

DDO-00 performs no neural training, optimizer creation, learned-model fitting, dynamic rollout, next-state prediction, sealed-test reuse, or solver-in-the-loop work. The only future fitting allowed before architecture selection consists of explicitly diagnostic nearest-neighbor, closed-form linear/ridge, or low-order polynomial baselines using observable inputs.

Architecture selection is downstream of signal, scaling, identifiability, locality, and representation evidence. No MLP, GNN, Transformer, pair-force network, or other neural architecture is selected or authorized here.

## Frozen hypotheses

All six statements remain hypotheses with status `NOT_EVALUATED_DDO00`:

- H1 SIGNAL: the spatial defect is resolvable above reference and numerical uncertainty.
- H2 SCALING: the defect depends systematically on \(h\), \(kh\), and related discretization parameters.
- H3 IDENTIFIABILITY: online-observable low-cost descriptors contain enough information to predict the defect.
- H4 LOCALITY: a bounded particle neighborhood is sufficient.
- H5 STRUCTURE: a useful part of the defect is representable in a structure-compatible correction interface.
- H6 GENERALIZATION: conditioning on numerical descriptors transfers across at least some held-out resolutions or frequencies.

No hypothesis is marked PASS by DDO-00.

## Historical inheritance boundary

Only the smallest dependency-closed Stage 01C static operator subset is imported byte-for-byte: package initializer, deterministic periodic neighborhood, Wendland/consistency operators, conservative pressure, and conservative viscosity. Historical Stage 01C evidence supports limited static claims: reciprocal pressure-force antisymmetry and centrality; reciprocal viscous-force antisymmetry; nonnegative viscous coefficient and nonpositive viscous power under its tested matrix; and stated periodic-neighborhood/consistency diagnostics.

It does not support a claim that the full solver, dynamic disorder response, spatial convergence, independent shear benchmark, resource behavior, or complete Stage01 V2 qualification passed. The historical terminal boundary remains `V2_QUALIFICATION_FAIL`; full V2 qualification was not restored. Imported source identity is recorded in `06_manifests/`.

## Governance and change control

- Contracts and prospective gates must be frozen before inspecting DDO-01 target outcomes.
- Any later change must record the old value, new value, reason, timestamp, affected evidence, and whether results had already been seen.
- A post-outcome change cannot retroactively qualify the original gate.
- Reference-only data and observable descriptors must be stored in separately named fields and audited before any diagnostic fit.
- Field configurations, seeds, units, normalizations, source hashes, and software environment must be manifest-bound.
- Failures and non-identifiability evidence are retained, not tuned away.

## Terminal status and authorization

DDO-00 terminal status: `DDO_SPATIAL_DEFECT_AND_IDENTIFIABILITY_CONTRACT_FROZEN`.

Authorized next stage: **DDO-01 — Analytical Spatial-Defect Atlas**, limited to deterministic field sampling, static continuum/SPH operator evaluation, uncertainty estimation, descriptor construction, and the preregistered non-neural diagnostics.

Not authorized: neural model training, Transformer implementation, solver-in-the-loop training, autonomous rollout, temporal-loss construction, or performance claims.
