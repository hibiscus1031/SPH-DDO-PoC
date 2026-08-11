# DDO-01C-R support-ratio report

Every result is `DESCRIPTIVE_SCOPE_DIAGNOSTIC`. No expected sign or H2 threshold applies.

| Component | Track/layout | Median local slope | Minimum local slope | Maximum local slope |
|---|---|---:|---:|---:|
| Density rate | V100|jitter_0.05 | -1.57060853712 | -5.15644119265 | -0.806466751121 |
| Density rate | V100|regular | -2.70089105003 | -6.1089060456 | 0.951386785932 |
| Interpolation/density | D010|jitter_0.05 | -1.43043448209 | -2.84148556971 | -1.0058160184 |
| Interpolation/density | D010|regular | -0.278090034528 | -4.43708564427 | -0.00738316141496 |
| Pressure gradient | D010|jitter_0.05 | -3.10560796955 | -3.23275788889 | -2.9853891608 |
| Pressure gradient | D010|regular | -0.628388888453 | -4.97323545715 | 0.0925491405882 |
| Total acceleration | D010|jitter_0.05 | -3.10560796955 | -3.23275788889 | -2.9853891608 |
| Total acceleration | D010|regular | -0.628388888453 | -4.97323545715 | 0.0925491405882 |
| Total acceleration | V100|jitter_0.05 | -3.07270130318 | -3.20821910031 | -3.02996722161 |
| Total acceleration | V100|regular | -3.50030411573 | -6.21764354558 | 0.202344248238 |
| Viscosity/Laplacian | V100|jitter_0.05 | -3.07270130318 | -3.20821910031 | -3.02996722161 |
| Viscosity/Laplacian | V100|regular | -3.50030411573 | -6.21764354558 | 0.202344248238 |

Support-ratio changes also change neighbor count; this diagnostic is not interpreted as an independent neighbor-count effect and cannot alter the canonical `h/dx=4` verdict.
