# Locality and receptive-field ladder

## Purpose

The ladder tests whether bounded online neighborhoods contain enough information for the spatial defect. Every rung uses the same target records, group splits, metrics, and observable firewall. Larger rungs add information monotonically so that performance differences can be attributed to receptive field rather than a changed target or split.

## Rungs

| Rung | Information available | Required construction |
|---|---|---|
| L0 pair only | central particle plus one edge \((i,j)\) | \(\mathbf r_{ij}/h_{ij}\), pair state differences, pair kernel quantities, numerical parameters; evaluated as edge-conditioned diagnostics, not assumed sufficient for a particle target |
| L1 one-hop | all particles with \(r_{ij}\le h_{ij}\) | permutation-invariant sums/moments; geometry, consistency, physical and numerical descriptors |
| L2 enlarged local | union of one-hop neighbors of L1 or radius \(2h_i\) | exact radius/hop rule recorded; no target-driven neighbor selection |
| L3 regional | fixed periodic patch of radius \(4h_i\) or four-hop cap | summaries only, with particle count and physical radius reported |
| L4 global diagnostic | whole-domain invariant summaries | mode-blind state/geometry statistics only; absolute coordinates and analytical mode labels remain prohibited |

The pair-only rung cannot in general map a full particle defect without aggregation. It is retained to test pair attribution and R2 representation, not to presuppose pair-force sufficiency.

## Comparison protocol

For each rung, compute nearest-neighbor disagreement, conditional variance ratio, and the allowed oracle baselines using identical group-held-out folds. Report computational support size, feature dimension, feature-space coverage, and uncertainty. Nested features must be audited: L1 is a strict subset of L2, and so on.

Let \(E_l\) be group-held-out NRMSE and \(C_l\) conditional variance ratio. The smallest rung is provisionally locality-sufficient only if its upper 95% bootstrap bound is within 5% relative NRMSE of every larger rung through L4, its \(C_l\) is no more than 0.05 absolute above the best larger rung, and it satisfies the H3 prospective thresholds. If L3/L4 improves NRMSE by more than 10% relative with a nonoverlapping paired bootstrap interval, bounded one-hop locality is rejected for that target/component.

## Leakage controls

- No analytical wave vector, family ID, phase, exact derivative, target magnitude, or global coordinate enters any rung.
- Numerical parameters such as \(h/\Delta x\), declared physical \(\nu\), and online Mach/Re-like scalars are allowed Layer N inputs.
- Global summaries must be deployable from the low-cost state and invariant to particle ordering and periodic translation.
- Feature dimension growth is recorded; apparent gains are cross-checked with ridge effective degrees of freedom and matched low-order baselines.

## Outcome language

Possible future outcomes are `PAIR_DIAGNOSTIC_ONLY`, `ONE_HOP_SUFFICIENT_ON_ATLAS`, `ENLARGED_LOCAL_REQUIRED`, `REGIONAL_OR_GLOBAL_EVIDENCE_REQUIRED`, or `UNRESOLVED`. None is assigned in DDO-00.
