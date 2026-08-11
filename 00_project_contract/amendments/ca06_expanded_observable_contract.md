# CA-06 expanded observable contract

Status: `DDO_CA06_EXPANDED_OBSERVABLE_CONTRACT_FROZEN`

This contract was frozen after DDO-02A and before any fresh DDO-02B reference target was evaluated.

## Deployability and firewall

Formal inputs may use only fields classified `RUNTIME_DIRECT` or `RUNTIME_ESTIMABLE` in the DDO-02A ledger. `obs__kh_max`, `obs__kh_rms`, `obs__mode_count`, and `obs__jitter_fraction` are DESIGN_ONLY and prohibited. No analytical derivative, continuum value, defect, or reference-minus-low-cost quantity may enter a descriptor.

## Content ladder

- C0: deployable geometry/graph scalars G, excluding DESIGN_ONLY fields.
- C1: C0 plus low-cost consistency residuals C.
- C2: C1 plus low-cost physical state and baseline SPH operator values P.
- C3: C2 plus the 30 frozen higher-order moment, observable-frame directional, and local quadratic-reconstruction descriptors listed in `data/ddo02a/candidate_descriptor_dictionary.csv`.

The CA-05 L0--L3 ladder is unchanged: particle, one-hop, unique two-hop, and case-global observable summary. Each C3 descriptor is evaluated at L0 and summarized by mean/std/min/max at L1, L2 and L3.

## Frames and degeneracy

The local O(2) frame is the principal frame of the observable second weighted particle moment. Its first-axis sign is fixed lexicographically from observable geometry and its second axis gives determinant +1. If the normalized eigenvalue gap is below 1e-6, the frame is marked degenerate and deterministically falls back to the global identity frame. Targets may only be transformed by this already-frozen observable frame for equivariant diagnostics.

## Moments and reconstruction

Neighbor weights are exp(-|r/h|^2), normalized per particle. Second-, third- and fourth-order tensor moments, contractions, eigen-invariants, condition number and angular harmonic magnitudes m=1..4 are computed in O(neighbors). Density and velocity use a weighted quadratic basis [x,y,x^2/2,xy,y^2/2]. Rank below 5, nonfinite condition, or condition above 1e12 triggers a retained failure flag; coefficients fall back to zero and residual/condition diagnostics remain present. Scaling uses only frozen physical scales followed by train-fold median/IQR; zero-IQR channels are excluded fold-locally.

## Fresh evidence and gates

DDO-02B contains exactly 384 complete cases, 96 each in F1--F4. Fresh phases are pi/7, 3pi/7 and 5pi/7; fresh disorder seeds are 20260901, 20260907 and 20260913. Exact CA-05 five-fold lineage partition, 128-particle SHA sampling, exact cKDTree, non-neural oracle, bootstrap and H3/H4 thresholds remain unchanged. No old DDO-01D case is formal evidence.
