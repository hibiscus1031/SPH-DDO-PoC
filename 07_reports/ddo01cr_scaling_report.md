# DDO-01C-R controlled spatial-defect scaling report

## Project result

`DDO01CR_COMPONENTWISE_SCALING_PARTIALLY_QUALIFIED`

All 204 fresh registered cases passed every mandatory CA-01 numerical/reference audit, and every formal log response was admissible. The project result is componentwise rather than global.

| Component | Regular scope | Jitter scope | Component result |
|---|---|---|---|
| Interpolation/density | `FAIL` | `FAIL` | `H2_SCALING_FAIL_REGULAR_SCOPE` |
| Density rate | `PASS` | `PASS` | `H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT` |
| Pressure gradient | `PASS` | `FAIL` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` |
| Viscosity/Laplacian | `PASS` | `FAIL` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` |
| Total acceleration | `PASS` | `FAIL` | `H2_SCALING_PASS_REGULAR_SCOPE_ONLY` |

Every PASS is restricted to the sampled F1 domain and canonical formal support ratio `h/dx=4`. It supports systematic scaling only; it does not establish H3-H6, learnability, architecture suitability, or corrected-solver convergence.

## Formal gate evidence

| Component | Family | Layout | M_family | M-0.75 | min(C-D) | Descriptive track median slopes | Verdict |
|---|---|---|---:|---:|---:|---|---|
| Interpolation/density | REFINEMENT_H | jitter_0.05 | 0.583333333333 | -0.166666666667 | -0.0216698731997 | `{"D005": 0.08000086116211289, "D010": 0.066288423078427}` | `FAIL` |
| Interpolation/density | REFINEMENT_H | regular | 0 | -0.75 | -1.6546763959e-11 | `{"D005": -1.1401009318032826e-14, "D010": -5.476293779286116e-15}` | `FAIL` |
| Interpolation/density | SPECTRAL_KH | jitter_0.05 | 0.333333333333 | -0.416666666667 | -0.0218326698749 | `{"D005": 0.0023689288384365946, "D010": -0.0082584154751675}` | `FAIL` |
| Interpolation/density | SPECTRAL_KH | regular | 0 | -0.75 | -1.64241953371e-11 | `{"D005": -9.091469101884793e-16, "D010": 1.3637203652827186e-15}` | `FAIL` |
| Density rate | REFINEMENT_H | jitter_0.05 | 1 | 0.25 | 0.40297262969 | `{"V050": 1.3425865725041146, "V100": 1.3423665870164627}` | `PASS` |
| Density rate | REFINEMENT_H | regular | 1 | 0.25 | 0.627116190969 | `{"V050": 1.8174727004945446, "V100": 1.8174727004945446}` | `PASS` |
| Density rate | SPECTRAL_KH | jitter_0.05 | 1 | 0.25 | 1.15004563429 | `{"V050": 2.2086017865475727, "V100": 2.2212262119977386}` | `PASS` |
| Density rate | SPECTRAL_KH | regular | 1 | 0.25 | 1.51856074713 | `{"V050": 2.7869359486378116, "V100": 2.7869359486378116}` | `PASS` |
| Pressure gradient | REFINEMENT_H | jitter_0.05 | 0 | -0.75 | 0.208521400963 | `{"D005": -0.8872184961686187, "D010": -0.8822613339059105}` | `FAIL` |
| Pressure gradient | REFINEMENT_H | regular | 1 | 0.25 | 0.332862201996 | `{"D005": 1.4923635774602309, "D010": 1.0141487718971267}` | `PASS` |
| Pressure gradient | SPECTRAL_KH | jitter_0.05 | 0.75 | 0 | 0.0253954259315 | `{"D005": 0.07804944174714382, "D010": 0.10051000205121591}` | `PASS` |
| Pressure gradient | SPECTRAL_KH | regular | 1 | 0.25 | 1.01194260547 | `{"D005": 2.3914395359118217, "D010": 1.9610007212725562}` | `PASS` |
| Viscosity/Laplacian | REFINEMENT_H | jitter_0.05 | 0 | -0.75 | 0.195875520677 | `{"V050": -0.8491722478216315, "V100": -0.8777783272311837}` | `FAIL` |
| Viscosity/Laplacian | REFINEMENT_H | regular | 1 | 0.25 | 0.532168457401 | `{"V050": 1.5546800794135602, "V100": 1.5546800794135602}` | `PASS` |
| Viscosity/Laplacian | SPECTRAL_KH | jitter_0.05 | 1 | 0.25 | 0.543182221591 | `{"V050": 1.0441587314124758, "V100": 1.0457474284229527}` | `PASS` |
| Viscosity/Laplacian | SPECTRAL_KH | regular | 1 | 0.25 | 1.89784995954 | `{"V050": 3.5044707795337553, "V100": 3.504470779533755}` | `PASS` |
| Total acceleration | REFINEMENT_H | jitter_0.05 | 0 | -0.75 | 0.195875520677 | `{"D005": -0.8872184961686187, "D010": -0.8822613339059105, "V050": -0.8491722478216315, "V100": -0.8777783272311837}` | `FAIL` |
| Total acceleration | REFINEMENT_H | regular | 1 | 0.25 | 0.332862201996 | `{"D005": 1.4923635774602309, "D010": 1.0141487718971267, "V050": 1.5546800794135602, "V100": 1.5546800794135602}` | `PASS` |
| Total acceleration | SPECTRAL_KH | jitter_0.05 | 0.875 | 0.125 | 0.0253954259315 | `{"D005": 0.07804944174714382, "D010": 0.10051000205121591, "V050": 1.0441587314124758, "V100": 1.0457474284229527}` | `PASS` |
| Total acceleration | SPECTRAL_KH | regular | 1 | 0.25 | 1.01194260547 | `{"D005": 2.3914395359118217, "D010": 1.9610007212725562, "V050": 3.5044707795337553, "V100": 3.504470779533755}` | `PASS` |

`M_family` uses equal scientific-track weighting. The formal monotonicity margin is `M_family-0.75`; the dispersion margin is `C_t-D_t`, reported conservatively as the minimum over mandatory tracks. A positive value supports the respective gate. Descriptive median local slopes are not fitted convergence orders and do not replace either gate.

## Numerical validity

- mandatory cases passed: `204/204`;
- maximum derivative discrepancy: `1.42108547152e-14`;
- maximum derivative gate fraction: `0.0140035578584`;
- `U_num` range: `2.84217094304e-16` to `1.77961952559e-12`;
- maximum component-closure residual: `0`.

The independently rebuilt float32 graph was unavailable for 14 diagnostic cases because support-boundary rounding broke reciprocity. Those cases used the valid primary edge set cast to float32 solely for the explicitly non-gating precision-degradation diagnostic. Primary float64 topology, CA-01 `U_num`, formal targets, and H2 decisions were unchanged.

## Claim boundary

H2 FAIL for interpolation/density rejects systematic scaling under these formal families and sampled scope; it does not imply H3 FAIL. Regular-only acceleration-channel results retain the disorder limitation. No case, interval, or disorder failure was removed.
