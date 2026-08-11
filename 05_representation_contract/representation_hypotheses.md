# Representation hypotheses

Representation tests ask how much of the measured particle defect can be expressed through correction interfaces. They do not assume a neural architecture or that reciprocal pair forces are sufficient.

Let the momentum target be particle accelerations \(\mathbf d_i\), particle masses \(m_i\), and mass inner product \(\|\mathbf d\|_M^2=\sum_i m_i\|\mathbf d_i\|^2\).

## R0 — unconstrained per-particle vector

Represent \(\widehat{\mathbf d}_i\in\mathbb R^2\) independently. R0 is the identity upper bound on representability and imposes no conservation property. It is not itself a deployable architecture.

## R1 — zero-center-of-mass projected correction

Project acceleration corrections as

\[
\Pi_{0}\mathbf d_i=\mathbf d_i-
\frac{\sum_jm_j\mathbf d_j}{\sum_jm_j}.
\]

Then \(\sum_i m_i\Pi_0\mathbf d_i=0\). Measure removed center-of-mass component and mass-norm residual. R1 is compatible with zero net internal force and therefore linear momentum; it does not establish pair locality, angular momentum conservation, or energy behavior.

## R2 — reciprocal antisymmetric pair-force basis

On a fixed reciprocal graph, assign one vector \(\mathbf g_e\) to each unordered edge \(e=(i,j)\). The particle force is the oriented incidence accumulation \(\mathbf F=B\mathbf g\), and acceleration is \(\widehat{\mathbf d}_i=\mathbf F_i/m_i\). Evaluate minimum-norm or ridge-stabilized least squares using fixed graph topology.

Subhypotheses:

- R2a: unrestricted antisymmetric pair vectors; guarantees zero net force on each connected component.
- R2b: central pair forces \(\mathbf g_{ij}=\alpha_{ij}\mathbf r_{ij}\); additionally compatible with pairwise angular-momentum conservation under minimum-image geometry.
- R2c: operator-aligned pressure/viscous bases using frozen kernel-gradient and velocity-difference directions; identities are formula-specific.

R2a sufficiency must not be called evidence for centrality. On a connected graph it may have high algebraic capacity, so report coefficient conditioning, null-space dimension, edge locality, and cross-case regularity in addition to residual.

## R3 — local equivariant neighborhood operator

R3 permits the correction at particle \(i\) to depend on the full bounded neighborhood while respecting particle permutation and Euclidean rotation/reflection transformation laws. DDO-00 defines only the representation class and observable inputs; it authorizes no neural implementation. Diagnostic tests use invariant/equivariant low-order bases and closed-form regression only.

## R4 — local plus regional/global representation

R4 augments R3 with deployable invariant summaries computed from the low-cost state over a fixed regional or whole-domain scope. It exists to test locality failure, not to encode analytical mode labels or absolute coordinates. Translation on the periodic domain must leave global summaries unchanged.

## Evaluation protocol

For R0–R4 report mass-norm reconstruction residual, per-component NRMSE, 90th-percentile particle error, conditioning, identity residuals, receptive-field size, and group-held-out coefficient regularity. Pressure, viscosity, total acceleration, and continuity/density targets are evaluated separately. Scalar density-rate corrections are not forced into a pair-force representation without a separately defined conservative mass-flux basis.

## Status

R0–R4 are `PROSPECTIVE_HYPOTHESES`. No representation is declared sufficient in DDO-00.
