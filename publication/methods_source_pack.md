# Methods source pack

## Target and component roles

The fixed-time target is `d_h* = R_h L(q*) - L_h(R_h q*)`. It excludes time-integration, next-state and rollout errors. Primary mappings are density rate, pressure-gradient acceleration and viscosity-Laplacian acceleration. Total acceleration is derived as pressure plus viscosity; interpolation density is an algebraic diagnostic.

## Reference qualification

Closed-form manufactured derivatives were checked against an independent automatic-derivative route. Periodic graph topology, repeatability, neighbor permutation, independent geometry reconstruction, compensated accumulation, positive-additive sign convention and component closure were audited. Float32 degradation remained non-gating; the primary uncertainty was float64. High-resolution SPH was never treated as truth.

## H1 and H2

H1 required component signal-to-uncertainty ratio `R_c >= 10` and strict bootstrap lower bound `L95_c > 5`, excluding analytically unexcited cases rather than inserting zeros. H2 used prospectively frozen monotonicity and dispersion gates on refinement and spectral tracks at canonical `h/dx=4`; descriptive slopes were not convergence-order fits.

## Atlas and firewall

The development atlas contained 512 static analytical cases, balanced across F1--F4. Observable and reference archives were physically separated. Reference-minus-low-cost values, analytical derivatives and targets were prohibited inputs. DDO-02A additionally classified fields as runtime-direct, runtime-estimable or design-only.

## H3/H4 semantics

Five folds were separated by field lineage. Exactly 128 SHA-selected particles per case were used. Feature scaling used training-fold median/IQR and excluded zero-IQR channels fold-locally. Exact cKDTree queries used k=5, 10 and 20; fixed ridge/polynomial-ridge and kNN models were diagnostic non-neural oracles. H3 required all frozen DNN, conditional-variance, oracle-error, family-robustness and coverage gates. H4 could be evaluated only after H3 PASS.

## Prospective redesign and fresh test

CA-06 froze 30 reference-free moment, angular, observable-frame and quadratic-reconstruction descriptors. Four DESIGN_ONLY fields were excluded. Frame degeneracy and reconstruction fallbacks were fixed before fresh targets. DDO-02B then generated 384 new cases (96 per family) with new phases/seeds and zero field-lineage overlap with DDO-01D, yielding 49,152 formal samples.

## Reproducibility boundary

All authoritative values and file hashes are enumerated in `claim_ledger.csv` and `06_manifests/ddo02z_final_evidence_manifest.json`. No neural model, optimizer, integrator, rollout, or solver-in-loop experiment belongs in Methods.
