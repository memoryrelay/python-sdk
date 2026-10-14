---
verified_at: 2026-10-14
verified_commit: 33feede6e95571a80cd8d0e53fe46cf68a51c5d0
---

# Release — the version, the tag, and what reaches PyPI

- The version is written twice: `pyproject.toml:7` and `memoryrelay/__init__.py:3`; they must agree. `release.sh` bumps both (lines 58-61), commits `chore: bump version to X` and makes the annotated tag `vX` locally (lines 63-69); it pushes nothing (lines 74-77) and refuses a dirty tree (lines 18-23).
- How versions were cut: `v0.3.0` tags a bump commit made on `main`; `v0.4.0` tags the merge commit of the pull request that carried the bump. Either way the tag points at a commit on `main` whose CI is green.
- Pushing the tag is the release: the `publish` job (`.github/workflows/ci-cd.yml:53-88`) waits for the test matrix, builds the wheel and sdist with hatchling (`pyproject.toml:1-3`), uploads to PyPI by trusted publishing with `skip-existing: true` (line 80), then creates the GitHub release with generated notes and both files (lines 82-88).
- The trusted publisher is configured on PyPI for this repository and the workflow file name `ci-cd.yml` (`RELEASE.md:11-16`): renaming or splitting that file stops publishing until a person updates PyPI.
- PyPI never accepts the same version twice, and `skip-existing` makes a re-pushed tag for a published version a silent no-op: a mistake is fixed by a new patch version; yanking is a person's act on pypi.org.
- Who publishes, and the plan to move it: [upstream.md](upstream.md).
- Check a release: `gh release view vX --repo memoryrelay/python-sdk` lists the wheel and sdist; `https://pypi.org/pypi/memoryrelay/json` gives the version; `pip install memoryrelay==X` in a clean environment imports and reports `memoryrelay.__version__`.
