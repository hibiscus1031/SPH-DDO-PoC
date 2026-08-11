# Final failure taxonomy

| Code | Question | Frozen disposition | Evidence boundary |
|---|---|---|---|
| F0 | Numerical/reference implementation uncertainty | Resolved/qualified | DDO-01B-R, DDO-01C-R, DDO-01D and DDO-02B mandatory audits passed. This qualifies the fixed-time analytical reference chain, not a dynamic solver. |
| F1 | Defect signal too weak | Rejected by H1 evidence | Every frozen component passed `R_c >= 10` and `L95_c > 5` over its qualified excited-case scope. |
| F2 | No systematic scaling | Component-dependent | Density rate passed regular and tested-disorder scope; momentum and total passed regular scope only; interpolation density failed regular scaling scope. |
| F3 | Insufficient feature-space coverage | Not sufficient to explain DDO-01E failure | Formal coverage was 0.953 in DDO-01E and 0.936 in DDO-02B, both above 0.90, while H3 failed. Coverage alone is not identifiability. |
| F4 | Observable conditional ambiguity | Supported | DNN-tail, conditional-variance and oracle-error failures persisted componentwise. |
| F5 | Simple consistency descriptors rescue disorder failure | Not supported | F4 C0-versus-C1 ablations showed no uniform pressure/viscosity rescue. |
| F6 | Explicit directional-frame augmentation rescues the route | Not supported as a complete route | DDO-02A justified a fresh test, but DDO-02B still failed all primary H3 gates; fallback occurred for exactly 515904/627264 particle environments. |
| F7 | Expanded deployment-compatible observables identify the defects | Fresh requalification failed | CA-06 was prospectively frozen, then tested on 384 new cases with zero DDO-01D lineage overlap. |

No entry implies that every SPH defect is fundamentally unlearnable, that temporal information cannot help, or that an untested observable/representation must fail.
