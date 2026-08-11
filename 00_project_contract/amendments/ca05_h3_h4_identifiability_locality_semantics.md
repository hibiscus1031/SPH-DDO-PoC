# CA-05 prospective H3/H4 identifiability and locality semantics

## Status and pre-outcome boundary

CA-05 prospectively resolves operational gaps found by the DDO-01E semantic
executability precheck. The DDO-00 H3/H4 scientific thresholds exist and are
unchanged, so the appropriate route is an implementation-semantics amendment,
not `DDO01E_H3H4_UNRESOLVED_CONTRACT_GAP`.

No DDO-01E reference archive, target response, nearest-neighbor target
disagreement, conditional target variance, regression result, predictive score,
locality result, or target SVD/PCA result was inspected before this amendment,
its pure semantics implementations, and its synthetic tests were frozen.

CA-05 authorizes only non-neural information diagnosis over the 512
`DEVELOPMENT_ATLAS` cases. It does not create validation, sealed-test, H5, H6,
architecture-selection, neural-training, integration, rollout, or corrected-
solver evidence.

## 1. Formal components and response

The formal independent H3/H4 targets are `density_rate`,
`pressure_gradient_acceleration`, and `viscosity_laplacian_acceleration`.
`interpolation_density` is evaluated separately as an
`ALGEBRAIC_DENSITY_DIAGNOSTIC`. `total_acceleration` is never fitted as an
independent response; any diagnostic total prediction is exactly the sum of
pressure and viscosity predictions.

Responses are the raw fixed-time particle defects from the reference side.
Fixed CA-01 dimensional scales may be used for numerically stable arithmetic,
but all dimensional scores are reconstructed and no empirical `h^p`, target
PCA coordinate, target RMS, H1 ratio, H2 slope, relative defect, or `U_num`
enters an observable feature.

Scalar responses remain scalar. Vector responses remain two-Cartesian-component
vectors. Primary metrics use squared Euclidean vector norm without division by
the number of Cartesian components. Cartesian component and vector-angle views
are descriptive supplements only.

## 2. FIELD_LINEAGE_ID and five diagnostic folds

The canonical target-free lineage payload contains, in this exact order:

`macro_family`, `field_subtype`, `mode_indices`, `phases_radians`, `probe`,
`polarization`, and `active_amplitude`.

It excludes resolution, `dx`, `h`, `h/dx`, layout/disorder state, disorder seed,
particle count, target values, and audit outcomes. The ID is

`DDO01E|FIELD_LINEAGE|` + SHA-256(canonical compact JSON payload).

For F4, equality with the prospectively frozen `f4_matched_block_id` grouping is
mandatory; all 16 support/disorder variants of each block share one lineage.

Within each F1-F4 family, unique lineage IDs are ordered by SHA-256 of
`DDO01E|FOLD|<macro_family>|<FIELD_LINEAGE_ID>` and assigned round-robin to
`DIAGNOSTIC_FOLD_0` through `DIAGNOSTIC_FOLD_4`. All cases from a lineage inherit
the same fold. No particle-level split is permitted. These folds are diagnostic
development partitions, not validation or generalization partitions.

## 3. Formal particle sample and weighting

Every numerically complete case contributes exactly 128 unique particles.
Particle IDs are ordered by the full SHA-256 digest of

`DDO01E|PARTICLE|<canonical_case_id>|<particle_id>`

with particle ID as a final deterministic tie-break, and the first 128 are
selected. The sample registry is frozen before reference arrays are opened.

All particle statistics are first reduced within case. Cases are equally
weighted within fold, folds are equally weighted for overall summaries, and
components are never pooled into a single score. Family and disorder summaries
use the same particle-to-case order. A component/project decision therefore
cannot be dominated by high-resolution cases.

## 4. Observable content sets

The exact source-field layers are frozen below. Join fields `particle_id`,
`edge_row`, and `edge_col` are connectivity only and not metric channels.

### Layer G

`obs__relative_position_over_h`, `obs__distance_over_h`,
`obs__neighbor_count`, `obs__neighbor_count_normalized`,
`obs__support_h_over_L0`, `obs__support_over_dx`,
`obs__covariance_over_h2`, `obs__covariance_eigenvalues_over_h2`,
`obs__covariance_eigenvalue_ratio`, `obs__anisotropy`,
`obs__neighbor_distance_cv`, `obs__jitter_fraction`.

### Layer C

`obs__zeroth_moment_error`, `obs__first_moment_error`,
`obs__first_moment_error_frobenius`,
`obs__gradient_constant_times_h`,
`obs__gradient_constant_times_h_norm`, `obs__kernel_volume`,
`obs__support_count_completeness`.

### Layer P

`obs__velocity_difference_over_U0`, `obs__rho_over_rho0`,
`obs__delta_rho_over_rho0`, `obs__pressure_over_P0`,
`obs__sph_divergence_normalized`, `obs__sph_vorticity_normalized`,
`obs__strain_trace_normalized`, `obs__strain_frobenius_normalized`,
`obs__strain_determinant_normalized`,
`obs__pressure_acceleration_over_A0`,
`obs__viscosity_acceleration_over_A0`,
`obs__total_acceleration_over_A0`.

### Layer N

`obs__kh_max`, `obs__kh_rms`, `obs__mode_count`, `obs__mach`,
`obs__reynolds`, `obs__eps64`.

The nested sets are exactly `C0=G`, `C1=G+C`, `C2=G+C+P`, and
`C3=G+C+P+N`. Fields never move between sets after outcomes are observed.

Tensor/vector observable fields are not flattened in a global Cartesian frame.
Particle tensors become rotation-invariant trace, determinant, Frobenius norm,
and ordered symmetric eigenvalue scalars where applicable; particle vectors
become Euclidean norms. Signed scalar divergence, vorticity, strain trace, and
scalar state channels retain sign. Edge vectors are used only through distance,
norm, radial dot, and 2-D cross pseudoscalar summaries.

`obs__eps64`, `obs__mach`, and `obs__reynolds` remain in schema/provenance but
are marked `CONSTANT_IN_CURRENT_ATLAS_EXCLUDED_FROM_METRIC`. They never enter a
distance, regression matrix, or variance-based selector. Any other channel with
zero training-fold IQR is fold-locally excluded and recorded; it is not deleted
from the atlas.

## 5. Operational locality ladder

DDO-00's pair-only rung remains a supplementary edge-attribution view because
it cannot by itself map a complete particle response. The formal DDO-01E ladder
is the following monotone particle-response ladder:

- `L0`: central-particle scalar/invariant observables already stored at particle
  level. Edge-only fields are absent.
- `L1`: `L0` plus deterministic one-hop summaries over the exact observable SPH
  graph. For every eligible node scalar, append neighbor mean, standard
  deviation, minimum, and maximum. For eligible edge fields append the frozen
  invariant edge summaries.
- `L2`: `L1` plus the same mean, standard deviation, minimum, and maximum over
  the exact unique union of nodes reachable within at most two graph hops.
- `L3`: `L2` plus permutation- and periodic-translation-invariant whole-case
  mean, standard deviation, minimum, and maximum of particle scalar/invariant
  observables, together with observable particle and edge counts.

Self is included once in every node set. Graph reachability uses only
`edge_row/edge_col`; targets cannot change a receptive field. Feature names are
prefixed by rung and aggregation, making `L0` a strict subset of `L1`, `L1` of
`L2`, and `L2` of `L3`. L3 is a broad regional/case-global information
diagnostic and is not called a Transformer, architecture, or deployable learned
global representation.

## 6. Training-fold-only standardization and distance

For each held-out outer fold and each Cx/Ly matrix, calculate the median and IQR
from the other four folds only. A channel is retained iff its training IQR is
finite and strictly positive. Transform retained values by `(x-median)/IQR`.
No clipping, target scaling, feature selection, or held-out-fold fitting is
performed. Euclidean feature distance is divided by `sqrt(retained_dimension)`.

Training samples are ordered by SHA-256 of their canonical case/particle key.
Exact `scipy.spatial.cKDTree` search uses `p=2`, `eps=0`, and one worker. Ties
inherit this frozen training order. Approximate search is prohibited.

## 7. Nearest-neighbor disagreement and coverage

All candidates come from the four training folds. Because lineages are wholly
held out, no candidate shares the query case or `FIELD_LINEAGE_ID`. Primary
nearest-neighbor size is `K=10`, uniform weight `1/K`.

For query particle `i`, define the numerator as mean squared raw-target
difference to its K feature neighbors. Its matched random baseline consists of
K unique training samples drawn without replacement by NumPy PCG64 seeded with
the full SHA-256 integer of `DDO01E|BASELINE|<sample_key>`. Define the particle
ratio as numerator divided by the matched baseline mean squared difference;
zero/zero is unresolved and a zero denominator with positive numerator is
infinite. Reduce by particle median and 90th percentile within case, then the
same statistic within fold, then equally across folds. Also retain feature
radius, reciprocal-neighbor fraction, neighbor-family composition, and scalar
sign disagreement or vector negative-dot-product disagreement.

The development-radius threshold is training-fold-only: for each training
sample, find its nearest sample from a different lineage and take the 95th
percentile using NumPy `method="inverted_cdf"`. Coverage is the fraction of
held-out queries whose nearest permitted training distance is no larger than
that radius; reduce particle to case mean, case to fold mean, then fold mean.

## 8. Conditional target variance

For K in `{5,10,20}`, use the same exact feature neighbors. At a query, compute
the unbiased sample covariance trace of the K raw target vectors, equivalently
the sum of squared deviations from the neighbor mean divided by `K-1`. Divide
by the unbiased covariance trace over all training-fold target samples after
giving every training case total weight one. The primary statistic uses K=10;
K=5 and K=20 are sensitivity diagnostics.

Reduce query ratios by particle mean within case, case mean within fold, and
equal fold mean. Unconditional variance is always reported separately. A
deterministic 2,000-replicate lineage bootstrap resamples held-out lineages
within family and fold; its 2.5% and 97.5% `inverted_cdf` quantiles form the
95% interval. The seed is the full SHA-256 integer of
`DDO01E|BOOTSTRAP|<component>|<content>|<locality>|<metric>`.

## 9. Non-neural diagnostic oracles

The complete preregistered oracle bundle is:

1. K-nearest-neighbor mean at K `{5,10,20}`;
2. linear ridge with intercept and fixed `alpha=1.0` on the robust-standardized
   feature matrix; and
3. degree-two polynomial ridge with fixed `alpha=1.0` using only the following
   available scalar base channels and no interaction with unavailable layers:
   `neighbor_count_normalized`, `anisotropy`, `zeroth_moment_error`,
   `first_moment_error_frobenius`, `gradient_constant_times_h_norm`,
   `delta_rho_over_rho0`, `sph_divergence_normalized`, and `kh_rms`.

Ridge is solved by deterministic float64 linear algebra, not an iterative
optimizer. The fixed alpha and K values are not selected from outcomes.

Held-out scores are raw-dimensional equal-case NRMSE, MAE, signed scalar or
vector bias, vector-angle error above `max(10*U_num(case), 1e-6*S_component)`,
and R2 against the training-fold mean-target baseline. Overall and family NRMSE
first average particle squared vector norm within case, then average cases.
Baseline improvement is `1-RMSE_oracle/RMSE_mean`. The best oracle for an H3
gate is the preregistered oracle with smallest equal-fold NRMSE; all oracle
results remain reported and this selection does not authorize an architecture.

## 10. H3 evidence bundle and verdict

For every component and Cx/Ly combination, H3 passes only if all frozen DDO-00
gates pass:

- DNN case/fold median `<=0.25` and 90th percentile `<=0.60`;
- primary K=10 Cvar point `<=0.25` and upper 95% bound `<=0.35`;
- at least one oracle NRMSE `<=0.50` with mean-baseline RMSE improvement
  `>=0.20`;
- every F1-F4 family NRMSE for that oracle `<=0.75`; and
- coverage `>=0.90` under the frozen training-only radius.

A nonfinite required statistic, fewer than eight held-out cases in a fold, a
numerically invalid case, no retained feature, or failed firewall maps to
`H3_IDENTIFIABILITY_UNRESOLVED`. Otherwise a complete gate failure maps to
`H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE`, and complete success maps to
`H3_OBSERVABLE_MAPPING_IDENTIFIABLE`.

The formal component H3 verdict uses the broadest preregistered combination
`C3/L3`; the complete 16-combination ladder remains visible and cannot
retroactively change that verdict. Interpolation is diagnostic only. Total is
derived from pressure plus viscosity predictions and receives no independent
formal H3 verdict.

Project aggregation is `DDO01E_OBSERVABLE_MAPPING_AND_LOCALITY_QUALIFIED` only
when all three primary components pass H3 and receive a bounded L0-L2 H4 rung;
`DDO01E_IDENTIFIABILITY_QUALIFIED_LOCALITY_PARTIAL` when all three pass H3 but
one or more requires L3 or has unresolved locality;
`DDO01E_COMPONENTWISE_IDENTIFIABILITY_MIXED` when primary H3 statuses differ;
and `DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` when all three are formal H3
not-identifiable. Any unresolved formal primary statistic maps the project to
the mixed state with the unresolved components listed, unless every primary is
unresolved, which maps to `DDO01E_H3H4_UNRESOLVED_CONTRACT_GAP` only for a new
contract/execution gap, not an adverse metric outcome.

## 11. H4 smallest sufficient context

H4 uses C3 only and is evaluated only for a component whose formal C3/L3 H3
verdict is identifiable. For candidate rung `l`, compute paired lineage-
bootstrap degradation against every broader rung `m>l`:

`delta_E=(NRMSE_l-NRMSE_m)/NRMSE_m` and `delta_C=Cvar_l-Cvar_m`.

Rung `l` is sufficient only if it independently passes H3, every upper 95%
paired-bootstrap `delta_E <=0.05`, and every upper 95% paired-bootstrap
`delta_C <=0.05`. Select the first passing rung in L0,L1,L2,L3 order. L3 has no
broader comparator and is sufficient iff it passes H3.

Map L0 to `PARTICLE_LOCAL_INFORMATION_SUFFICIENT`, L1 to
`ONE_HOP_LOCALITY_SUPPORTED`, L2 to
`EXTENDED_BOUNDED_LOCALITY_SUPPORTED`, and L3 to
`STRICT_LOCALITY_NOT_SUPPORTED_GLOBAL_CONTEXT_REQUIRED`. If formal H3 fails,
map to `OBSERVABLE_MAPPING_NOT_IDENTIFIABLE`; if paired evidence is incomplete,
map to `H4_LOCALITY_UNRESOLVED`.

## 12. Required stratification and post-verdict SVD

Pressure and viscosity metrics are separately reported for regular,
`jitter_0.025`, `jitter_0.05`, and `jitter_0.1`, including C0 versus C1 at L1.
Every component is also reported for F1-F4 and overall. Empty disorder strata
are reported as not available outside F4 and never fabricated.

Formal H3/H4 verdicts and their input metric hashes are frozen before target
SVD/PCA. The later analysis is labeled `TARGET_SUBSPACE_DIAGNOSTIC`, uses
centered target covariance only, cannot alter verdicts, and cannot be called a
physical manifold or intrinsic-dimension proof.

## 13. Python figure contract

Python is the exclusive backend for plots, previews, SVG/PDF/TIFF exports, and
visual QA. The five required figures are quantitative grids whose core claim is
to expose componentwise, locality, consistency-layer, disorder, and family
evidence without hiding adverse strata. Primary exports are editable-text SVG,
with PDF and 600-dpi TIFF companions. Values come only from frozen DDO-01E
metric tables; figures never define a verdict.

