# Analytical/manufactured field-family specification

## Common domain and sampling

Primary DDO-01 fields live on the two-dimensional periodic torus \(\Omega=[0,L)^2\). Let \(\boldsymbol\kappa=(2\pi/L)(n_x,n_y)\), with integer mode indices, \(k=\|\boldsymbol\kappa\|\), phase \(\phi\), unit wave direction \(\mathbf e_k=\boldsymbol\kappa/k\), and transverse direction \(\mathbf e_\perp=(-e_{k,y},e_{k,x})\).

For each configuration, the same closed-form continuum field is sampled on every requested particle resolution. Analytical derivatives are evaluated from the formula, not estimated from particles. The default EOS is \(p=c_0^2(\rho-\rho_0)\). Amplitudes must satisfy \(\rho>0\) everywhere and the declared weak-compressibility/Mach envelope.

Nominal particles are cell-centered Cartesian points. Disorder is applied to particle positions only; the continuum field formula remains fixed and is resampled at the perturbed positions. Periodic wrapping and minimum-image geometry are mandatory. A case identity binds field formula, coefficients, phases, resolution, support ratio, jitter seed, dtype, and code hashes.

These are static operator probes. They need not be time-integrated solutions. No Taylor–Green configuration is used, avoiding assumptions that conflict with the selected barotropic WCSPH operator.

## F1 — single spatial mode

Use three separately labeled probes to isolate operator channels:

1. Density/pressure mode:
   \[
   \rho^*=\rho_0[1+A_\rho\sin(\boldsymbol\kappa\cdot\mathbf x+\phi)],
   \qquad \mathbf v^*=\mathbf 0.
   \]
   It isolates density interpolation and pressure-gradient defects.
2. Longitudinal velocity mode:
   \[
   \rho^*=\rho_0,\qquad
   \mathbf v^*=A_v\mathbf e_k\sin(\boldsymbol\kappa\cdot\mathbf x+\phi).
   \]
   It gives nonzero divergence and Laplacian with zero continuum vorticity.
3. Transverse velocity mode:
   \[
   \rho^*=\rho_0,\qquad
   \mathbf v^*=A_v\mathbf e_\perp\sin(\boldsymbol\kappa\cdot\mathbf x+\phi).
   \]
   It gives vorticity and Laplacian with zero continuum divergence.

The density and velocity modes may be combined only in a separately labeled `F1_coupled` case after each isolated component passes target-construction audits.

## F2 — multi-frequency modes

Define deterministic sums

\[
\rho^*=\rho_0\left[1+\sum_{m=1}^{M}A_{\rho,m}\sin(\boldsymbol\kappa_m\cdot\mathbf x+\phi_m)\right],
\]

\[
\mathbf v^*=\sum_{m=1}^{M} A_{v,m}\mathbf e_m
\sin(\boldsymbol\kappa_m\cdot\mathbf x+\psi_m),
\]

where \(\mathbf e_m\) is explicitly longitudinal or transverse to its own wave vector. Coefficients, phases, and mode tuples are fixed in the case manifest. The sum of absolute density amplitudes must be below one, and the realized velocity maximum must satisfy the Mach envelope.

F2 tests whether similar local observable states can arise from different spectral mixtures and thereby expose conditional target variance. It must include separated and moderately adjacent mode magnitudes; aliasing-prone cases with fewer than the declared particles per wavelength are rejected.

## F3 — oblique and anisotropic modes

Use integer wave-vector pairs such as \((1,1)\), \((1,2)\), \((2,1)\), and their symmetry-related orientations. Pair cases with the same \(k\) where the integer lattice permits, and include longitudinal/transverse polarization.

F3 separates orientation sensitivity from \(kh\) sensitivity. On the regular lattice, axis-aligned and oblique cases probe discrete anisotropy. Under particle disorder, rotate both wave vector and vector polarization while preserving continuum amplitudes. Rotation-equivalence diagnostics compare invariant norms and appropriately rotated vector defects; they do not assume equivalence before measurement.

## F4 — controlled particle disorder

Starting from nominal points \(\mathbf x_i^0\), define

\[
\mathbf x_i=\operatorname{wrap}\left(\mathbf x_i^0+\epsilon_j\Delta x\,\boldsymbol\xi_i\right),
\qquad \boldsymbol\xi_i\sim U([-1,1]^2),
\]

using a declared CPU generator and seed. Initial pilot jitter fractions are 0, 0.025, 0.05, and 0.10. Every generated layout is hashed. The neighborhood must pass reciprocity, uniqueness, bounds, support-interior completeness, and minimum-image audits before operator evaluation.

F4 is crossed with a small, deterministic subset of F1/F3 in DDO-01; it is not a license for a large sweep. Random seeds are replicates, not independent physical fields, and group-aware uncertainty must respect that hierarchy.

## Analytical derivatives

For each mode \(s=\sin(\boldsymbol\kappa\cdot\mathbf x+\phi)\),

\[
\nabla s=\boldsymbol\kappa\cos(\boldsymbol\kappa\cdot\mathbf x+\phi),
\qquad
\nabla^2s=-k^2s.
\]

These identities construct \(\nabla\rho\), \(\nabla p=c_0^2\nabla\rho\), velocity divergence, vorticity, strain, and vector Laplacian. A second independent implementation must cross-check a preregistered sample to dtype-scaled tolerance before atlas generation.

## Resolution and support comparability

The continuum mode indices, amplitudes, phases, domain, EOS, and physical parameters remain identical when resolution changes. Varying \(h/\Delta x\) changes only the discrete operator. Report both points per wavelength \(2\pi/(k\Delta x)\) and \(kh\). Cases are excluded if compact support is not smaller than half the periodic extent or if the wavelength-resolution rule fails.

## Pilot order

DDO-01 begins with a small audit set: one density mode, one longitudinal mode, one transverse mode, regular layouts at two resolutions and the inherited support ratio, then one oblique mode and one fixed 5% jitter realization. Only after signal/reference checks pass may the prospective axes be expanded. This sequencing prevents a large sweep from preceding target validation.
