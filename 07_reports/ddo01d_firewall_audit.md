# DDO-01D field-by-field reference-firewall audit

## Verdict

`REFERENCE_IN_MODEL_INPUT=false` — firewall pass.

The 512 observable archives and 512 reference archives occupy disjoint physical
paths, have separately frozen schemas and hashes, and share only canonical case
identity plus local particle join identity. Reference fields did not enter case
selection, role assignment, descriptor construction, neighborhood construction,
or normalization. No dataset-fitted normalization statistics exist.

## Observable-side fields

| Field | Classification | Firewall |
|---|---|---|
| `edge_col` | join/index only | pass |
| `edge_row` | join/index only | pass |
| `obs__anisotropy` | deployable observable | pass |
| `obs__covariance_eigenvalue_ratio` | deployable observable | pass |
| `obs__covariance_eigenvalues_over_h2` | deployable observable | pass |
| `obs__covariance_over_h2` | deployable observable | pass |
| `obs__delta_rho_over_rho0` | deployable observable | pass |
| `obs__distance_over_h` | deployable observable | pass |
| `obs__eps64` | deployable observable | pass |
| `obs__first_moment_error` | deployable observable | pass |
| `obs__first_moment_error_frobenius` | deployable observable | pass |
| `obs__gradient_constant_times_h` | deployable observable | pass |
| `obs__gradient_constant_times_h_norm` | deployable observable | pass |
| `obs__jitter_fraction` | deployable observable | pass |
| `obs__kernel_volume` | deployable observable | pass |
| `obs__kh_max` | deployable observable | pass |
| `obs__kh_rms` | deployable observable | pass |
| `obs__mach` | deployable observable | pass |
| `obs__mode_count` | deployable observable | pass |
| `obs__neighbor_count` | deployable observable | pass |
| `obs__neighbor_count_normalized` | deployable observable | pass |
| `obs__neighbor_distance_cv` | deployable observable | pass |
| `obs__pressure_acceleration_over_A0` | deployable observable | pass |
| `obs__pressure_over_P0` | deployable observable | pass |
| `obs__relative_position_over_h` | deployable observable | pass |
| `obs__reynolds` | deployable observable | pass |
| `obs__rho_over_rho0` | deployable observable | pass |
| `obs__sph_divergence_normalized` | deployable observable | pass |
| `obs__sph_vorticity_normalized` | deployable observable | pass |
| `obs__strain_determinant_normalized` | deployable observable | pass |
| `obs__strain_frobenius_normalized` | deployable observable | pass |
| `obs__strain_trace_normalized` | deployable observable | pass |
| `obs__support_count_completeness` | deployable observable | pass |
| `obs__support_h_over_L0` | deployable observable | pass |
| `obs__support_over_dx` | deployable observable | pass |
| `obs__total_acceleration_over_A0` | deployable observable | pass |
| `obs__velocity_difference_over_U0` | deployable observable | pass |
| `obs__viscosity_acceleration_over_A0` | deployable observable | pass |
| `obs__zeroth_moment_error` | deployable observable | pass |
| `particle_id` | join/index only | pass |

`particle_id`, `edge_row`, and `edge_col` are identifiers/connectivity, not
deployable descriptors. Every deployable field has the `obs__` namespace.

## Reference-target-side fields

| Field | Classification | Model input |
|---|---|---|
| `particle_id` | join/index only | excluded |
| `target_ref__continuum_density` | reference/target only | excluded |
| `target_ref__continuum_density_rate` | reference/target only | excluded |
| `target_ref__continuum_pressure_acceleration` | reference/target only | excluded |
| `target_ref__continuum_total_acceleration` | reference/target only | excluded |
| `target_ref__continuum_viscosity_acceleration` | reference/target only | excluded |
| `target_ref__defect_density_rate` | reference/target only | excluded |
| `target_ref__defect_interpolation_density` | reference/target only | excluded |
| `target_ref__defect_pressure_acceleration` | reference/target only | excluded |
| `target_ref__defect_total_acceleration` | reference/target only | excluded |
| `target_ref__defect_viscosity_acceleration` | reference/target only | excluded |
| `target_ref__normalized_defect_density_rate` | reference/target only | excluded |
| `target_ref__normalized_defect_interpolation_density` | reference/target only | excluded |
| `target_ref__normalized_defect_pressure_acceleration` | reference/target only | excluded |
| `target_ref__normalized_defect_total_acceleration` | reference/target only | excluded |
| `target_ref__normalized_defect_viscosity_acceleration` | reference/target only | excluded |
| `target_ref__sph_density_rate` | reference/target only | excluded |
| `target_ref__sph_interpolation_density` | reference/target only | excluded |
| `target_ref__sph_pressure_acceleration` | reference/target only | excluded |
| `target_ref__sph_total_acceleration` | reference/target only | excluded |
| `target_ref__sph_viscosity_acceleration` | reference/target only | excluded |

Every non-identifier reference field has the `target_ref__` namespace. The
reference index explicitly sets `eligible_as_model_input=false`; the observable
index sets `reference_in_model_input=false`. All 1024 per-case archive hashes
were recomputed and matched their indexes and metadata. The two indexes provide
transitive binding from the final DDO-01D manifest to every case archive.
