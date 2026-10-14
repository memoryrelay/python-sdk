---
verified_at: 2026-10-14
verified_commit: 33feede6e95571a80cd8d0e53fe46cf68a51c5d0
---

# Documents — every document of this repository, and who owns its facts

The agent-facing files are the root `AGENTS.md` (the entry), its one-line pointer `CLAUDE.md`, and this `.github/icm/` folder; there were no agent instruction files before them. Everything below is a document a person reads; each restates facts that the code or a workflow owns, and the owner is right when they disagree.

## Pinned: current

Each is a `fact` node in the workspace; a stage names one when it needs it.

| Document | What it answers | Owner of the facts |
|---|---|---|
| [README.md](../../../README.md) | install, both clients, authentication, each resource, ICM workspaces, exceptions, options; also the PyPI long description (`pyproject.toml:9`) | `memoryrelay/`, `pyproject.toml` |
| [QUICKSTART.md](../../../QUICKSTART.md) | a one-page reference: setup, examples, client options | `memoryrelay/client.py`, `memoryrelay/resources/` |
| [RELEASE.md](../../../RELEASE.md) | the PyPI trusted-publisher settings and the release steps | `.github/workflows/ci-cd.yml`, `release.sh` |

`examples/basic_usage.py` and `examples/v2_async_and_byok.py` are code, read by the stage that changes what they call. `LICENSE` is MIT.

## Known drift

- `README.md:317-322` ("Links") points at `github.com/yourusername/memoryrelay-python`; the repository is `memoryrelay/python-sdk` (`pyproject.toml:53-54`).
- `README.md:301-315` ("Development") lints with `ruff check memoryrelay` and omits black; CI runs `ruff check .` and `black --check .` ([build-and-test.md](build-and-test.md)).
- `QUICKSTART.md:110-113` lists three resources; the clients also carry `extraction` and `icm` (`memoryrelay/client.py:74-78`).
- `RELEASE.md` predates the first release: "Step 2" says the script creates `v0.1.0`, both command blocks start with `cd` into a folder on the author's machine, and "Current Status" (37 tests, trusted publishing pending) is superseded by four published versions and PyPI's provenance for 0.4.0 ([upstream.md](upstream.md)). The publisher settings in "Step 1" are still the ones in force.
- `tests/test_integration.py:11` names memoryrelay/api's path ([gotchas.md](gotchas.md)).

A new document goes in one of the lists above when it is added.
