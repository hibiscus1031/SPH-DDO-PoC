# 1 Executive status

**PRIVATE_REMOTE_CLOSURE_COMPLETE**

The project was initialized as an independent `main` repository after large-file, secret, environment, and historical-source audits. No scientific artifact was deleted, regenerated, or rewritten. The audited `main` branch is published only to a verified private GitHub repository.

# 2 Repository identity

| Field | Value |
|---|---|
| Path | `/Users/xiejinbo/Documents/SPH-DDO-PoC` |
| Repository name | `SPH-DDO-PoC` |
| Branch | `main` |
| Audited baseline commit | `2ca6e59fc134b710dd6f61bc882fb57e3c87e5a3` |
| Remote | `https://github.com/hibiscus1031/SPH-DDO-PoC.git` (`origin`) |
| Visibility | `PRIVATE`, verified through GitHub CLI |

# 3 What is tracked

The baseline contains 292 tracked files (28,901,339 apparent bytes; 27.6 MiB) before this report is added. No tracked file exceeds 100 MiB; the largest is `figures/main/figure04.tiff` at 1,848,224 bytes.

Tracked content includes project/qualification contracts, the static imported baseline source, 39 formal manifests/hash ledgers, 61 formal reports, 42 Python files (including 4 test modules), publication manuscripts and claim/evidence maps, 64 audited figure exports, and migration/provenance records.

# 4 What is intentionally untracked

2,025 files (660,829,904 bytes) are ignored and retained on disk. The principal category is the 633 MiB `data/` tree containing atlas cases, identifiability caches, diagnostics, checkpoints, and numerical ledgers. Python bytecode, temporary Codex render/check files, and publication literature are also excluded.

The working tree had zero non-ignored untracked files immediately after the baseline commit. Untracked/ignored does not mean deleted; manifests and hashes provide the repository-side evidence index.

# 5 Git LFS

- Installed: **NO**
- Used: **NO**
- LFS patterns: none
- LFS volume: 0 bytes

The final publication figures are a small, finite set (22.5 MiB total) and each file is below 1.9 MiB, so they are stored in ordinary Git. Bulk numerical data remain external rather than being placed in LFS by default.

# 6 Provenance

- Repository state: `provenance/repository_state.md`
- Existing manifest/hash index: `provenance/datasets/dataset_manifest.csv`
- Experiment registry: `provenance/experiments/experiment_registry.csv`
- Environment audit: `provenance/environment/environment_audit.md`
- Historical audit: `audit/historical_code_provenance_audit.csv`
- Exact baseline candidate paths: `audit/baseline_candidate_paths.txt`

Existing `06_manifests/inherited_artifact_manifest.csv`, `inherited_artifact_sha256.txt`, and DDO-02Z freeze/hash sources remain authoritative. The new dataset manifest is only an index.

# 7 Historical limitations

No pre-migration Git repository or independently verified Stage00–Stage08 historical source snapshot was found. The imported baseline has a byte-identity manifest/hash, but that is evidence for the imported tree, not a historical Git commit. All pre-baseline experiment registry rows therefore use `UNKNOWN_HISTORICAL_CODE_STATE`. No historical commit or tag was invented.

# 8 Secret audit

**PASS.** The bounded filename and content-signature audit found no private-key, AWS, GitHub, Hugging Face, OpenAI, or explicit credential signature in the tracked set. Secret values were never printed.

# 9 Reproducibility status

| Area | Status | Basis |
|---|---|---|
| Code | PARTIAL | Solver import, operators, analysis, qualification, publication, and tests are versioned; historical run commits are unavailable. |
| Data | PARTIAL | Strong manifests/hashes exist, but the 633 MiB payload is external to Git. |
| Figures | PARTIAL | Generation script and all audited exports are tracked; external frozen data are required. |
| Tables | PARTIAL | Per-table sources, hashes, and manual steps are closed; no verified single end-to-end presentation builder exists. |
| Environment | PARTIAL | The exact current dependency set is specified and tested; the historical run environment remains unknown. |

Validation: 52 tests collected and 52/52 bounded registry/H1–H4 semantic tests passed. No atlas rebuild, formal evaluation, training, optimizer, time integration, or rollout was run.

# 10 GitHub status

GitHub CLI is authenticated as `hibiscus1031`. The repository was confirmed absent, created with private visibility, and pushed through the ordinary non-force workflow:

```bash
gh repo create SPH-DDO-PoC --private --source=. --remote=origin
git push -u origin main
```

Do not use `--public`, force push, or overwrite an existing remote repository.

# 11 Remaining actions

No remaining action is required for the requested private-remote closure. Any future public release or external-data deposit requires a separate authorization and review.

# 12 Remote and reproducibility closure update

`requirements.txt` now records the minimal exact versions used by the current baseline. The environment is **PARTIAL**: `CURRENT_REPRODUCIBLE_ENVIRONMENT` is specified and 52/52 bounded tests pass, while `HISTORICAL_ENVIRONMENT_UNKNOWN` remains explicit.

`publication/TABLE_REPRODUCIBILITY.md` closes the table audit at **PARTIALLY_REPRODUCIBLE** for all three formal tables. Each table has frozen sources, full SHA256 references, manual-processing disclosure, and row-to-claim provenance, but no verified presentation-only end-to-end builder. No builder or scientific result was fabricated.

External-data handling and the read-only checker are documented in `DATA_RETRIEVAL_AND_INTEGRITY.md`. The final checksum ledger passed quick verification for 42/42 entries and the inherited checksum ledger passed full SHA256 verification for 5/5 entries. The intended index has zero secret signatures, zero files over 100 MiB, zero numerical binaries, zero literature PDFs, zero cache paths, and no executable/configuration host-path dependency.

The publishing identity is resolved from authenticated GitHub account `hibiscus1031` and its primary verified email. No history was amended. `origin/main` was created and pushed privately without force; the annotated tag `repo-audited-2026-08-12` identifies the final closure-report state and carries the historical-state disclaimer. Current status: **REPRODUCIBILITY_CLOSURE_PARTIAL** and **PRIVATE_REMOTE_CLOSURE_COMPLETE**.
