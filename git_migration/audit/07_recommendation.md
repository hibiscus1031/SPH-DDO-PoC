# Recommendation

## Repository boundary

Track source, tests, configuration, small manifests, small formal reports, claim/evidence maps, and figure-generation code.
Keep large datasets, trajectories, checkpoints, caches, full-text literature, and generated bulk artifacts on disk but outside ordinary Git.

## Migration decision

Initialize a new `main` repository only after the ignore and candidate lists are reviewed.
Git history begins (or continues) from the state that can be verified now. Frozen reports and manifests remain evidence, not invented commits.

## Remote decision

GitHub CLI was not installed at audit time. Complete local migration only; do not create a public repository.
