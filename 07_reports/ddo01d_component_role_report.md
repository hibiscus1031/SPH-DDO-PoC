# DDO-01D component-role report

| Component | DDO-01D role | Historical H1 | Historical H2 scope | Units |
|---|---|---|---|---|
| `density_rate` | `PRIMARY_DYNAMIC_TARGET` | `H1_SIGNAL_PASS` | `H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT` | `M L^-2 T^-1` |
| `pressure_gradient_acceleration` | `PRIMARY_DYNAMIC_TARGET` | `H1_SIGNAL_PASS` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` | `L T^-2` |
| `viscosity_laplacian_acceleration` | `PRIMARY_DYNAMIC_TARGET` | `H1_SIGNAL_PASS` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` | `L T^-2` |
| `total_acceleration` | `DERIVED_CLOSURE_DIAGNOSTIC` | `H1_SIGNAL_PASS` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` | `L T^-2` |
| `interpolation_density` | `ALGEBRAIC_DENSITY_DIAGNOSTIC` | `H1_SIGNAL_PASS` | `H2_SCALING_FAIL_REGULAR_SCOPE` | `M L^-2` |

The three dynamic targets remain density rate, pressure-gradient acceleration,
and viscosity/Laplacian acceleration. Total acceleration remains a derived
closure diagnostic, not an independent mechanism. Interpolation density remains
an algebraic density diagnostic and is not combined with the dynamic RHS.

The independently reopened reference archives give a maximum particlewise
closure residual of `0`
for `d_total = d_pressure + d_viscosity`. Raw defects use the positive additive
sign convention `continuum = SPH + defect`; the maximum independently recomputed
sign residuals are recorded in `data/atlas/ddo01d_release_audit.json`.

H2 evidence shapes the retained scope only. The interpolation failure, the
regular-only momentum scope, disorder cases, and support-ratio dependence remain
present and are not used to remove cases or define an empirical power target.
