# Environment audit

Audit date: 2026-08-12 (Asia/Shanghai)

## Dependency-source audit

Before this closure, the repository had no `pyproject.toml`, `requirements.txt`, `environment.yml`, or lockfile. A project-wide AST import scan covered Python source, tests, publication scripts, and analysis/qualification scripts. It identified these third-party distributions in the current working environment:

| Distribution | Current version | Import role |
|---|---:|---|
| NumPy | 1.26.4 | array/numerical operations throughout the project |
| SciPy | 1.17.1 | spatial, statistical, interpolation, and numerical analysis |
| Matplotlib | 3.10.8 | publication and diagnostic figure generation |
| pandas | 3.0.1 | tabular publication/release processing |
| Pillow | 12.1.1 | publication image and release-audit handling |
| pypdf | 6.14.2 | publication PDF inspection |
| scikit-learn | 1.9.0 | diagnostic learning/identifiability analysis |
| PyTorch | 2.10.0 | imported baseline and scientific computation code |
| pytest | 9.1.1 | bounded test suite |

The interpreter used for the audit is Python 3.13.9. Exact current pins are now recorded in the repository-root `requirements.txt`. This is a minimal project import specification; it is not a system-wide `pip freeze` and contains no unrelated host packages.

## Reproducibility boundary

`CURRENT_REPRODUCIBLE_ENVIRONMENT`: the dependency versions currently installed, importable, and exercised by the bounded tests are specified from the audited Git baseline onward.

`HISTORICAL_ENVIRONMENT_UNKNOWN`: no independently verified historical environment file or lockfile was found for the experiments that produced the frozen evidence. The new requirements file must not be cited as their exact experiment-time environment.

## Bounded validation

Validation commands are intentionally limited to test discovery and the previously audited unit/semantic suite:

```bash
python -m pytest --collect-only -q
python -m pytest -q
```

Observed result on 2026-08-12: 52 tests collected in 0.18 s; 52/52 passed in 20.66 s.

No atlas build, formal evaluation, training, optimizer run, time integration, rollout, or scientific-result regeneration is authorized by this environment audit.

## Assessment

Environment = **PARTIAL**. The current baseline now has explicit, exact dependency pins and bounded test coverage. It is not `FULL` because the historical run environment remains unknown, no cross-platform lock with artifact hashes was recovered, and the external scientific data are not installed by the dependency specification.
