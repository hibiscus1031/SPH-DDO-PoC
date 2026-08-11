# DDO-01D balance and dataset-QC report

## Release gates

| Check | Result |
|---|---:|
| Fresh case count | 512 / 512 |
| Family quotas | 128 each, pass |
| Unique canonical IDs | 512 / 512 |
| Deterministic registry replay | exact match |
| Observable archives and hashes | 512 / 512 |
| Reference archives and hashes | 512 / 512 |
| Mandatory CA-01 valid | 512 / 512 |
| Primary topology valid | 512 / 512 |
| Independent topology valid | 512 / 512 |
| Exact component closure | 512 / 512 |
| Unit and role schema valid | 512 / 512 |
| Observable nonfinite elements | 0 |
| Missing observable/reference fields | 0 / 0 |

## Prospective balance

- F1: resolution `{'16': 25, '24': 26, '32': 26, '48': 25, '64': 26}`; h/dx `{'2': 32, '3': 32, '4': 32, '5': 32}`; probe `{'density': 48, 'longitudinal': 40, 'transverse': 40}`; layout `{'regular': 128}`.
- F2: resolution `{'16': 25, '24': 26, '32': 26, '48': 26, '64': 25}`; h/dx `{'2': 32, '3': 32, '4': 32, '5': 32}`; probe `{'density': 51, 'longitudinal': 39, 'transverse': 38}`; layout `{'regular': 128}`.
- F3: resolution `{'16': 25, '24': 25, '32': 26, '48': 26, '64': 26}`; h/dx `{'2': 32, '3': 32, '4': 32, '5': 32}`; probe `{'density': 51, 'longitudinal': 38, 'transverse': 39}`; layout `{'regular': 128}`.
- F4: resolution `{'16': 16, '24': 16, '32': 32, '48': 32, '64': 32}`; h/dx `{'2': 32, '3': 32, '4': 32, '5': 32}`; probe `{'density': 64, 'longitudinal': 32, 'transverse': 32}`; layout `{'jitter_0.025': 32, 'jitter_0.05': 32, 'jitter_0.1': 32, 'regular': 32}`.

F4 contains 8 matched blocks with 16
cases per block and exact `4 h/dx x 4 disorder-state` coverage. These blocks
hold continuum field, mode, phase, resolution, amplitude, and polarization
fixed. Support sampling and neighbor count co-vary with `h/dx`.

## Precision provenance

Float32 is non-gating and excluded from primary `U_num`. Protocol counts are
`INDEPENDENT_FLOAT32_REBUILD=507`
and `PRIMARY_TOPOLOGY_CAST_FLOAT32=5`;
they are not aggregated as identical precision experiments.

## Missing and degenerate descriptor channels

No frozen descriptor channel is missing. The following globally constant
observable-side channels are retained and reported, not silently removed:

- `obs__eps64`
- `obs__mach`
- `obs__reynolds`

They are prescribed numerical constants for this atlas, so their degeneracy is
expected. Full per-channel element counts, ranges, and finite-value results are
in `data/atlas/ddo01d_release_audit.json`. No dataset-fitted standardization was
created; normalizations use only frozen scales and prescribed observable-side
case parameters.
