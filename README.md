# SPH-DDO-PoC

Scientific root for **SPH-DDO — Learning Structure-Preserving Discretization-Defect Operators for Smoothed Particle Hydrodynamics**.

The initial frozen DDO-00 outcome is `DDO_SPATIAL_DEFECT_AND_IDENTIFIABILITY_CONTRACT_FROZEN`. The later frozen route-closure status is `SPH_DDO_ONLINE_ROUTE_CLOSED_PUBLICATION_EVIDENCE_FROZEN`. The tested fixed-time, deployment-observable, instantaneous spatial-defect route did not satisfy the fresh H3 operational-identifiability gate. Neural training, optimizer creation, time integration, rollout, solver-in-loop work, and DDO-03 were therefore not authorized.

The historical repository `/Users/xiejinbo/Documents/SPH-PIO-PoC` is an external read-only evidence source and is not a parent stage of this project.

## Scientific scope and claim boundary

This project contains the static SPH baseline import, defect/operator definitions, analytical field and representation contracts, differentiable/observable descriptor analyses, atlas and identifiability scripts, formal qualification ledgers, publication figure/table generation, and claim/evidence mappings.

The closure applies only to the tested route. It is not a claim about all neural SPH, all observable representations, temporal information, equivariant graph networks, target intrinsic dimension, or high-resolution SPH truth.

## Repository structure

- `00_project_contract/`–`05_representation_contract/`: scope, defect, field, identifiability, and representation contracts.
- `01_imported_baseline/`: byte-identical static SPH baseline import identified by the inherited artifact manifest.
- `06_manifests/` and `07_reports/`: frozen evidence identities, qualification ledgers, and route decisions.
- `08_scripts/`: atlas, diagnostic, verification, publication, and test code.
- `figures/` and `publication/`: final figure exports, manuscript sources, and claim/evidence maps.
- `provenance/` and `git_migration/`: software/dataset/experiment provenance and the audited repository migration.

## Installation and validation

No formal project-scoped dependency lockfile existed at migration time. Review `provenance/environment/environment_audit.md` before constructing an isolated environment. Routine validation is limited to bounded, non-training tests under `08_scripts/test_*.py`; data generation, formal atlas execution, and scientific requalification are not repository smoke tests.

## Reproducibility and data policy

The 633 MiB `data/` tree remains external to ordinary Git and is referenced by existing manifests/hashes and `provenance/datasets/dataset_manifest.csv`. Final publication figures are versioned because they are a small, explicitly audited evidence set. Figure and table mappings are described in `publication/REPRODUCIBILITY.md`.

Historical experiments predate the first Git baseline. Their registry entries therefore use `UNKNOWN_HISTORICAL_CODE_STATE`; the migration commit must not be cited as experiment-time code.

## Qualification philosophy

Signal resolvability, scaling, identifiability, locality, and downstream authorization are separate gates. Passing an earlier gate never implies a later one. Negative evidence is reported within the frozen observational and deployment scope.

## License and citation

No license has been selected. Until the owner adds one, all rights remain reserved. A formal citation record is pending publication.
