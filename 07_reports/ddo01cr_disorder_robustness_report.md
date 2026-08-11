# DDO-01C-R disorder robustness report

Regular and 5% jitter cases are compared through 102 prospectively paired identities. No disorder failure was deleted.

| Component | Interaction class | Median jitter/regular Y | Minimum | Maximum |
|---|---|---:|---:|---:|
| Interpolation/density | `NO_SYSTEMATIC_SCALING_SUPPORTED` | 2.90804873378 | 1.17453536885 | 67.4410673651 |
| Density rate | `REGULAR_AND_DISORDER_SCALING_SUPPORTED` | 1.16277724478 | 1.00487434376 | 2.15254362857 |
| Pressure gradient | `REGULAR_ONLY_SCALING_SUPPORTED` | 7.44755819909 | 1.40604223929 | 38.222563378 |
| Viscosity/Laplacian | `REGULAR_ONLY_SCALING_SUPPORTED` | 9.87966548828 | 1.67124424035 | 49.0514164934 |
| Total acceleration | `REGULAR_ONLY_SCALING_SUPPORTED` | 9.22581363029 | 1.40604223929 | 49.0514164934 |

The paired response ratios are descriptive effect sizes. Formal robustness is determined only by the separately frozen refinement and spectral gates for the jitter layout.
