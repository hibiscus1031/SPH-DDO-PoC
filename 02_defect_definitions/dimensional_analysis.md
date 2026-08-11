# Dimensional analysis and normalization contract

## Base dimensions and case scales

Use base dimensions mass \(M\), length \(L\), and time \(T\), and let \(D\) be spatial dimension. The SPH kernel has \([W]=L^{-D}\), particle density has \([\rho]=ML^{-D}\), and barotropic pressure has \([p]=ML^{2-D}T^{-2}\). Every case records positive scales \(\rho_0\,[ML^{-D}]\), \(L_0\,[L]\), \(U_0\,[LT^{-1}]\), sound speed \(c_0\,[LT^{-1}]\), pressure scale \(P_0=\rho_0c_0^2\,[ML^{2-D}T^{-2}]\), advective time \(T_0=L_0/U_0\,[T]\), acceleration scale \(A_0=U_0^2/L_0\,[LT^{-2}]\), and density-rate scale \(\dot\rho_0=\rho_0U_0/L_0\,[ML^{-D}T^{-1}]\). The primary imported baseline is \(D=2\); its \(M\) and \(p\) are therefore the consistent two-dimensional (per-unit-thickness) quantities, not silently three-dimensional units.

For low-Mach density/pressure modes, report \(\delta\rho/\rho_0\) and \(p/P_0\). If \(U_0=0\) for a density-only probe, use declared nonzero probe amplitude \(U_{probe}\) for velocity-derived scales; never divide by a realized zero RMS.

The project uses \(h\) as compact support radius and \(\Delta x=L/N\) as nominal lattice spacing. Wave-vector magnitude \(k\,[L^{-1}]\) gives \(kh\), and \(h/\Delta x\) is dimensionless.

## Observable descriptor dictionary

All normalizations use only prescribed case parameters or low-cost state statistics; none uses targets or references.

| Layer | Descriptor | Dimension | Frozen normalization / representation |
|---|---|---:|---|
| G | relative position \(\mathbf r_{ij}\) | \(L\) | \(\mathbf r_{ij}/h_{ij}\), minimum image |
| G | distance | \(L\) | \(r_{ij}/h_{ij}\) |
| G | neighbor count | 1 | raw integer and \((n_i-n_{nom})/\max(n_{nom},1)\) |
| G | support radius | \(L\) | \(h_i/L_0\) and \(h_i/\Delta x\) |
| G | covariance \(C_i=\sum\omega\,\mathbf r\mathbf r^T/\sum\omega\) | \(L^2\) | \(C_i/h_i^2\) |
| G | covariance eigenvalues/ratios | \(L^2\), 1 | \(\lambda_a/h_i^2\); \(\lambda_{min}/(\lambda_{max}+\epsilon)\) |
| G | disorder/anisotropy | 1 | \((\lambda_{max}-\lambda_{min})/(\lambda_{max}+\lambda_{min}+\epsilon)\), coefficient of neighbor-distance variation |
| C | zeroth moment error \(S_0-1\) | 1 | unchanged |
| C | first moment \(\sum V_j(\mathbf x_j-\mathbf x_i)\otimes\nabla W\) error | 1 | subtract identity using the frozen sign convention; Frobenius/invariants |
| C | gradient of constant | \(L^{-1}\) | multiply by \(h_i\) |
| C | support completeness | 1 | observed kernel volume or count divided by periodic nominal value |
| P | density | \(ML^{-D}\) | \(\rho_i/\rho_0\), \((\rho_i-\rho_0)/\rho_0\) |
| P | pressure | \(ML^{2-D}T^{-2}\) | \(p_i/P_0\) |
| P | velocity difference | \(LT^{-1}\) | \((\mathbf v_j-\mathbf v_i)/\max(U_0,c_0\epsilon)\) |
| P | SPH divergence | \(T^{-1}\) | \(h_i(\nabla\cdot\mathbf v)_{h,i}/\max(U_0,c_0\epsilon)\) |
| P | SPH vorticity | \(T^{-1}\) | same time-scale normalization as divergence |
| P | strain-rate tensor/invariants | \(T^{-1}\) | \(h_i\mathbf S_i/\max(U_0,c_0\epsilon)\); dimensionless invariants |
| P | pressure acceleration | \(LT^{-2}\) | \(\mathbf a^p_{h,i}/A_0\), plus local frame components |
| P | viscous acceleration | \(LT^{-2}\) | \(\mathbf a^\nu_{h,i}/A_0\), plus local frame components |
| N | \(h/\Delta x\), \(kh\), Mach | 1 | unchanged; \(Ma=U_0/c_0\) |
| N | Reynolds-like number | 1 | \(Re=U_0L_0/\nu\); record `infinite` only when \(\nu=0\) and do not feed infinity to diagnostics |

Here \(\epsilon\) is a fixed machine-safe dimensionless floor recorded by dtype, not a fitted value. Tensor features are stored either as complete tensors with a declared rotation law or as invariant scalars; arbitrary global Cartesian components are not mixed with claims of rotational invariance.

## Target normalization

Raw dimensional targets are always retained. Diagnostic normalized targets are:

\[
\widehat d^{\rho,\Sigma}=d^{\rho,\Sigma}/\rho_0,\quad
\widehat d^{\dot\rho}=d^{\dot\rho}/\dot\rho_0,\quad
\widehat{\mathbf d}^{p,\nu,a}=\mathbf d^{p,\nu,a}/A_0.
\]

For frequency-conditioned plots, an additional analytical scale such as \(c_0^2A_\rho k\) for pressure or \(\nu A_vk^2\) for viscosity may be reported, but it must be labeled `reference_scale_diagnostic` and cannot normalize deployable model inputs because it may require manufactured-field knowledge.

## Coordinate and aggregation rules

- No absolute global coordinate by default.
- Pair vectors use minimum-image displacement and symmetric \(h_{ij}=(h_i+h_j)/2\).
- Neighborhood scalar aggregations are permutation invariant; vector/tensor aggregations must state their rotation covariance.
- Dataset standardization, if used for diagnostics, is fit on development groups only and never on target/reference columns.
- Dimensional scalar, vector, and tensor channels are never silently concatenated before the declared nondimensionalization.
