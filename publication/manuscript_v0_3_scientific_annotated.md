# Pre-learning qualification of SPH spatial discretization defects: resolvability, scaling, and limits of identifiability from instantaneous observables

**Title status:** PROVISIONAL  
**Authors:** [TO BE COMPLETED]  
**Target journal:** [TO BE SELECTED]

## Abstract

Learned numerical corrections are useful only when the correction target is sufficiently determined by information available during deployment. We examined this requirement for a fixed-time smoothed particle hydrodynamics (SPH) spatial discretization defect. The defect was defined as the sampled analytical continuum operator minus the corresponding low-cost SPH operator, without time-integration or rollout error. Analytical references and numerical uncertainty were qualified before testing signal resolvability, controlled scaling, and observable identifiability. A mechanism-stratified development atlas contained 512 manufactured-field cases, and a redesigned observable set was evaluated on 384 entirely fresh cases.

<!-- CLAIM_ID: ABSTRACT-P01 -->

All five evaluated defect components were resolved above the qualified float64 uncertainty floor. Scaling was component- and disorder-dependent: density rate retained systematic scaling in regular and tested-disorder scopes, whereas pressure-gradient and viscosity-Laplacian accelerations qualified only in the regular scope. On fresh evidence, the pressure nearest-neighbour disagreement 90th percentile was 45.54, while the density-rate diagnostic oracle normalized root-mean-square error was 0.548. All three primary dynamic mappings failed the preregistered identifiability criteria after observable redesign. Locality was therefore not interpreted, and no representation-learning or neural-correction stage was initiated. These results show that a resolvable and systematically scaling SPH defect need not satisfy identifiability from the tested deployment-compatible instantaneous observables.

<!-- CLAIM_ID: ABSTRACT-P02 -->

## 1. Introduction

Smoothed particle hydrodynamics represents continuum fields through kernel-weighted interactions among moving particles. Its spatial approximations therefore depend on resolution, kernel support, particle consistency, and local particle arrangement. Truncation and consistency analyses have shown that these factors interact, particularly when particle distributions depart from regular configurations (Quinlan et al., 2006; Litvinov et al., 2015; Sigalotti et al., 2016). Spatial discretization defects should consequently be treated as operator- and component-specific quantities rather than as a single scalar measure of SPH accuracy.

<!-- CLAIM_ID: INTRO-P01 -->

Machine learning has been used to construct data-driven discretizations and correct iterative partial differential equation solvers (Bar-Sinai et al., 2019; Um et al., 2020). It has also parameterized Lagrangian particle models (Woodward et al., 2023). AI-based SPH emulators demonstrate that particle interactions can be optimized from data (Amato et al., 2024). Differentiable SPH frameworks support inverse problems and hybrid solver-network systems (Winchenbach and Thuerey, 2026). These advances establish learned numerical correction and learned SPH as active research areas. They do not determine whether a specified correction target is recoverable from observables retained at deployment.

<!-- CLAIM_ID: INTRO-P02 -->

Several close studies delimit the contribution considered here. Kiener et al. (2023) learned vertexwise coarse-to-fine computational fluid dynamics discretization errors, while Qarariyah et al. (2025) coupled residual learning to an SPH discretization. Duraisamy (2021) identified non-uniqueness and numerical-model error confounding as concerns for machine-learning-augmented turbulence models. More recently, Katz and John (2026) reported unsuccessful validation after training several coarse-flow correction networks. Thus, discretization-error learning, SPH correction, identifiability concerns, and negative post-training correction results each have clear precedents. The unresolved issue is their ordering within a prospective qualification workflow.

<!-- CLAIM_ID: INTRO-P03 -->

A correction target can be large relative to numerical uncertainty and can vary systematically with discretization parameters, yet remain conditionally ambiguous for the available input. Model fitting cannot by itself separate information deficiency from architectural or optimization limitations. We therefore ask whether a componentwise, fixed-time SPH spatial defect is sufficiently determined by deployment-compatible instantaneous observables before selecting a neural architecture. The study separates signal magnitude, controlled scaling, and observable identifiability as independent empirical questions.

<!-- CLAIM_ID: INTRO-P04 -->

Within the documented targeted search, we did not locate a peer-reviewed study that applied this complete componentwise pre-learning identifiability gate to an SPH spatial discretization-defect target. We also did not locate one that withheld neural training after a prospectively frozen gate failed. This search-bounded position is not a claim of priority across all inverse problems or learned simulators. The present study is also distinct from any separate trained conservative-correction route, whose optimizer, stability, and support evidence would require an independent manuscript and evidence chain.

<!-- CLAIM_ID: DISC-P07 -->

The study makes four contributions. First, it defines and numerically qualifies an analytical fixed-time SPH defect with a strict observable-reference firewall. Second, it distinguishes signal resolvability (H1) from controlled scaling (H2) and observable identifiability (H3). Third, it applies non-neural conditional-ambiguity diagnostics to a balanced development atlas, followed by a prospectively fixed observable redesign and fresh requalification. Fourth, it enforces the hierarchy beyond H3: locality (H4) is interpreted only after identifiability, while representation learning (H5) and generalization (H6) require the preceding stages. This hierarchy prevents downstream model evidence from being inferred when an upstream requirement is absent.

<!-- CLAIM_ID: FORM-P04 -->

[Figure 1 near here]

## 2. Methods

### 2.1 Spatial discretization-defect formulation

Let \(q^*(\mathbf{x})\) denote a smooth manufactured continuum state, and let \(\mathcal{L}\) denote the continuum spatial operator. The maps \(\mathcal{R}_h\) and \(\mathcal{L}_h\) denote particle sampling and the corresponding SPH semi-discrete operator. The fixed-time spatial defect was defined as \(d_h^*=\mathcal{R}_h\mathcal{L}(q^*)-\mathcal{L}_h(\mathcal{R}_h q^*)\). This positive-additive sign convention means that adding \(d_h^*\) recovers the sampled continuum operator within qualified numerical uncertainty. The target excludes time integration, next-state prediction, and rollout error.

<!-- CLAIM_ID: FORM-P01 -->

Analytical and manufactured quantities were used only to construct and audit reference targets. Deployment descriptors, neighbourhood construction, normalization, routing, and diagnostic inputs could not use reference-minus-low-cost quantities or equivalent target-derived proxies. Observable and reference fields were stored separately, and the separation was audited before each identifiability assessment. This one-way information firewall ensured that the target definition could not leak into the candidate deployment inputs.

<!-- CLAIM_ID: FORM-P03 -->

[Figure 2 near here]

### 2.2 Analytical reference and numerical qualification

Closed-form derivatives of the manufactured fields provided the primary continuum reference. An independent automatic-differentiation route was used only to cross-check those derivatives. Refining the same SPH discretization was not treated as a reference solution, and high-resolution SPH was never used as truth. The resulting scope is an analytical, fixed-time assessment of spatial operators rather than an evaluation of accumulated trajectory error.

<!-- CLAIM_ID: FORM-P05 -->

Numerical qualification combined analytical-route agreement with explicit SPH graph and accumulation checks. The graph audits covered periodic topology, neighbour reciprocity, support completeness, and deterministic geometry reconstruction. Repeat evaluation, neighbour permutation, compensated accumulation, the positive-additive sign convention, and pressure-plus-viscosity component closure were also checked. Formal uncertainty was based on float64 calculations; float32 degradation remained a non-gating diagnostic.

<!-- CLAIM_ID: NUM-P01 -->

### 2.3 Manufactured-field families and component roles

Three quantities were treated as independent primary dynamic components: density rate, pressure-gradient acceleration, and viscosity-Laplacian acceleration. Total acceleration was retained only as the derived pressure-plus-viscosity closure diagnostic. Interpolation density was treated as an algebraic density diagnostic. These roles were fixed before qualification and prevented a favourable derived quantity from replacing a failed primary component.

<!-- CLAIM_ID: FORM-P02 -->

The manufactured fields comprised four mechanism families. They covered single-mode fields, multimode fields, directional or mechanism-focused fields, and controlled-disorder configurations. The disorder family included matched blocks across support ratio and perturbation level, so difficult strata were retained rather than removed after numerical evaluation. The family definitions were fixed before target construction.

<!-- CLAIM_ID: ATLAS-P02 -->

### 2.4 Signal-resolvability qualification

For component \(c\), signal resolvability compared a robust target scale \(T_c\) with qualified numerical and reference uncertainty \(U_c\) through \(R_c=T_c/U_c\). The preregistered criterion required \(R_c\geq10\) and a stratified-bootstrap lower bound \(L_{95,c}>5\). Analytically unexcited component-case pairs were excluded from the component aggregation rather than inserted as zeros. This procedure tested whether a defect rose above the numerical uncertainty floor.

<!-- CLAIM_ID: SIGNAL-P01 -->

Signal qualification was deliberately not interpreted as learnability. A component could satisfy the amplitude criteria while remaining ambiguous for deployment observables. Likewise, a later identifiability result could not be attributed to insufficient signal once signal qualification had passed. This separation preserved the distinct evidential roles of uncertainty qualification and conditional target determination.

<!-- CLAIM_ID: SIGNAL-P03 -->

### 2.5 Controlled scaling qualification

Controlled scaling was assessed prospectively on refinement and spectral tracks at the canonical formal support ratio \(h/\Delta x=4\). Separate regular and jittered scopes were evaluated with predefined monotonicity and dispersion gates. Local log slopes were reported only as descriptive summaries and were not fitted or interpreted as convergence orders. The formal outcome was therefore a componentwise statement about systematic variation within the tested tracks.

<!-- CLAIM_ID: SCALE-P01 -->

### 2.6 Mechanism-stratified development atlas

The mechanism-stratified development atlas contained 512 complete static cases. Its registry was fixed before target evaluation and was balanced across the four families, with 128 cases per family. The design exposed the observable mapping to several defect mechanisms rather than to a single refinement sequence. All case strata remained subject to the same analytical-reference, numerical-qualification, and firewall requirements.

<!-- CLAIM_ID: ATLAS-P01 -->

The 512 cases were designated development evidence from their creation. They supported the initial identifiability assessment and later failure attribution, after which they were considered consumed for observable design. They could not be relabelled as fresh evidence for the redesigned representation. This distinction enforced independence between diagnosis and formal requalification.

<!-- CLAIM_ID: ATLAS-P03 -->

Atlas qualification established case balance, numerical validity, descriptor availability, and reference separation. It did not establish predictability, locality, representation suitability, target-manifold dimension, or solver improvement. These properties required separate diagnostics and, where applicable, fresh evidence.

<!-- CLAIM_ID: ATLAS-P04 -->

[Figure 5 near here]

### 2.7 Identifiability and locality diagnostics

Observable identifiability was assessed by asking whether nearby particles in deployment-compatible feature space had sufficiently similar defects. The diagnostics combined nearest-neighbour disagreement, conditional target variance, fixed non-neural oracle error and improvement, family robustness, and feature-space coverage. The disagreement median and 90th percentile could not exceed 0.25 and 0.60, respectively. Conditional-variance and oracle-error limits were 0.35 and 0.50, while coverage had to reach 0.90. Every applicable gate had to pass.

<!-- CLAIM_ID: ID-P01 -->

The initial assessment used exactly 65,536 deterministically selected particle samples, corresponding to 128 particles from each development case. Five folds were separated by manufactured-field lineage. Feature scaling used the training-fold median and interquartile range, and zero-interquartile-range channels were removed within each fold. Exact nearest-neighbour queries used \(k=5,10,20\), while ridge, polynomial-ridge, and nearest-neighbour regressors served only as fixed diagnostic oracles.

<!-- CLAIM_ID: ID-P02 -->

### 2.8 Prospective observable redesign and fresh requalification

Candidate redesign information was classified as runtime-direct, runtime-estimable, or design-only. The manufactured-wave quantities \(kh_{\max}\), \(kh_{\mathrm{rms}}\), mode count, and jitter fraction were design-only and were excluded from the formal deployable set. Reference-free status alone was not sufficient for deployment eligibility; the information also had to be available or estimable under the intended online route.

<!-- CLAIM_ID: REDESIGN-P02 -->

Before any fresh target was evaluated, the expanded representation was fixed with 30 reference-free descriptors. These covered weighted second- to fourth-order particle moments, angular harmonics, observable-defined directional channels, and local quadratic reconstruction proxies. Descriptor dimensions, normalization, transformation behaviour, conditioning, failure flags, contextual aggregation, and frame-degeneracy fallback were specified prospectively. The design used geometric equivariance only as representation context; no equivariant neural network was implemented (Satorras et al., 2021).

<!-- CLAIM_ID: REDESIGN-P03 -->

Fresh requalification used 384 newly generated complete cases, balanced as 96 cases per family. New deterministic phases and disorder realizations produced zero field-lineage overlap with the development atlas. Exactly 49,152 particle samples entered the formal analysis. The expanded representation and all diagnostic gates remained unchanged after fresh target access.

<!-- CLAIM_ID: REQUAL-P01 -->

## 3. Results

### 3.1 Numerical qualification and defect resolvability

All 24 signal-qualification cases passed the mandatory analytical, topology, uncertainty, sign, and closure audits. The maximum discrepancy between analytical derivative routes was \(1.776357\times10^{-15}\), and the maximum component-closure residual was zero. All 204 scaling cases also passed numerical qualification. Their maximum derivative discrepancy was \(1.421086\times10^{-14}\), and every formal log response was admissible.

<!-- CLAIM_ID: NUM-P02 -->

The 512-case development atlas passed numerical qualification without post-target case replacement or failure deletion. Observable and reference-target archives remained physically separated. No empirical target normalization based on fitted powers of the smoothing length was introduced. The complete balanced atlas was therefore retained for the initial observable assessment.

<!-- CLAIM_ID: NUM-P03 -->

All 384 fresh cases passed the same mandatory fixed-time qualification before formal aggregation. The fresh release audit satisfied all 13 preregistered quality gates. Its feature-schema audit also recorded that the reference archive was not opened during observable-feature construction. These checks preserved the target-input firewall after redesign.

<!-- CLAIM_ID: NUM-P04 -->

All five components satisfied the signal-resolvability criteria over their qualified excited-case scopes. Ratios were \(2.455\times10^{11}\) for interpolation density, \(1.615\times10^{12}\) for density rate, and \(2.194\times10^{12}\) for pressure-gradient acceleration. They were \(1.405\times10^{12}\) for viscosity-Laplacian acceleration and \(1.267\times10^{12}\) for total acceleration. Bootstrap lower bounds ranged from \(2.284\times10^{11}\) to \(1.643\times10^{12}\), far above the qualification limits.

<!-- CLAIM_ID: SIGNAL-P02 -->

[Figure 3 near here]

[Table 1 near here]

### 3.2 Componentwise scaling and disorder sensitivity

Density rate passed the refinement and spectral gates in both regular and tested jittered configurations. It therefore retained systematic scaling at the canonical support ratio across the complete qualified scaling scope. This component supplied the only primary dynamic example whose scaling qualification survived the tested disorder perturbation.

<!-- CLAIM_ID: SCALE-P02 -->

Pressure-gradient acceleration and viscosity-Laplacian acceleration passed both regular-track gates but did not satisfy the jittered refinement requirement. Their formal scaling scope was therefore restricted to regular configurations. Derived total acceleration had the same regular-only status and was not used to replace either primary component. The combined result established component- and disorder-dependent scaling rather than a shared order across operators.

<!-- CLAIM_ID: SCALE-P03 -->

Interpolation density did not satisfy either regular or jittered scaling qualification and remained an algebraic diagnostic. Its signal was nevertheless strongly resolved above numerical uncertainty. This contrast provides the clearest example that resolvability alone does not establish systematic scaling. It also shows why signal and scaling require separate evidence.

<!-- CLAIM_ID: SCALE-P04 -->

[Figure 4 near here]

[Table 2 near here]

### 3.3 Initial observable-identifiability assessment

At the formal initial representation, all three primary dynamic mappings failed at least one preregistered identifiability criterion. Density rate had a disagreement 90th percentile of 2.653 and an oracle normalized root-mean-square error of 0.463. Pressure-gradient acceleration had a disagreement 90th percentile of 3.665, a conditional-variance upper bound of 1.399, and an oracle error of 1.044. Viscosity-Laplacian acceleration had a disagreement 90th percentile of 10.696 and an oracle error of 1.049. Passing individual diagnostics did not override a failed all-gates decision.

<!-- CLAIM_ID: ID-P03 -->

Formal feature-space coverage was 0.9526, exceeding the minimum of 0.90. Inadequate sampling of nearby feature points was therefore not sufficient to explain the initial outcome. Instead, the component-specific combination of disagreement tails, conditional variance, oracle error, and family sensitivity was consistent with conditional ambiguity under the tested observables.

<!-- CLAIM_ID: ID-P04 -->

[Figure 6 near here]

### 3.4 Failure attribution and prospective redesign

Within matched disorder blocks, adding simple consistency descriptors did not uniformly reduce pressure or viscosity ambiguity. The pressure conditional-variance diagnostic increased from 0.093 to 0.260 in the regular stratum and changed negligibly across the tested jitter strata. Viscosity showed the same absence of a uniform rescue. A post-verdict target singular-value decomposition was retained only as an empirical covariance diagnostic and was not interpreted as a low-dimensional physical manifold.

<!-- CLAIM_ID: ID-P05 -->

Attribution on consumed development evidence supported two hypotheses for a fresh test: observable-defined directional augmentation and component-specific feature combinations. Their best disagreement-tail reductions were 10.49% and 20.95%, respectively. Higher-order particle moments and higher-derivative proxies produced smaller diagnostic reductions of 5.63% and 6.43% and remained inconclusive. None of these consumed-evidence results constituted a renewed identifiability assessment.

<!-- CLAIM_ID: REDESIGN-P01 -->

[Figure 7 near here]

### 3.5 Fresh identifiability requalification

Density rate did not satisfy the fresh criteria after observable expansion. Its disagreement median was 0.001276, but the 90th percentile was 8.202, above the limit of 0.60. The conditional-variance upper bound was 0.1489, while the best fixed-oracle normalized root-mean-square error was 0.5481, above the limit of 0.50. Thus, favourable median and variance diagnostics did not offset the failed tail and oracle criteria. This outcome followed prior signal qualification and scaling qualification in both regular and tested-disorder scopes.

<!-- CLAIM_ID: REQUAL-P02 -->

Pressure-gradient acceleration also failed the fresh all-gates decision. Its disagreement median was 0.0008044, but the 90th percentile reached 45.54. The conditional-variance upper bound was 1.070, and the best-oracle normalized root-mean-square error was 1.010. These values exceeded the respective limits of 0.60, 0.35, and 0.50. The result concerns the tested component, cases, and expanded observable representation.

<!-- CLAIM_ID: REQUAL-P03 -->

Viscosity-Laplacian acceleration failed several fresh criteria. Its disagreement median was 0.2773, slightly above the limit of 0.25, while its 90th percentile was 26.88. The conditional-variance upper bound was 0.4042, and the best-oracle normalized root-mean-square error was 1.049. Each value exceeded its corresponding limit. The outcome does not extend to every viscosity discretization or possible observable representation.

<!-- CLAIM_ID: REQUAL-P04 -->

The observable-defined directional-frame fallback was triggered in exactly 515,904 of 627,264 particle environments, or 82.246710%. This frequency documents degeneracy of the tested frame construction rather than failure of equivariance or graph learning. Because none of the three primary mappings satisfied the fresh identifiability criteria, locality was not interpreted. No representation-learning stage or neural correction was initiated, and the tested instantaneous online route was not supported.

<!-- CLAIM_ID: REQUAL-P05 -->

[Figure 8 near here]

[Table 3 near here]

## 4. Discussion

The results first separate resolvability from scaling. Every evaluated component was far above the qualified uncertainty floor, but interpolation density did not satisfy the regular or jittered scaling criteria. A numerically visible defect therefore need not vary systematically along the tested discretization tracks. Conversely, the scaling evidence for the other components remained limited to their stated operator and disorder scopes. Signal qualification cannot substitute for scaling qualification, and neither addresses the deployment-observable mapping.

<!-- CLAIM_ID: DISC-P01 -->

The second separation is between scaling and identifiability. Density rate provides the clearest counterexample because it passed signal qualification and retained systematic scaling in regular and tested-disorder configurations. It nevertheless failed fresh identifiability through its disagreement tail and oracle error. Pressure and viscosity exhibited different patterns, with regular-only scaling and distinct conditional-ambiguity signatures. The componentwise contrast rules out a single total-acceleration or descriptor-expansion summary as a substitute for independent qualification.

<!-- CLAIM_ID: DISC-P03 -->

The third separation is between feature-space coverage and conditional identifiability. Coverage exceeded the preregistered minimum in both assessment cycles, reaching 0.9526 initially and 0.9358 after redesign. Nearby feature points were therefore available, yet their targets retained heavy disagreement tails, component-dependent conditional variance, weak oracle performance, and family sensitivity. These observations support conditional ambiguity for the tested observables, but they do not establish an architecture-independent impossibility theorem (Bellman and Åström, 1970; Stuart, 2010).

<!-- CLAIM_ID: DISC-P02 -->

Prospective separation between diagnosis and requalification strengthens the interpretation of the redesign. Directional and component-specific hypotheses were selected using consumed evidence, fixed before new targets, and evaluated on lineages with zero overlap. The frequent frame fallback limits that observable-defined directional construction. It does not imply failure of rotational equivariance, graph neural networks, or temporal representations. Those alternatives were not tested (Satorras et al., 2021).

<!-- CLAIM_ID: DISC-P04 -->

Existing work has already demonstrated learned discretizations, coarse-grid error correction, SPH residual correction, and differentiable SPH workflows. It has also identified non-uniqueness concerns and post-training correction failures (Duraisamy, 2021; Kiener et al., 2023; Qarariyah et al., 2025; Winchenbach and Thuerey, 2026; Katz and John, 2026). The contribution here is the upstream ordering of evidence. Once the tested input-target relation failed its prerequisite, architecture search could not answer the missing-information question. No neural training, optimization, time integration, rollout, or solver-in-loop evaluation was therefore justified (Ioannidis, 2022; Sandve et al., 2013).

<!-- CLAIM_ID: DISC-P05 -->

These findings are restricted to fixed-time, two-dimensional, periodic manufactured fields, the frozen SPH operators, and the tested instantaneous observables. Boundary information, temporal history, latent state, alternative sensors, learned representations, dynamic integration, and solver feedback were not evaluated. The diagnostic oracles were deliberately simple and non-neural. The target singular-value decomposition described covariance only, and high-resolution SPH was not used as truth. Consequently, the result is route-specific and cannot be generalized to all SPH defects or correction strategies.

<!-- CLAIM_ID: DISC-P06 -->

[Table 4 near here]

## 5. Conclusions

Five conclusions follow from the qualified evidence. First, the analytical fixed-time SPH defect was numerically qualified and resolved above float64 uncertainty for all five components. Second, scaling was component- and disorder-dependent: density rate qualified in regular and tested-disorder scopes, pressure and viscosity qualified only in the regular scope, and interpolation density did not qualify.

<!-- CLAIM_ID: CONC-P01 -->

Third, a spatial discretization defect may be numerically resolvable and exhibit systematic scaling without satisfying identifiability from the tested deployment-compatible instantaneous observables. Density rate provides the clearest empirical example because its systematic scaling survived tested disorder, while its fresh disagreement tail and oracle error did not satisfy the identifiability criteria.

<!-- CLAIM_ID: CONC-P02 -->

Fourth, the prospectively redesigned observables did not satisfy fresh identifiability criteria for density rate, pressure-gradient acceleration, or viscosity-Laplacian acceleration. Locality was therefore not interpreted because identifiability was its prerequisite. Fifth, no neural correction was trained, and no representation-learning or generalization claim was made. These conclusions apply only to the tested fixed-time instantaneous route and do not imply universal non-identifiability.

<!-- CLAIM_ID: CONC-P03 -->

## References

1. Amato, E., Zago, V. & Del Negro, C. A physically consistent AI-based SPH emulator for computational fluid dynamics. *Nonlinear Engineering* **13**, 20220359 (2024). https://doi.org/10.1515/nleng-2022-0359
2. Bar-Sinai, Y., Hoyer, S., Hickey, J. & Brenner, M. P. Learning data-driven discretizations for partial differential equations. *Proceedings of the National Academy of Sciences* **116**, 15344–15349 (2019). https://doi.org/10.1073/pnas.1814058116
3. Bellman, R. & Åström, K. J. On structural identifiability. *Mathematical Biosciences* **7**, 329–339 (1970). https://doi.org/10.1016/0025-5564(70)90132-X
4. Duraisamy, K. Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence. *Physical Review Fluids* **6**, 050504 (2021). https://doi.org/10.1103/PhysRevFluids.6.050504
5. Ioannidis, J. P. A. Pre-registration of mathematical models. *Mathematical Biosciences* **345**, 108782 (2022). https://doi.org/10.1016/j.mbs.2022.108782
6. Katz, S. & John, V. On limitations of several approaches for correcting coarse flow simulations with machine learning techniques. *ZAMM – Journal of Applied Mathematics and Mechanics* **106**, e70373 (2026). https://doi.org/10.1002/zamm.70373
7. Kiener, A., Langer, S. & Bekemeyer, P. Data-driven correction of coarse grid CFD simulations. *Computers & Fluids* **264**, 105971 (2023). https://doi.org/10.1016/j.compfluid.2023.105971
8. Litvinov, S., Hu, X. Y. & Adams, N. A. Towards consistence and convergence of conservative SPH approximations. *Journal of Computational Physics* **301**, 394–401 (2015). https://doi.org/10.1016/j.jcp.2015.08.041
9. Qarariyah, A., Yang, T. & Deng, F. An intelligent SPH framework based on machine-learned residual correction for elliptic PDEs. *Algorithms* **18**, 803 (2025). https://doi.org/10.3390/a18120803
10. Quinlan, N. J., Basa, M. & Lastiwka, M. Truncation error in mesh-free particle methods. *International Journal for Numerical Methods in Engineering* **66**, 2064–2085 (2006). https://doi.org/10.1002/nme.1617
11. Sandve, G. K., Nekrutenko, A., Taylor, J. & Hovig, E. Ten simple rules for reproducible computational research. *PLoS Computational Biology* **9**, e1003285 (2013). https://doi.org/10.1371/journal.pcbi.1003285
12. Satorras, V. G., Hoogeboom, E. & Welling, M. E(n) equivariant graph neural networks. *Proceedings of the 38th International Conference on Machine Learning*, PMLR **139**, 9323–9332 (2021). https://proceedings.mlr.press/v139/satorras21a.html
13. Sigalotti, L. Di G., Klapp, J., Rendón, O., Vargas, C. A. & Peña-Polo, F. On the kernel and particle consistency in smoothed particle hydrodynamics. *Applied Numerical Mathematics* **108**, 242–255 (2016). https://doi.org/10.1016/j.apnum.2016.05.007
14. Stuart, A. M. Inverse problems: A Bayesian perspective. *Acta Numerica* **19**, 451–559 (2010). https://doi.org/10.1017/S0962492910000061
15. Um, K., Brand, R., Fei, Y. (R.), Holl, P. & Thuerey, N. Solver-in-the-loop: Learning from differentiable physics to interact with iterative PDE-solvers. *Advances in Neural Information Processing Systems* **33**, 6111–6122 (2020). https://proceedings.neurips.cc/paper/2020/hash/43e4e6a6f341e00671e123714de019a8-Abstract.html
16. Winchenbach, R. & Thuerey, N. diffSPH: Differentiable smoothed particle hydrodynamics for hybrid machine learning solutions in fluid mechanics. *Journal of Computational Physics* **555**, 114769 (2026). https://doi.org/10.1016/j.jcp.2026.114769
17. Woodward, M. *et al.* Physics-informed machine learning with smoothed particle hydrodynamics: Hierarchy of reduced Lagrangian models of turbulence. *Physical Review Fluids* **8**, 054602 (2023). https://doi.org/10.1103/PhysRevFluids.8.054602
