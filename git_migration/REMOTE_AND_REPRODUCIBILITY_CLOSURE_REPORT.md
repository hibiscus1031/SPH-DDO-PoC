# Remote and reproducibility closure report

Audit date: 2026-08-12 (Asia/Shanghai)

## Executive status

- `REPRODUCIBILITY_CLOSURE_PARTIAL`
- `PRIVATE_REMOTE_CLOSURE_COMPLETE`

No scientific recomputation, atlas build, training, formal evaluation, frozen-data change, source refactor, history rewrite, force operation, external-data upload, or historical Stage reconstruction was performed. Only the audited Git repository was pushed to its private remote.

## Repository and identity

| Item | Result |
|---|---|
| Local branch | `main`; final audited target is resolved by `repo-audited-2026-08-12` |
| Initial closure commit | `2fc3a51f0d68622416a2b87c1d234579a9b1a457` |
| Global identity | `user.name` and `user.email` unset |
| Local identity | `hibiscus1031 <2623839613@qq.com>`; email is primary and verified by authenticated GitHub API |
| Historical HEAD identity | `谢槿博 <xiejinbo@Jinbo-Mac.local>`; not accepted for future publishing |
| Remote | `https://github.com/hibiscus1031/SPH-DDO-PoC.git` (`origin`) |
| Private visibility | `PRIVATE`, verified through GitHub CLI before and after push |
| Tag | `repo-audited-2026-08-12`; annotated tag targeting the final closure-report commit |

The identity resolution is recorded in `git_migration/git_identity_action_required.md`. The GitHub profile name is unset, so the authenticated account login is used as the repository-local author name; no email was inferred or guessed.

## Current environment closure

The AST import audit covered project Python source, tests, publication scripts, and analysis/qualification scripts. `requirements.txt` records the exact current Python 3.13.9 environment dependencies: NumPy, SciPy, Matplotlib, pandas, Pillow, pypdf, scikit-learn, PyTorch, and pytest. It is a minimal project specification, not a Mac-wide `pip freeze`.

- `CURRENT_REPRODUCIBLE_ENVIRONMENT`: specified and bounded-tested.
- `HISTORICAL_ENVIRONMENT_UNKNOWN`: retained because no experiment-time lockfile was recovered.
- `python -m pytest --collect-only -q`: 52 tests collected.
- `python -m pytest -q`: 52/52 passed.
- Environment status: **PARTIAL**, not `FULL`.

## Table closure

`publication/TABLE_REPRODUCIBILITY.md` records the required fields for all formal tables:

| Table | Status | Basis |
|---|---|---|
| Table 1 — qualification hierarchy | `PARTIALLY_REPRODUCIBLE` | Frozen ledgers/manifests, full hashes, and row claims exist; final wording/Markdown assembly is manual. |
| Table 2 — initial versus fresh metrics | `PARTIALLY_REPRODUCIBLE` | Frozen metric/verdict files and hashes exist; selection, approved rounding, and assembly are manual. |
| Table 3 — evidence-set design | `PARTIALLY_REPRODUCIBLE` | Frozen registries/manifests and row claims exist; role wording and assembly are manual. |

No `scripts/build_publication_tables.py` was invented because the current repository does not encode every presentation decision in machine-readable form. This prevents overstating automation and does not alter any scientific result.

## External data and integrity

`DATA_RETRIEVAL_AND_INTEGRITY.md` documents the ignored 1,965-file, approximately 633 MiB `data/` tree, authoritative manifests, completeness rules, and publication boundaries. `scripts/verify_external_data.py` is read-only and supports `--manifest`, `--quick`, and `--full`.

- Final DDO-02Z checksum ledger quick verification: 42/42 passed.
- Inherited artifact checksum ledger full SHA256 verification: 5/5 passed.
- Missing, size mismatch, hash mismatch, and unreadable results: zero.
- External data status: `LOCAL_OR_INSTITUTIONAL_STORAGE_ONLY`; no upload or public-release authorization was inferred.

## Security, size, and portability

The intended index contains 299 files and 28,933,028 apparent bytes.

- Secret/token/private-key signature audit: **PASS**, zero findings.
- Files over 100 MiB and over 10 MiB: zero.
- Tracked numerical binaries, duplicate numerical dumps, checkpoint/trajectory paths, literature PDFs, and cache paths: zero.
- Absolute host-path occurrences in tracked historical/research text: 19, retained without mechanical replacement.
- Executable/configuration host-path dependencies: zero.

## Remote and tag closure

GitHub CLI is authenticated as `hibiscus1031`, the verified identity is configured locally, and `hibiscus1031/SPH-DDO-PoC` was confirmed absent before creation. All pre-push gates passed. The repository was created with `--private`, `main` was pushed without force or mirror, and remote visibility was verified as `PRIVATE`.

The annotated tag `repo-audited-2026-08-12` targets the final closure-report commit. Its message states: “This tag identifies the audited repository state after Git migration. It does not reconstruct or assert historical experiment code states.” The tag is not a Stage tag and makes no historical-state claim.
