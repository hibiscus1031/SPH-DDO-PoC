# SPH-DDO title positioning memo

## Recommendation

Use formulation A as the **provisional v0.2 working title**, subject to journal-specific editing after the related-work prose is reconstructed:

> Pre-learning qualification of SPH spatial discretization defects: resolvability, scaling, and limits of instantaneous observable identifiability

This recommendation is based on scientific scope control and retrieval value, not rhetorical impact. It keeps the target (SPH spatial discretization defects), the workflow (pre-learning qualification), the positive findings (resolvability and scaling), and the bounded negative finding (limits of the tested instantaneous-observable identifiability) visible in the title.

## Comparative risk assessment

| Candidate | Scientific precision | Risk of overgeneralizing “non-identifiable” | CMAME/JCP fit | Searchability | Overall risk |
|---|---|---|---|---|---|
| Current: **Resolvable yet non-identifiable: pre-learning qualification of instantaneous SPH discretization-defect correction** | Moderate. The contrast is accurate only after reading the tested-scope qualifiers; “correction” can also suggest a trained method. | High. The unqualified lead phrase can be read as a general property of SPH defects or as architecture-independent impossibility. | Moderate. Memorable, but more rhetorical and negative-result led than method led. | Moderate. Contains SPH and discretization defect, but omits “spatial,” “scaling,” and “observable identifiability” from the searchable lead. | High |
| A: **Pre-learning qualification of SPH spatial discretization defects: resolvability, scaling, and limits of instantaneous observable identifiability** | High. Names the fixed-time spatial target, workflow, and bounded inference dimensions. | Low-to-moderate. “Limits of” keeps the finding conditional, although the abstract must still say “tested deployment-compatible observables.” | High. Reads as a numerical-method qualification study and exposes the componentwise evidence chain. | High. Strong terms include SPH, spatial discretization defects, resolvability, scaling, and observable identifiability. | Low |
| B: **Pre-learning qualification of SPH discretization defects: from resolvability to observable identifiability** | High but less explicit than A about spatial/fixed-time scope and the negative result. | Low. It does not label the target globally non-identifiable. | High. Concise and workflow oriented. | High, though it drops “spatial,” “scaling,” and “instantaneous.” | Low-to-moderate |

## Journal-positioning notes

For *Journal of Computational Physics*, formulation A most directly signals numerical analysis, operator qualification, and evidence about discretization defects. For *Computer Methods in Applied Mechanics and Engineering*, A also fits, but later prose should make the methodological transferability of the qualification hierarchy clear without claiming universality. Formulation B is the best shorter fallback if title length becomes an editorial concern.

The current “Resolvable yet non-identifiable” construction may be retained as a restrained phrase in an abstract or discussion sentence only when immediately followed by the frozen scope. It should not lead the title because the literature audit located adjacent uses of identifiability and several successful learned-correction/SPH workflows; a categorical negative title would invite an unnecessarily broad burden of proof.

## Prohibited title drift

- Do not use “unlearnable,” “impossible,” “fundamentally non-identifiable,” or “architecture-independent.”
- Do not imply a neural correction, differentiable solver, or solver-in-loop method was developed.
- Do not remove “SPH” or “discretization defect,” because doing so would broaden the literature claim beyond the audited scope.
- Do not use a “first” claim in the title.

Title status after L1: `PROVISIONAL_A_RECOMMENDED_NOT_FINALIZED`.

