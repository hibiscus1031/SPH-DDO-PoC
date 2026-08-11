# Conservation claim boundary

## Linear momentum

For acceleration correction \(\delta\mathbf a_i\), zero net internal force requires

\[
\sum_i m_i\delta\mathbf a_i=\mathbf0.
\]

R1 enforces this globally by projection. R2 enforces it per connected component when reciprocal pair forces are accumulated with opposite signs. Either condition supports only **linear-momentum compatibility of the correction interface**, assuming masses are fixed during the static evaluation.

## Angular momentum

Angular momentum additionally requires vanishing internal torque,

\[
\sum_i \mathbf x_i\times m_i\delta\mathbf a_i=0,
\]

with an explicitly valid periodic-domain lever-arm convention. Zero net force alone does not imply this. Reciprocal pair forces conserve angular momentum only when each pair force is central (parallel to its minimum-image separation) or a separate torque cancellation proof applies.

The inherited pressure force is central under its periodic minimum-image geometry. The inherited componentwise viscosity force is generally not central and historically carried an explicit no-angular-momentum-guarantee boundary. A combined correction cannot inherit the pressure proof for its viscous or learned parts.

## Energy

Neither zero net force nor pair antisymmetry guarantees kinetic-energy conservation or dissipation. Energy behavior depends on correction power

\[
P_\delta=\sum_i m_i\mathbf v_i\cdot\delta\mathbf a_i.
\]

A dissipative claim requires \(P_\delta\le0\) under a defined state class and numerical tolerance; a conservative claim requires the appropriate discrete total-energy exchange identity, including internal energy for compressible flow. The inherited viscosity formula has a nonpositive pair-power identity within its formula, but that property does not automatically transfer to a defect correction or fitted representation.

## Mass and density

A scalar density-rate correction requires a separately defined conservative mass-flux interface to claim mass conservation. A per-particle scalar correction, even if mean-centered, is not automatically a conservative continuity discretization when particle masses, volumes, or boundaries vary.

## Claim vocabulary

Allowed without further proof: `zero-net-force projected`, `reciprocal antisymmetric`, `linear-momentum compatible`, `central pair basis`, and `measured nonpositive correction power on the stated atlas`.

Prohibited without separate evidence: `conserves angular momentum`, `conserves energy`, `thermodynamically consistent`, `stable in rollout`, `conservative SPH correction`, or `physically exact`.

All future conservation reports must state whether the result is algebraic by construction, numerically measured, or empirically observed on a finite atlas.
