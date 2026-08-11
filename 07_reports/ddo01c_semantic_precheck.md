# DDO-01C H2 semantic executability precheck

## Terminal decision

`DDO01C_H2_UNRESOLVED_CONTRACT_GAP`

DDO-01C stopped at the contract-binding precheck. No DDO-01C case registry was
created, no fresh target or numerical outcome was evaluated, and no H2 scaling
statistic was computed. This is the mandatory outcome because the frozen H2
record does not uniquely define all decisions needed to construct and classify
the requested controlled scaling study.

## Hash-bound inputs

All required inputs were loaded and independently SHA-256 hashed before this
decision. The observed hashes match their upstream frozen bindings.

| Evidence | Path | SHA-256 |
|---|---|---|
| DDO-00 manifest | `06_manifests/ddo00_manifest.json` | `f298c23395047058212914339a0db6c5e5985f180d2c4011c1eeab9ba2b4663f` |
| DDO-00 prospective H2 gate | `04_identifiability_contract/prospective_gates.md` | `cb83636e0595d89b9f87bbb79b55b1042634ab528e499db82784271057e3ca17` |
| Prospective parameter axes | `03_field_design/prospective_parameter_axes.json` | `d680b1a89d1b5df4c58cff6b2faba2926e0f2f9a615ca9ffede593fa917faf27` |
| Dimensional-analysis contract | `02_defect_definitions/dimensional_analysis.md` | `b733fb6bcac458b795a3d30bd3b09ec3fc8cb35bf5e69ac19409e12cf9c10088` |
| CA-01 numerical contract | `00_project_contract/amendments/ca01_numerical_qualification_contract.md` | `8029eee814efac3cf8dc82de7e60495ee33352890ca60a0944de50991b3c2a70` |
| CA-01 manifest | `06_manifests/ca01_manifest.json` | `3e0c0ae43034feed692bd4a371c7698c33c036f27c8bab0747a89ebcd472fb08` |
| CA-01 final report | `07_reports/ca01_final_report.md` | `28adb2da5f924eed7937b37e8f3bde3353d2215ad52e3446ceb0ef04735921e8` |
| CA-02 H1 semantics contract | `00_project_contract/amendments/ca02_h1_signal_semantics_contract.md` | `284fe579ff8445a9a3efdbd1bcc36060f15071cfd131ec18719e698640f11756` |
| CA-02 manifest | `06_manifests/ca02_manifest.json` | `2cab9c8b435d138eee2d964b81914596effb87044c8cc272c07983d0e8626a8a` |
| CA-02 final report | `07_reports/ca02_final_report.md` | `f708ec047c05b59a3fb83f95627535f1697ac6104903f96ae2d04457a4f6f5a6` |
| DDO-01B-R registry | `06_manifests/ddo01br_case_registry.json` | `ee654fffdaf966bbaa01974fd09755c5c6c65af62bc77e8240d40ede4547dd8f` |
| DDO-01B-R excitation mask | `06_manifests/ddo01br_excitation_mask.json` | `d7a71824ac55525d90e8c469fd0236424fdaae5f074310f606a3113e497d3d8b` |
| DDO-01B-R manifest | `06_manifests/ddo01br_manifest.json` | `9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875` |
| DDO-01B-R signal report | `07_reports/ddo01br_signal_report.md` | `8ded1bd2e2d11c6b895d88c253bd5610036d5088cef11d07fd491d453e386cc8` |
| DDO-01B-R component ledger | `07_reports/ddo01br_component_h1_ledger.csv` | `d6c7fe5885bd878409350b6acdde71f106a43e171775b745d8e6a15fe81199b1` |
| DDO-01B-R uncertainty report | `07_reports/ddo01br_uncertainty_report.md` | `9eb57ba1a67e527cdc77afa2b4410ff23037abc177fe5d29dc9a2c2962ef754c` |
| DDO-01B-R firewall audit | `07_reports/ddo01br_firewall_audit.md` | `ef50ad0b86d8cc45be1e3f280f8118991590b414d4751b64e46ec3c8a8286118` |
| DDO-01B-R next-stage decision | `07_reports/ddo01br_next_stage_decision.md` | `dbd9ebf42e238a4087bb789b14e2c098567586d76d467e92e14c1d7cea6556bb` |

DDO-01B-R is used only to establish that the five named components are
H1-eligible and that DDO-01C was recommended subject to separate authorization.
Its 24 cases are not adopted as the formal H2 qualification set.

## What is frozen and usable

The frozen record does establish:

- the five eligible components: interpolation/density, density rate, pressure
  gradient acceleration, viscosity/Laplacian acceleration, and total
  acceleration;
- the fixed-time positive-additive defect, continuum minus SPH, without
  `dt`, time integration, or high-resolution SPH truth;
- scalar and vector case-RMS definitions from CA-02, where applicable;
- raw target retention and component dimensional normalizations from
  `dimensional_analysis.md`;
- the CA-01 per-case numerical/reference validity and additive `U_num` rules;
- prospective atlas coordinate pools for resolution, `h/dx`, mode, phase,
  amplitude, polarization, jitter, seed, and dtype;
- a minimum of three admissible `h` or `kh` levels on each of at least two
  independent field tracks; and
- the qualitative H2 requirements of finite local log-slopes, the same
  expected sign on at least 75% of adjacent intervals, and between-replicate
  dispersion below the median level-to-level change.

These statements constrain an H2 design, but do not uniquely instantiate one.

## Mandatory semantic gaps

| Required H2 decision | Precheck | Blocking gap |
|---|---|---|
| Eligible components | Complete | Five components are H1-qualified by DDO-01B-R. |
| Scaling metric | Incomplete | The contract names local log-slopes and monotonicity, but does not select raw versus normalized target, `h` versus `kh` for each formal family, or a unique family-level statistic. |
| Target norm | Partially complete | CA-02 defines case RMS, but the H2 response used for replicate aggregation and component classification is not frozen. |
| Pairing across levels | Incomplete | “Same continuum field across resolutions” is required, but canonical field-track membership, phase pairing, disorder-realization pairing, and a pairing identifier are not specified. |
| Slope estimator | Incomplete | No exact formula, admissible-interval rule, zero/nonpositive handling, regression-versus-adjacent convention, or replicate aggregation is frozen. |
| Weighting | Incomplete | No weighting across particles beyond case RMS, replicates, adjacent intervals, field tracks, or controlled families is frozen for H2. CA-02 H1 equal-case weighting cannot be silently transferred to H2. |
| Minimum levels | Threshold found, design incomplete | Three levels and two tracks are required, but “admissible level” and “independent field track” are not operationally defined, and no complete H2 slice is selected. |
| Monotonicity statistic | Incomplete | The 75% sign threshold is present, but the expected sign by coordinate, denominator, tie/plateau rule, uncertainty-overlap rule, and aggregation across tracks are absent. |
| Uncertainty treatment | Incomplete | CA-01 supplies per-case `U_num`; propagation to target ratios, differences, slopes, sign decisions, dispersion, and final H2 margins is not defined. |
| Bootstrap/resampling | Incomplete if used | CA-02 freezes H1 bootstrap semantics only. No H2 resampling requirement, unit, strata, replicate count, seed mapping, interval, or quantile is frozen. |
| Gate thresholds | Partially complete | Level/track, 75% sign, and dispersion comparisons are stated, but the quantities on both sides of the dispersion comparison are not uniquely defined. |
| PASS/FAIL/UNRESOLVED mapping | Incomplete | Componentwise PASS is allowed, but family-to-component aggregation and the treatment of invalid cases, insufficient levels, mixed tracks, support-ratio dependence, plateaus, and uncertainty are not frozen. |

## Registry-design gap

The parameter-axis file explicitly says a full Cartesian product is not
required and calls for balanced slices with preregistered holdouts, but it does
not identify the complete DDO-01C slice. It also does not provide the requested
DDO-01C SHA-256 mappings for phase offsets, jitter seeds, or pairing IDs.
Consequently, multiple non-equivalent registries satisfy the axis ranges.
Selecting one now without a prospective amendment would invent the scientific
design at the same time as execution.

## Stop boundary

The ambiguity can change both calculated gate margins and final
classifications. Therefore the following artifacts were intentionally not
created or inspected:

- `06_manifests/ddo01c_case_registry.json`;
- `data/scaling_f1/` and any DDO-01C targets or evidence;
- every DDO-01C scaling exponent, monotonicity result, uncertainty interval,
  relative-effect value, and collapse diagnostic; and
- `figures/ddo01c/`.

No H3-H6 analysis, model, optimizer, time integration, rollout,
solver-in-the-loop calculation, high-resolution SPH truth, LCDF_03, or
LCDF_10 was used.
