# Supplementary Methods: operational qualification definitions

## S1. Scope and meaning of operational identifiability

Throughout the manuscript, *identifiability* denotes an operational qualification concept for the sampled mapping from deployment-compatible observables to the fixed-time spatial discretization defect. A component is operationally identifiable only when all prospectively frozen empirical H3 criteria are satisfied on field-lineage-held-out cases. This usage is not a proof of classical structural identifiability, global injectivity, uniqueness over an unrestricted state space, or suitability of a neural architecture. Conversely, failure to satisfy the criteria establishes only that the tested observable representation and instantaneous route did not qualify over the frozen evidence scope.

The target for component (c) is the raw fixed-time defect (d_{jic}) at particle (i) of case (j). Scalar responses remain scalar, and vector responses retain both Cartesian components. Squared Euclidean vector norms are not divided by the number of Cartesian components. Analytical-reference fields construct the target only; they and all target-derived quantities are excluded from the deployment-observable path.

## S2. Numerical/reference uncertainty

Primary arithmetic is CPU float64. For case (j) and dimensionally homogeneous channel (c), the roundoff allowance is

\[
U_{\mathrm{round}}(j,c)=128\,\epsilon_{64}S(j,c),
\]

where (S(j,c)) is the maximum of the frozen dimensional scale, the infinity norm of the analytical operator output, and the infinity norm of the SPH operator output. The primary numerical/reference uncertainty is the prospectively fixed additive bound

\[
U_{\mathrm{num}}(j,c)=U_{\mathrm{round}}+\Delta_{\mathrm{ref}}+\Delta_{\mathrm{repeat}}
+\Delta_{\mathrm{accum}}+\Delta_{\mathrm{geometry}}+\Delta_{\mathrm{identity}}.
\]

Here, (Delta_{\mathrm{ref}}) is the target change between independent closed-form and automatic-differentiation continuum routes; (Delta_{\mathrm{repeat}}) is the deterministic repeat discrepancy; and (Delta_{\mathrm{accum}}) is the larger of the neighbour-permutation and compensated-accumulation discrepancies. The remaining terms measure independent periodic-geometry reconstruction and, for total acceleration, pressure-plus-viscosity identity closure. The terms are added in their target units; they are not combined in quadrature or calibrated after observing H1. Float32-versus-float64 degradation is reported separately and does not enter (U_{\mathrm{num}}).

## S3. Signal-resolvability qualification (H1)

For scalar defects, the case root-mean-square magnitude is

\[
T_{jc}=\left(N_j^{-1}\sum_i d_{jic}^{2}\right)^{1/2},
\]

and for vector defects it is

\[
T_{jc}=\left(N_j^{-1}\sum_i\lVert\mathbf d_{jic}\rVert_2^{2}\right)^{1/2}.
\]

Let (E_c) contain the analytically excited, valid, complete cases and (M_c=|E_c|). The component magnitude uses equal case weighting,

\[
T_c=\left(M_c^{-1}\sum_{j\in E_c}T_{jc}^{2}\right)^{1/2},
\]

while the conservative component uncertainty is (U_c=\max_{j\in E_c}U_{\mathrm{num}}(j,c)). The separation ratio is (R_c=T_c/U_c). It compares defect magnitude with qualified numerical/reference uncertainty; it is not a physical signal-to-noise ratio and does not quantify model-form or experimental uncertainty. The point criterion is (R_c\geq10).

The second H1 criterion is a stratified group bootstrap over complete cases. Analytically unexcited component-case pairs are excluded rather than inserted as zero targets. Within each resolution-by-layout stratum, the original number of cases is sampled with replacement for exactly 10,000 deterministic replicates. Each replicate recomputes (T_c^{(b)}) with equal case weighting and divides it by the fixed full-evidence (U_c). The lower bound (L_{95,c}) is the 0.05 quantile using the inverted empirical cumulative-distribution convention. H1 requires (L_{95,c}>5), at least eight eligible cases, and valid mandatory numerical/reference audits in addition to the point criterion.

## S4. Controlled scaling qualification (H2)

For fixed dimensional component scale (S_c), define (Y_{jc}=T_{jc}/S_c), (u_{jc}=U_{\mathrm{num}}(j,c)/S_c), and (Y_{jc}^{\pm}=(T_{jc}\pm U_{\mathrm{num}}(j,c))/S_c). A point is log-admissible only when its numerical audits are valid and (T_{jc}-U_{\mathrm{num}}(j,c)>0). For adjacent levels (a,b), ordered by increasing formal coordinate (x), the descriptive local log slope is

\[
p=\frac{\log Y_b-\log Y_a}{\log x_b-\log x_a}.
\]

The propagated uncertainty interval is

\[
p_{-}=\frac{\log Y^{-}_b-\log Y^{+}_a}{\log(x_b/x_a)},\qquad
p_{+}=\frac{\log Y^{+}_b-\log Y^{-}_a}{\log(x_b/x_a)}.
\]

An interval supports the expected positive sign only when (p_->0); (p_+<0) indicates the opposite sign, and (p_-\leq0\leq p_+) denotes a plateau or uncertainty overlap. Local slopes are descriptive and are not fitted or interpreted as convergence orders.

For track (t), the monotonicity fraction (m_t) is the fraction of valid adjacent replicate intervals with (p_->0). Tracks are equally weighted to obtain (M_{\mathrm{family}}=\operatorname{mean}_t(m_t)), which must be at least 0.75. Replicate dispersion is evaluated in log-response space. At each level, (D_{tl}) spans the largest replicate upper log bound to the smallest replicate lower log bound, and (D_t) is its median over levels. The adjacent-level change (C_t) is the median non-overlapping separation between uncertainty intervals over replicates and levels. Every mandatory track must satisfy (D_t<C_t). Each formal component/family/layout decision additionally requires two independent tracks, at least three levels per track, three matched replicates per level, admissible responses, and valid numerical audits. Refinement and spectral families are evaluated separately at the canonical support ratio (h/\Delta x=4); both must pass for a layout scope to qualify.

## S5. Observable-identifiability qualification (H3)

Feature channels are robust-standardized using the training-fold median and interquartile range; zero-interquartile-range channels are removed within that fold. Exact Euclidean nearest neighbours are drawn only from the four training folds after excluding the held-out field lineage. Feature distance is divided by the square root of retained feature dimension. The primary neighbourhood size is (K=10), with (K=5) and (K=20) retained as sensitivity diagnostics.

For a query particle, nearest-neighbour disagreement is the mean squared raw-target difference to its (K) feature neighbours divided by the corresponding mean squared difference to a deterministic matched random baseline. Particle ratios are reduced to within-case median and 90th percentile, then to fold summaries, and finally with equal fold weighting. The frozen limits are a disagreement median no greater than 0.25 and a 90th percentile no greater than 0.60. A favourable median cannot replace a failing tail criterion.

Conditional target variance is the unbiased covariance-trace estimate among the (K) feature neighbours divided by the equal-case-weighted unconditional target covariance trace in the training folds. Query ratios are averaged within case, cases within fold, and folds equally. A deterministic 2,000-replicate lineage bootstrap provides the 95% interval. The primary (K=10) point estimate must be no greater than 0.25 and its upper 95% bound no greater than 0.35.

The preregistered non-neural diagnostic oracles are (K)-nearest-neighbour means for (K\in\{5,10,20\}), ridge regression with fixed regularization, and degree-two polynomial ridge on the frozen scalar subset. Oracle normalized root-mean-square error is the equal-case held-out RMSE divided by held-out target RMS. Mean-baseline improvement is (1-\mathrm{RMSE}_{\mathrm{oracle}}/\mathrm{RMSE}_{\mathrm{mean}}). At least one oracle must have normalized error no greater than 0.50 and improvement of at least 0.20, and its error must not exceed 0.75 in any required field family. These oracles diagnose regularity; they are not learned production corrections or architecture comparisons.

Coverage is the fraction of held-out queries whose nearest permitted training distance does not exceed a training-only development radius. That radius is the training-set 95th percentile of nearest-different-lineage distance under the inverted empirical cumulative-distribution convention. Coverage is reduced from particles to equally weighted cases and folds and must be at least 0.90. Coverage does not replace any ambiguity or oracle criterion.

An H3 component passes only when every applicable disagreement, conditional-variance, oracle-error, oracle-improvement, family-robustness, and coverage gate passes. A complete adverse metric outcome is distinct from an unresolved computation. The manuscript reports this all-gates operational decision without extending it to classical structural identifiability or untested observable routes.

## S6. Field-lineage folds and weighting

Field lineage is constructed from target-free manufactured-field metadata: macro family, field subtype, mode indices, phases, probe, polarization, and active amplitude. Resolution, support ratio, layout, disorder seed, particle count, targets, and audit outcomes are excluded. All cases with one lineage enter the same one of five deterministic folds; matched controlled-disorder variants share a lineage. Consequently, particles from the same field realization cannot appear on both sides of a held-out diagnostic.

All particle statistics are first reduced within case. Cases receive equal weight within a fold, and the five folds receive equal weight in overall summaries. Components are never pooled into one score. This hierarchy prevents high-resolution cases, which contain more particles, from dominating formal qualification.

## S7. Formal particle sampling

Each numerically complete development or fresh case contributes exactly 128 unique particles to formal H3 diagnostics. Particle identifiers are ordered by a deterministic SHA-256 key constructed without reference-target access, and the first 128 are selected. The sample registry is frozen before reference arrays are opened. Thus, the 512-case development atlas contributes 65,536 formal samples and the 384-case fresh atlas contributes 49,152 formal samples.

## S8. Formal H3 sample versus frame-audit populations

The 49,152 fresh formal H3 samples are the fixed 128-particle-per-case subsample used for neighbour, variance, oracle, family, and coverage diagnostics. The directional-frame fallback audit instead examines every particle environment in all 384 fresh cases. Its denominator is therefore 627,264 full particle environments, not the formal H3 subsample. The fallback occurred in 515,904 environments, corresponding to 82.246710%.

## S9. Observable-frame degeneracy

The tested local two-dimensional frame is the principal frame of the observable second weighted particle moment. The first-axis sign is fixed lexicographically from observable geometry, and the second axis is chosen to produce determinant (+1). The frame is declared degenerate when the normalized eigenvalue gap is below (10^{-6}). A degenerate environment is flagged and deterministically uses the global identity frame. The reported fallback fraction therefore measures frequent degeneracy of this specific observable-defined frame construction. It is not evidence of failure of equivariance, graph neural networks, rotationally equivariant learning, or other frame choices.

## S10. Consumed development evidence and fresh evidence

The 512-case balanced mechanism atlas was designated development evidence when created. It supported the initial operational-identifiability assessment and subsequent attribution of descriptor, disorder, tail, moment, reconstruction, and directional effects. Once used to select redesign hypotheses, it became consumed observable-design evidence and could not be relabelled as fresh support for the redesign.

The 30 expanded deployment-compatible descriptors and their normalization, transformation, conditioning, and fallback rules were frozen before fresh targets were evaluated. Formal requalification then used 384 new cases, 96 from each of the single-mode, multimode, directional/mechanism, and controlled-disorder families, with new phases and disorder seeds and zero field-lineage overlap with the development atlas. No development case contributed formal evidence to the fresh decision. This separation supports a prospective test of the redesigned observables; it does not establish generalization beyond the frozen fresh scope.
