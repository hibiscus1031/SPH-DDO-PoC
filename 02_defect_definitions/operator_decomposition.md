# Operator and defect decomposition

## Rule

Every component is defined as continuum value sampled at the same particles minus the explicitly paired SPH counterpart. Components are retained separately even when a total RHS target is assembled.

## A. Interpolation and density-related defects

For any manufactured scalar \(f^*\), raw SPH interpolation is

\[
I_hf_i=\sum_j V_j f_jW_{ij},\qquad V_j=m_j/\rho_j,
\]

and its diagnostic interpolation defect is

\[
d^{I,f}_{h,i}=f^*(\mathbf x_i)-I_h(R_hf^*)_i.
\]

For density summation,

\[
\rho^{\Sigma}_{h,i}=\sum_jm_jW_{ij},\qquad
d^{\rho,\Sigma}_{h,i}=\rho^*(\mathbf x_i)-\rho^{\Sigma}_{h,i}.
\]

This is a state-reconstruction defect with units of density, not a spatial RHS component. It must not be added to acceleration or density rate.

The density-rate/continuity defect is

\[
d^{\dot\rho}_{h,i}=
-\rho_i(\nabla\!\cdot\mathbf v^*)_i
-\left[-\rho_i(\nabla\!\cdot\mathbf v)_{h,i}\right].
\]

Interpolation, density summation, and density rate are three distinct targets.

## B. Pressure-gradient operator defect

The continuum pressure acceleration and the SPH pressure acceleration are

\[
\mathbf a^{p,*}_i=-\rho_i^{-1}\nabla p^*(\mathbf x_i),
\qquad
\mathbf a^p_{h,i}=m_i^{-1}\mathbf F^p_{h,i}.
\]

The pressure defect is

\[
\boxed{\mathbf d^p_{h,i}=\mathbf a^{p,*}_i-\mathbf a^p_{h,i}.}
\]

Pressure is computed from the same frozen EOS on both sides. A mismatch between incompressible pressure and barotropic WCSPH pressure is model-form mismatch and is prohibited in this target.

## C. Viscous/Laplacian operator defect

For constant kinematic viscosity,

\[
\mathbf a^{\nu,*}_i=\nu\nabla^2\mathbf v^*(\mathbf x_i),
\qquad
\mathbf a^\nu_{h,i}=m_i^{-1}\mathbf F^\nu_{h,i},
\]

and

\[
\boxed{\mathbf d^\nu_{h,i}=\mathbf a^{\nu,*}_i-\mathbf a^\nu_{h,i}.}
\]

If variable viscosity is introduced later, the continuum operator and pair formula require a new contract; the constant-\(\nu\) formula cannot be relabeled as a variable-viscosity defect.

## D. Total spatial RHS defect

For \(q=(\rho,\mathbf v)\),

\[
d^{*,\mathrm{RHS}}_{h,i}=
\begin{bmatrix}
d^{\dot\rho}_{h,i}\\
\mathbf d^p_{h,i}+\mathbf d^\nu_{h,i}
\end{bmatrix}.
\]

The momentum/acceleration component is also reported separately as

\[
\mathbf d^a_{h,i}=\mathbf d^p_{h,i}+\mathbf d^\nu_{h,i}.
\]

The equality above is an audit identity. Per-case tolerances must be based on dtype and accumulation uncertainty; failure means the total/component construction is inconsistent.

## Diagnostic consistency channels

Zeroth moment error, first moment tensor error, gradient-of-constant residual, support completeness, raw scalar gradient defect, and raw Laplacian defect are explanatory diagnostics. They are not substituted for \(d_h^*\) and are not assumed sufficient descriptors.

## Model-form firewall

The following differences are never labeled discretization defect: different EOS, physical viscosity, boundary condition, forcing, dimensionality, continuum PDE, kernel family, or intentionally changed modeled term across the two sides. Such comparisons require a separately named model-form study.
