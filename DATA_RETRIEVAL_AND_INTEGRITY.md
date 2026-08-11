# External data retrieval and integrity

This repository intentionally keeps the frozen numerical payload outside ordinary Git. No data were uploaded, regenerated, or relocated during this closure.

## External material and local locations

| Material | Local repository-relative locations | Why external |
|---|---|---|
| Frozen atlas, identifiability, attribution, and diagnostic data | `data/` (currently 1,965 files, approximately 633 MiB) | Bulk generated numerical evidence is unsuitable for ordinary Git. |
| Checkpoints and cached analysis state | `data/identifiability/checkpoints/`, `data/ddo02b_identifiability/`, and other stage-specific data subtrees | Required for traceability/rebuilds but represented in Git by manifests and hashes. |
| Python caches and temporary renders | `__pycache__/`, `.pytest_cache/`, `cache/`, `tmp/`, `.codex_tmp*/` | Rebuildable host-local output. |
| Literature copies | `publication/literature/` | Reference material may be copyright-restricted and is not project source. |
| Export archives | `*.zip`, `*.tar*`, `*.7z` | Packaging copies rather than canonical source. |

## Authoritative manifests

- `06_manifests/ddo02z_final_sha256.txt` is the final closure checksum ledger for key project, frozen data, report, publication, and status artifacts.
- `06_manifests/ddo02z_final_evidence_manifest.json` records the final frozen evidence and generated publication/closure artifacts.
- Stage manifests under `06_manifests/` remain authoritative for their own case registries, descriptors, partitions, inputs, and verdicts.
- `data/identifiability/ddo01e_checkpoint_manifest.json` and `data/ddo02b_identifiability/ddo02b_checkpoint_manifest.json` are the checkpoint-level sources inside the external tree.
- `provenance/datasets/dataset_manifest.csv` is only a Git-side index of these existing sources and does not replace them.

There is no authenticated public data repository, DOI, accession, or approved external download URL in the audited repository. Restoring data currently requires an authorized local/institutional backup preserving the repository-relative `data/` tree. A Git clone alone cannot rebuild the figures or fully audit the tables.

## Read-only verification

The checker reads manifests and payloads only. Quick mode checks existence and recorded sizes; full mode also calculates SHA256.

```bash
cd /Users/xiejinbo/Documents/SPH-DDO-PoC
python scripts/verify_external_data.py \
  --manifest 06_manifests/ddo02z_final_sha256.txt \
  --quick

python scripts/verify_external_data.py \
  --manifest 06_manifests/ddo02z_final_sha256.txt \
  --full
```

Checkpoint-specific checks can use the JSON manifests directly:

```bash
python scripts/verify_external_data.py \
  --manifest data/identifiability/ddo01e_checkpoint_manifest.json \
  --quick
```

Completeness requires zero `MISSING`, `SIZE_MISMATCH`, `HASH_MISMATCH`, and `UNREADABLE` results for every authoritative manifest in scope. Hash agreement establishes byte identity, not scientific correctness or historical code identity.

Observed snapshot on 2026-08-12: the final checksum ledger passed quick verification for 42/42 entries, and the inherited checksum ledger passed full SHA256 verification for 5/5 entries, with zero failures.

## Publication boundary

- Potentially publishable only after a separate license, authorship, privacy, and intellectual-property review: source code, non-sensitive manifest metadata, explicitly approved manufactured/synthetic datasets, and publication summaries.
- Not currently authorized for public release: the complete `data/` tree, cached/checkpoint payloads, local environment state, and third-party literature files.
- No scientific artifact gains publication permission merely because it is synthetic or has a SHA256 value.

Until a sanctioned repository and release decision exist, external data status is `LOCAL_OR_INSTITUTIONAL_STORAGE_ONLY`; this document does not authorize upload to any service.
