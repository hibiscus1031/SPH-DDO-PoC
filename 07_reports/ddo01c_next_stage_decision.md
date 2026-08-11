# DDO-01C next-stage decision

## Decision

Assign:

`DDO01C_H2_UNRESOLVED_CONTRACT_GAP`

DDO-01C has no componentwise H2 PASS or FAIL because no H2 scientific target
was observed. DDO-01D balanced-atlas generation is not authorized.

## Required prospective repair

Before any DDO-01C registry or target is created, a new prospective amendment
must freeze at least:

1. the exact controlled families and complete parameter slices for refinement,
   support-ratio, spectral, and regular-versus-disorder contrasts;
2. canonical field-track membership plus SHA-256 mappings for phase, jitter,
   and pairing identifiers;
3. the formal H2 response measure, component-specific normalization, case norm,
   and all replicate/track/family weights;
4. the exact local-slope estimator, coordinate choice, admissible interval,
   handling of zero/nonpositive values, and slope-uncertainty calculation;
5. the monotonicity statistic, expected sign, denominator, tie/plateau rule,
   and treatment of uncertainty overlap;
6. the between-replicate dispersion and median level-to-level change
   statistics, including units and the precise comparison;
7. propagation of CA-01 `U_num` through every H2 statistic and any H2-specific
   resampling scheme, deterministic seed, replicate count, and quantile rule;
8. family-to-component and component-to-project
   `PASS`/`FAIL`/`UNRESOLVED` mappings, including invalid cases, insufficient
   levels, mixed regular/disorder results, and support-ratio dependence; and
9. the exact dimensionless relative-effect diagnostic and characteristic
   floor, explicitly descriptive and not an H2 gate.

The amendment must be frozen without using any DDO-01C target, slope, plot, or
classification. Afterward, DDO-01C must begin with a fresh complete registry;
DDO-01B-R cases may remain historical anchors only if the amendment explicitly
permits and defines that use.

## Closed work

H3-H6, F2-F4 balanced-atlas construction, PCA/SVD target geometry,
nearest-neighbor or regression prediction, MLP, GNN, Transformer, optimizer,
time integration, rollout, solver-in-the-loop, high-resolution SPH truth,
LCDF_03, and LCDF_10 remain closed.
