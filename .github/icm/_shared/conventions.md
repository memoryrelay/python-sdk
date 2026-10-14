---
verified_at: 2026-10-14
verified_commit: 33feede6e95571a80cd8d0e53fe46cf68a51c5d0
---

# Conventions — how code and changes are written here

- Python 3.10 is the floor: `requires-python` (`pyproject.toml:10`), the classifiers (lines 21-23), the tool targets under `[tool.mypy]`, `[tool.black]` and `[tool.ruff]`, and the CI matrix (`.github/workflows/ci-cd.yml:18`) move together, or not at all.
- Annotations: `from __future__ import annotations` and `X | None` (`memoryrelay/client.py:3`, line 31); public methods are typed (the package declares `Typing :: Typed`, `pyproject.toml:25`).
- Every resource has a sync class and an async twin in the same module with the same methods (`memoryrelay/resources/icm.py:155` and `:333`); a change to one is made to the other in the same pull request, as `README.md` promises users ("`AsyncMemoryRelay` exposes the same methods").
- Errors: a resource raises the `memoryrelay/exceptions.py` types from its `_handle_errors`, reading the API's `detail` (`memoryrelay/resources/memories.py:310-329`); ICM raises `IcmError` with the server's `code`. A new status or code gets its exception class there and its export in `memoryrelay/__init__.py`.
- Branches and pull requests target `main` (`.github/workflows/ci-cd.yml:3-8`); `main` has no branch protection, so the review is the only gate. Subjects follow conventional commits (`feat:`, `fix:`, `chore: bump version to X`, as `release.sh:66` writes it).
- There is no changelog file: the GitHub release notes are generated from the merged pull requests (`.github/workflows/ci-cd.yml:85`), so a pull request's title and description are the record of the change, with any breaking change named in them.
