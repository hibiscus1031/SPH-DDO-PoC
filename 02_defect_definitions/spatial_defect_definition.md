# Spatial discretization-defect definition

## State and continuum operator

DDO-01 uses a two-dimensional periodic barotropic weakly compressible Navier–Stokes operator in material form. At one fixed time, define

\[
q=(\rho,\mathbf v),\qquad p=p(\rho),
\]

with \(\rho>0\), velocity \(\mathbf v\), constant kinematic viscosity \(\nu\ge0\), and frozen barotropic equation of state. The primary EOS candidate is

\[
p(\rho)=c_0^2(\rho-\rho_0),
\]

where any background pressure is excluded unless it is included identically in both continuum and discrete definitions. The continuum spatial RHS is

\[
\mathcal L(q)=
\begin{bmatrix}
-\rho\,\nabla\!\cdot\mathbf v\\[2mm]
-\rho^{-1}\nabla p+\nu\nabla^2\mathbf v
\end{bmatrix}.
\]

Body forces and manufactured balance sources are not part of the primary defect. If later used to realize a dynamic manufactured solution, they must be kept in a separate source channel and must cancel neither continuum nor discrete spatial terms in the target definition.

## Sampling and discrete operator

Let particles have fixed evaluation positions \(\mathbf x_i\), masses \(m_i\), support radius \(h_i\), and sampled state

\[
(R_hq^*)_i=(\rho^*(\mathbf x_i),\mathbf v^*(\mathbf x_i)).
\]

Here \(h\) denotes compact-support radius. The imported implementation calls it `support`; any alternative smoothing-length convention must record its conversion to this \(h\).

The SPH semi-discrete RHS is evaluated without advancing time:

\[
\mathcal L_h(R_hq^*)_i=
\begin{bmatrix}
-\rho_i(\nabla\!\cdot\mathbf v)_{h,i}\\[1mm]
\mathbf a^p_{h,i}+\mathbf a^\nu_{h,i}
\end{bmatrix}.
\]

For the primary raw continuity operator,

\[
(\nabla\!\cdot\mathbf v)_{h,i}
=\sum_j \frac{m_j}{\rho_j}(\mathbf v_j-\mathbf v_i)\cdot\nabla_iW_{ij}.
\]

For pressure, imported pair force \(\mathbf f^p_{ij}\) is converted to acceleration:

\[
\mathbf f^p_{ij}=-m_im_j\left(\frac{p_i}{\rho_i^2}+\frac{p_j}{\rho_j^2}\right)\nabla_iW_{ij},
\]

For every unordered pair \(i<j\), the imported accumulator adds \(\mathbf f^p_{ij}\) to particle \(i\) and \(-\mathbf f^p_{ij}\) to particle \(j\). Calling the resulting particle force \(\mathbf F^p_{h,i}\), define \(\mathbf a^p_{h,i}=\mathbf F^p_{h,i}/m_i\).

For viscosity,

\[
\mathbf f^\nu_{ij}=m_im_j\Gamma_{ij}(\mathbf v_j-\mathbf v_i),
\]

\[
\Gamma_{ij}=-\frac{4\nu}{\rho_i+\rho_j}
\frac{\mathbf r_{ij}\cdot\nabla_iW_{ij}}
{r_{ij}^2+(0.01h_{ij})^2}.
\]

The same unordered-pair accumulator defines \(\mathbf F^\nu_{h,i}\) by opposite additions, and \(\mathbf a^\nu_{h,i}=\mathbf F^\nu_{h,i}/m_i\).

The exact code path, dtype, kernel, support convention, neighbor graph, self-edge handling, and accumulation convention must be manifest-bound for every atlas case.

## Primary target and sign

The raw spatial discretization defect is

\[
\boxed{d^*_{h,i}=(R_h\mathcal L(q^*))_i-\mathcal L_h(R_hq^*)_i.}
\]

Positive correction means “add to the low-cost RHS.” A perfect correction would satisfy \(\mathcal L_h+d_h^*=R_h\mathcal L\) at the sampled fixed state.

The target has a scalar density-rate component and a vector acceleration component. They must not be concatenated without separate dimensional normalization and component labels.

## Exclusions and validity conditions

- No integrator, \(\Delta t\), next state, one-step residual, trajectory, or rollout is used.
- Analytical derivatives are evaluated before sampling; differentiating an interpolant of particle values is not equivalent.
- High-resolution SPH is not truth.
- The continuum and discrete sides use the same EOS, viscosity, domain, field, and modeled terms; otherwise the difference includes model-form mismatch and is invalid as a discretization-defect target.
- Reference quantities may appear only in target-generation records, never deployable descriptors.
- Cases with nonpositive density, unresolved discontinuities, ambiguous periodic wave vectors, or invalid support topology are rejected rather than silently clipped.

## Target record schema

Each particle target record must include `case_id`, `particle_id`, position hash (not necessarily exposed as a feature), units, \(\rho_i\), \(\mathbf v_i\), continuum component values, discrete component values, signed component defects, \(h\), \(\Delta x\), \(kh\), field family, resolution, jitter seed, dtype, and reference-evaluation method. Reference-only columns must carry the prefix `target_ref__`; online-observable columns must carry `obs__`.
