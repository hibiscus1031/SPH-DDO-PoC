# Table reproducibility

Audit date: 2026-08-12. This audit traces the three formal tables in `publication/p3_main_tables.md`. It does not recompute scientific results.

## Table 1

| Field | Record |
|---|---|
| `table_id` | Table 1 — Final componentwise qualification hierarchy |
| `scientific_role` | Summarizes the frozen H1–H6 componentwise qualification and prerequisite states without converting unevaluated stages into failures. |
| `source_data` | `02_defect_definitions/operator_decomposition.md`; `publication/final_hypothesis_ledger.csv`; `06_manifests/ddo01br_manifest.json`; `06_manifests/ddo01cr_manifest.json`; `data/ddo02b_identifiability/ddo02b_metrics.json`; `data/ddo02b_identifiability/ddo02b_formal_verdicts.json`; `06_manifests/ddo02z_final_status_ledger.json`; row bindings in `publication/p3_table_claim_map.csv` |
| `source_hash` | `13c01a36aecfd977fa8d2666db0a1aa57c1bad53b1d1c768752ec207a1f4162b`; `694841a5ff154ebaefa39207a526739eee619a8db6fb53d02447b92d92ba0743`; `9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875`; `44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef`; `551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582`; `6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c`; `0f7c74b44575a3f744f31b1d2c7347d462dbfdfb381f47b0fb54087daddce54a` |
| `generation_script` | None verified for the final Markdown table. `08_scripts/publication_p1_assemble.py` creates the earlier plan-level mapping only. |
| `manual_processing` | Component selection, permitted wording, prerequisite vocabulary, and Markdown assembly were manual; row-level claims and prohibited extrapolations are recorded in `publication/p3_table_claim_map.csv`. |
| `current_status` | `PARTIALLY_REPRODUCIBLE` |

## Table 2

| Field | Record |
|---|---|
| `table_id` | Table 2 — Initial versus fresh operational-identifiability metrics |
| `scientific_role` | Places the frozen development and fresh C3/L3 metrics, thresholds, and all-gates decisions side by side. |
| `source_data` | `data/identifiability/ddo01e_metrics.json`; `data/identifiability/ddo01e_formal_verdicts.json`; `data/ddo02b_identifiability/ddo02b_metrics.json`; `data/ddo02b_identifiability/ddo02b_formal_verdicts.json`; row bindings in `publication/p3_table_claim_map.csv` |
| `source_hash` | `871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb`; `478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e`; `551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582`; `6cbedb7c46bc4c3b622ef2601ee4631b9763976bb98dd414fc9dd6d33c88d87c` |
| `generation_script` | None verified for the final Markdown table. |
| `manual_processing` | Values were selected from frozen metric files and rounded to the approved publication precision; the all-gates wording was manually assembled. No replacement score or scientific value was recomputed in this closure. |
| `current_status` | `PARTIALLY_REPRODUCIBLE` |

## Table 3

| Field | Record |
|---|---|
| `table_id` | Table 3 — Evidence-set design |
| `scientific_role` | Distinguishes H1/H2 qualification data, consumed development evidence, and fresh prospective evidence with their frozen case/sample counts. |
| `source_data` | `06_manifests/ddo01br_manifest.json`; `06_manifests/ddo01cr_manifest.json`; `06_manifests/ddo01d_manifest.json`; `07_reports/ddo01d_atlas_report.md`; `06_manifests/ddo02b_case_registry.json`; `data/ddo02b_identifiability/ddo02b_metrics.json`; row bindings in `publication/p3_table_claim_map.csv` |
| `source_hash` | `9dee9a6e1894e8c1745749b159915f7adc5a422c7b612f447188ee0c01e9a875`; `44bc51a9835be9c3bd9cd2732a9f1b9aee28cbc98cb2ca3931b83ad70f584fef`; `aa348eea6d59dd72d4d80116e7a44b212d9f6b571e79bbff514ceab59f0515f8`; `34287fad5e29fec9cafd9f66899a4ba1069095d9b8d19d495aacfd4f1c21fd9c`; `5588bcc92c0db124481187c17c1e313ef308cddfc75968f152107a4abb1264b4`; `551dc207bb23d22271f66d76df4fc65c08aa8649e366183ddc2db23072d2d582` |
| `generation_script` | None verified for the final Markdown table. |
| `manual_processing` | Evidence-role labels and the Markdown presentation were manually assembled from the frozen registries/manifests. |
| `current_status` | `PARTIALLY_REPRODUCIBLE` |

## Closure assessment

All three tables have frozen inputs, authoritative SHA256 values, and row-to-claim provenance, but none has a verified presentation-only end-to-end builder. Therefore the table layer is `PARTIALLY_REPRODUCIBLE`, not `FULLY_REPRODUCIBLE`. A `scripts/build_publication_tables.py` entry point was deliberately not invented: the current files do not encode all wording and formatting decisions in a machine-readable form, and silently recreating those decisions would overstate reproducibility.

The canonical presentation remains `publication/p3_main_tables.md` (SHA256 `3599b64c0bdef26776f11dd9c35c80caf159f111ccbb9c4dd6daf780f63d337d`); its row-claim map has SHA256 `2e1b74e30f546995268c6059dda4d709507ad8ba7b655387de0b41262a31cce2`. Integrity of external inputs is checked with `scripts/verify_external_data.py`; regenerating atlases, metrics, verdicts, or any scientific result is prohibited.
