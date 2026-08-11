# DDO-01C-R relative defect effect-size report

All values use `E_rel=T_jc/max(C_jc,U_round(j,c))` and are `DESCRIPTIVE_NOT_H2_GATE`. No threshold is introduced.

| Component | Layout | Minimum | Median | Maximum |
|---|---|---:|---:|---:|
| Interpolation/density | regular | 8.83203509945e-05 | 0.00355987219324 | 0.0463766887267 |
| Interpolation/density | jitter_0.05 | 0.00575324535622 | 0.00979338700635 | 0.0546669772007 |
| Density rate | regular | 0 | 0.00269512546648 | 0.139566072072 |
| Density rate | jitter_0.05 | 0 | 0.0047475098897 | 0.144607936106 |
| Pressure gradient | regular | 0 | 0.00453267113709 | 0.139918977665 |
| Pressure gradient | jitter_0.05 | 0 | 0.0456284777505 | 2.48881964991 |
| Viscosity/Laplacian | regular | 0 | 0.0020435706409 | 0.139192522276 |
| Viscosity/Laplacian | jitter_0.05 | 0 | 0.0284703223963 | 1.76254259398 |
| Total acceleration | regular | 0.00408714128179 | 0.0176388288134 | 0.139918977665 |
| Total acceleration | jitter_0.05 | 0.0569406447927 | 0.128871549775 | 2.48881964991 |

Large values mean the defect is large relative to the matching continuum quantity or CA-01 roundoff floor. They do not change any H2 verdict.
