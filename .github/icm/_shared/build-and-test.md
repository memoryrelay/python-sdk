---
verified_at: 2026-10-15
verified_commit: b398f4ade5053147138b820135d12fdaf215ad2f
---

# Build and test — the commands, and what CI runs

- Install: `pip install -e ".[dev]"`; the dev extra is `pyproject.toml:40-48` (pytest, pytest-asyncio, pytest-cov, respx, mypy, ruff, black).
- CI is the `test` job of `.github/workflows/ci-cd.yml:14-51`, on every pull request to `main` and every push to `main`, for Python 3.10, 3.11 and 3.12: `ruff check .` (line 34), `black --check .` (line 37), `mypy memoryrelay` (line 40, `continue-on-error`, so type errors do not fail it), `pytest --cov=memoryrelay` (line 44), and a Codecov upload that never fails the job. Run the same four locally before a pull request.
- Tool settings: `pyproject.toml` from `[tool.mypy]` down (line length 100, ruff rules `E F I N W UP`, `asyncio_mode = "auto"`, `testpaths = ["tests"]`). The vendored `.github/icm/_system/generate.py` is excluded from ruff and black there, because it must stay byte-identical to memoryrelay/api's copy.
- Unit tests run against a mocked server: an `httpx.MockTransport` passed through the client (`tests/test_icm_sources.py:14-15`, `tests/test_memories_v2_sync.py:52`). A reproduction or a new test follows them and calls the client, never a copy of its logic.
- `tests/test_integration.py:20-27` calls the live API and is skipped unless `MEMORYRELAY_API_KEY` starts with `mem_`; it creates and deletes real records. CI sets no key, so it never runs there; run it only with a person's agreement and a key meant for testing.
- A green run of this repository on 2026-10-15: 13 passed, 12 skipped (the live tests).
- CodeQL runs as GitHub's default setup (no workflow file here); its alerts arrive as code-scanning alerts and are fixed through `01-fix`.
- The ICM check: `.github/workflows/icm-check.yml` runs `python .github/icm/_system/generate.py --check` when an entry or `.github/icm/` changes, and `--check --strict` every Monday.
