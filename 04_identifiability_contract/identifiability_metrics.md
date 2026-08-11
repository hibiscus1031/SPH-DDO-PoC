# Identifiability metrics contract

## Mapping and data separation

The prospective mapping is \(\Phi_h(q_h)\mapsto d_h^*\), where \(\Phi_h\) contains only online-available Layer G/C/P/N observables. Reference fields are used to construct \(d_h^*\) only. Every diagnostic table must be generated after a schema audit confirms that no `target_ref__` column, target-derived normalization, case label encoding the analytical answer, or reference-minus-low-cost quantity enters \(\Phi_h\).

Samples are grouped by complete field/layout configuration. Cross-validation and bootstrap resampling operate on groups, not individual particles, to prevent particles from the same field realization appearing on both sides. Normalization is fitted within development groups only.

All vector metrics are reported for Cartesian norm and for longitudinal/transverse components relative to the declared wave frame when available. This target-aligned frame is a diagnostic view, not a deployable input unless its direction is reconstructible from online observables.

## A. Feature-space nearest-neighbor target disagreement

Within each declared receptive field, standardize scalar observables using robust development-set median and IQR. For rotation-covariant vector/tensor features, compare invariant scalars or use a declared alignment metric; do not flatten orientation-dependent components without alignment.

For each held-out sample \(i\), find the \(K=10\) nearest development samples subject to excluding its own case and seed. Define

\[
D_{NN}=
\frac{\sum_i\sum_{j\in N_K(i)}w_{ij}\|\widehat d_i-\widehat d_j\|^2}
{\sum_i\sum_{j\in B_K(i)}w_{ij}\|\widehat d_i-\widehat d_j\|^2},
\]

where \(B_K(i)\) is a deterministic matched-size random baseline and weights sum to one per \(i\). Report median, 90th percentile, group-bootstrap 95% interval, and coverage versus feature-space radius. A low average with a high tail is not sufficient; sparse/unsupported regions are reported separately.

Also report reciprocal-neighbor consistency, neighbor family composition, and target sign disagreement. The target is never used to select neighbors.

## B. Conditional target variance

Estimate local conditional variance by cross-fitted neighborhoods or fixed feature bins chosen without target access:

\[
C_{var}=\frac{\mathbb E[\operatorname{tr}\widehat{\operatorname{Cov}}(\widehat d\mid\Phi)]}
{\operatorname{tr}\widehat{\operatorname{Cov}}(\widehat d)}.
\]

Report bias-corrected within-neighborhood variance, between-case composition, effective sample count, and bootstrap interval. Evaluate sensitivity to \(K\in\{5,10,20\}\). This is evidence about the sampled descriptor atlas, not proof of global mathematical identifiability.

## C. Simple diagnostic oracle baselines

Allowed non-neural baselines are:

- K-nearest-neighbor averaging with \(K\in\{5,10,20\}\);
- linear least squares and ridge with a log-spaced regularization grid selected inside development groups;
- degree-two polynomial regression on a preregistered scalar invariant subset, with ridge stabilization.

Report group-held-out NRMSE, MAE, signed bias, vector-angle error above a target-magnitude floor, and \(R^2\) alongside a mean-target baseline. `NRMSE = RMSE / target_RMS` is computed per target component from held-out raw dimensional values. These are regularity diagnostics, not selected production models. No neural network, optimizer, or architecture comparison is allowed.

## D. Target geometry diagnostics

PCA/SVD may describe centered target covariance. Report explained-variance curves, stability across field families/resolutions, and reconstruction error. Use only language such as “empirical linear covariance subspace.” It must not be called the true physical manifold, and PCA coordinates may not leak into observable inputs.

## E. Signal and uncertainty

For each component, estimate target RMS \(S_d\) and a reference/numerical uncertainty floor \(U_d\) from independent derivative cross-checks, dtype repeats, accumulation-order checks, and exact operator identities where applicable. Define \(R_{signal}=S_d/U_d\). If \(U_d\) is indistinguishable from zero, use the conservative upper confidence bound on uncertainty, not literal division by zero.

## F. Scaling and held-out transfer

At fixed continuum field and support ratio, report defect norms against \(h\) and \(kh\), local log-slopes between adjacent admissible levels, monotonicity, and replicate dispersion. Ridge/linear trends are descriptive. Generalization diagnostics hold out at least one resolution and one wave magnitude as entire groups; interpolation and extrapolation are labeled separately.

## Interpretation boundary

Low disagreement or conditional variance is evidence only over the sampled support. High disagreement is a direct warning that descriptors are insufficient, the target is noisy, or the receptive field is too small. The diagnostics cannot distinguish these causes without the H1 uncertainty and locality ladders. No DDO-00 result is reported because no atlas was executed.
