# CA-03 prospective H2 semantics and design qualification

## Decision

Assign:

`DDO_CA03_H2_SCALING_SEMANTICS_AND_DESIGN_FROZEN`

CA-03 uniquely defines the formal H2 response, log admissibility, local slopes,
uncertainty bounds, track hierarchy, equal-track monotonicity, between-replicate
dispersion, formal and component verdicts, exact numeric registry slices, and
deterministic replicate mappings. The stopped DDO-01C state remains permanent.

## Design qualification

The inherited dimensional record uniquely supplies all five `S_c` values.
The authorized pools supply five refinement levels, three positive-x spectral
levels, four support ratios, three distinct phases, and three distinct jitter
seeds. Every selected point passes the prospective points-per-wavelength and
compact-support design filters.

The exact design has four field-track templates, separate regular and 5%
jitter layouts, and three matched replicates. It materializes 204 unique fresh
cases when the 34 unique numerical/field configurations are crossed with layout
and replicate. Formal component membership has at least two independent tracks.

## Synthetic executability qualification

Command:

`python3 08_scripts/test_h2_scaling_semantics.py`

All 14 synthetic-only tests passed. They cover clean refinement and spectral
PASS, the exact 75% boundary, below-threshold failure, uncertainty-overlap
plateau, opposite sign, dispersion failure, insufficient levels/tracks,
nonpositive lower response, equal-track weighting, regular/jitter mapping,
support-ratio noninterference, and deterministic hash mapping.

No historical or real SPH target magnitude appears in the tests.

## Authorization

CA-03 authorizes only creation and independent SHA-256 freeze of the exact
DDO-01C-R registry. Real target computation remains prohibited until that
registry hash is fixed. DDO-01C-R must rerun every CA-01 audit and may evaluate
only H2 plus the frozen descriptive diagnostics. DDO-01D remains closed.
