# Prospective DDO gates

These thresholds are frozen before DDO-01 target inspection. They are decision aids over the declared atlas, not universal theorems. Every gate is currently `NOT_EVALUATED_DDO00`; no hypothesis passes in DDO-00.

## H1 — signal resolvability

For each primary component, require target RMS to exceed the conservative uncertainty upper bound by at least 10×, with the group-bootstrap 95% lower bound above 5×. Require continuum derivative cross-check, float64 repeatability, target decomposition closure, and neighborhood audit to pass. Components failing H1 cannot be used to judge H3–H6.

## H2 — systematic scaling

Require at least three admissible \(h\) or \(kh\) levels on each of at least two independent field tracks. A candidate scaling result requires finite local log-slopes with the same expected sign on at least 75% of adjacent intervals and a between-replicate dispersion smaller than the median level-to-level change. Report plateaus/nonmonotonicity; do not force a convergence order. H2 can pass componentwise only.

## H3 — observable identifiability

For a declared descriptor set and receptive field, all of the following are required on group-held-out cases:

- nearest-neighbor disagreement ratio median \(D_{NN}\le0.25\) and 90th percentile \(\le0.60\);
- conditional variance ratio \(C_{var}\le0.25\), with upper 95% bound \(\le0.35\);
- at least one allowed simple oracle with NRMSE \(\le0.50\) and at least 20% relative RMSE improvement over the mean-target baseline;
- no required field family has NRMSE above 0.75;
- feature-space coverage of at least 90% under a preregistered development-radius threshold.

Passing supports “identifiable on the DDO-01 atlas under this descriptor set,” not universal identifiability or neural-model suitability.

## H4 — locality

Apply `locality_ladder.md`. A bounded rung passes only if it also passes H3 and is within 5% relative NRMSE and 0.05 absolute \(C_{var}\) of all larger rungs by paired group bootstrap. If a regional/global rung improves NRMSE by more than 10% with nonoverlapping paired uncertainty, the smaller bounded rung fails. Select the smallest passing rung; otherwise mark locality unresolved/nonlocal on the atlas.

## H5 — structure-compatible representability

For each representation R0–R4, reconstruct the raw defect by a non-neural least-squares/projection diagnostic on fixed neighborhoods. Report relative residual \(E_R=\|d-\Pi_Rd\|_M/\|d\|_M\). A representation is useful if median \(E_R\le0.25\), 90th percentile \(\le0.50\), and its enforced identities hold to dtype-scaled tolerance. R1/R2 may support linear-momentum compatibility only; angular momentum and energy need separate gates. A structured component may pass even if the full defect does not.

## H6 — held-out transfer

Using only an H3-passing descriptor/rung and allowed simple oracle, hold out complete resolution and frequency groups. Require interpolation NRMSE \(\le0.60\), extrapolation NRMSE \(\le0.75\), and no more than 25% relative degradation from in-range group-held-out NRMSE. At least one resolution and one frequency must be unseen during fitting. These thresholds diagnose conditioned transfer; they do not authorize a learned production operator.

## Stop and route rules

- H1 fail: improve reference/precision or redefine the measurable component prospectively; do not train.
- H1 pass but H3 fail: expand only online descriptors or receptive fields prospectively; do not select a neural architecture.
- H3 pass but H4 fail: study regional/global dependence before architecture choice.
- H5 fail: retain unconstrained correction as a diagnostic; do not impose pair-force claims.
- H6 fail: restrict the claim domain and redesign sampling; do not make transfer claims.

Only a separately authorized post-DDO-01 decision may open architecture selection.
