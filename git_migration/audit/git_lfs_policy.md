# Git LFS policy

Git LFS availability: **git: 'lfs' is not a git command. See 'git --help'.**

No LFS rules are activated because Git LFS is not installed. No installation was attempted.

| Pattern | Count | Total MiB | Recommendation | Reason |
|---|---:|---:|---|---|
| `*.pdf` | 16 | 0.66 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.png` | 18 | 2.54 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.jpg` | 0 | 0.00 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.jpeg` | 0 | 0.00 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.tiff` | 16 | 17.62 | SELECTIVE_LFS_AFTER_INSTALL | only final, necessary large publication binaries merit LFS |
| `*.docx` | 0 | 0.00 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.pptx` | 0 | 0.00 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.xlsx` | 0 | 0.00 | ORDINARY_GIT_IF_FINAL | small final artifacts remain manageable and reviewable |
| `*.pt` | 0 | 0.00 | EXTERNAL_NOT_LFS | dataset/checkpoint payloads default to external storage with manifest references |
| `*.pth` | 0 | 0.00 | EXTERNAL_NOT_LFS | dataset/checkpoint payloads default to external storage with manifest references |
| `*.ckpt` | 0 | 0.00 | EXTERNAL_NOT_LFS | dataset/checkpoint payloads default to external storage with manifest references |
| `*.npz` | 1797 | 479.76 | EXTERNAL_NOT_LFS | dataset/checkpoint payloads default to external storage with manifest references |
| `*.h5` | 0 | 0.00 | EXTERNAL_NOT_LFS | dataset/checkpoint payloads default to external storage with manifest references |
| `*.hdf5` | 0 | 0.00 | EXTERNAL_NOT_LFS | dataset/checkpoint payloads default to external storage with manifest references |
