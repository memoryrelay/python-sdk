---
verified_at: 2026-10-15
verified_commit: b398f4ade5053147138b820135d12fdaf215ad2f
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

None known. The five items found at onboarding (README links and development commands, QUICKSTART's resource list, RELEASE.md's pre-0.1.0 steps, the live-test usage path) were corrected on 2026-10-15.

A new document goes in one of the lists above when it is added.
