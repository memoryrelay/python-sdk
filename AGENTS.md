# python-sdk

`memoryrelay` on PyPI: the Python client for the MemoryRelay API (`api.memoryrelay.net`), sync and async, over memories, agents, entities, extraction and ICM workspaces (`/v2/icm`). The API it calls is owned by memoryrelay/api, and the package directory is a copy of that repository's `sdk/python/`. What leaves this repository is a reviewed pull request, or a version on PyPI.

**Who publishes today: this repository.** Every `memoryrelay` version on PyPI (latest 0.4.0) was uploaded by `ci-cd.yml` here on a `v*` tag; memoryrelay/api has no PyPI workflow. Its [alignment review](https://github.com/memoryrelay/api/blob/main/docs/plans/2026-10-04-plugin-alignment-review.md) ("4. SDKs", Recommendation 4) proposes making `sdk/python/` there the one publisher and retiring this repository as a publisher; that has not happened. Evidence and the check: [upstream.md](.github/icm/_shared/upstream.md).

## Where things live

| Path | What it holds |
|---|---|
| `memoryrelay/` | the package: two clients, one module per resource (sync and async class side by side), models, exceptions, integrations — mapped in [architecture.md](.github/icm/_shared/architecture.md) |
| `tests/`, `examples/` | tests against a mocked transport, live tests skipped without a key; two runnable examples |
| `pyproject.toml`, `release.sh` | version, dependencies, tool settings; the local bump-and-tag script |
| `.github/workflows/` | `ci-cd.yml` (lint and test on every pull request, publish to PyPI on a `v*` tag), `icm-check.yml` |
| `README.md`, `QUICKSTART.md`, `RELEASE.md` | the user guide; a one-page reference; the PyPI trusted-publishing setup ([documents.md](.github/icm/_shared/documents.md)) |
| [`.github/icm/_shared/`](.github/icm/_shared/CONTEXT.md) | what every job below draws on, one file per question |

## Jobs

| Pipeline | One run is |
|---|---|
| [01-fix](.github/icm/01-fix/CLAUDE.md) | one defect, reproduced, fixed, proposed |
| [02-align](.github/icm/02-align/CLAUDE.md) | this copy brought level with memoryrelay/api (its `sdk/python/` or the routes the SDK calls) |
| [03-release](.github/icm/03-release/CLAUDE.md) | one version tagged and published to PyPI |

## Route by what just happened

| Route | If | Go to | Then stop at |
|---|---|---|---|
| triage | an issue or report arrives and its kind is unclear | read it whole (`gh issue view <n> --comments`) and take the row below that fits | the row chosen, said to the person |
| which-sdk | asked which Python SDK is current, or which repository publishes `memoryrelay` | [upstream.md](.github/icm/_shared/upstream.md) | the answer, with the PyPI version and the workflow that uploaded it |
| fix | a defect: an issue, a failing test, a wrong result from a client call, a code-scanning alert | [01_reproduce](.github/icm/01-fix/stages/01_reproduce/CONTEXT.md) | a person has seen the reproduction fail |
| ci-red | `CI/CD` or `ICM check` is red on `main` | [01_reproduce](.github/icm/01-fix/stages/01_reproduce/CONTEXT.md), with the run log as the report | a person has seen the reproduction fail |
| align | memoryrelay/api changed a route the SDK calls, or its `sdk/python/` moved ahead of this copy | [01_compare](.github/icm/02-align/stages/01_compare/CONTEXT.md) | a person approves the differences to port |
| feature | a new method, resource or option is asked for | [upstream.md](.github/icm/_shared/upstream.md), "Where a change is written" | the person agrees where it is written |
| release | a version is to be published to PyPI | [01_plan](.github/icm/03-release/stages/01_plan/CONTEXT.md) | a person approves the version number |
| publish-check | a tag did not reach PyPI, or asked what PyPI has | [03_publish](.github/icm/03-release/stages/03_publish/CONTEXT.md), step 2 onwards, for that tag | a person has seen the version on PyPI |
| maintain | the weekly `ICM check` is red, or a fact's evidence moved | [the index](.github/icm/_shared/CONTEXT.md): re-read each fact against its files, fix the pointer, bump its frontmatter, run `generate.py` | a pull request read by a person |
| next | a stage's output was approved | the next numbered stage of the same job | a person reads that stage's output |
| status | asked for status | scan `.github/icm/*/stages/*/output/` | report what exists |

## Agents connecting remotely

This repository has no MemoryRelay workspace of its own: the hub workspace `memoryrelay-hub` includes it, and the hub's mirror compiles and serves these files at `https://api.memoryrelay.net/mcp` (key in `MEMORYRELAY_API_KEY`). An agent on a clone needs nothing: this file is the entry. Over MCP, start with `icm_context_build` for one route of this repository, report reads with `icm_report_reads` when a stage ends and the result with `icm_report_outcome`, and never write through MCP: a change is a branch and a pull request here.

## Rules

- Nothing moves to the next stage until a person has read the output of the last one. A stage writes to its own `output/`, never committed (one run per worktree or branch; clear it when the pull request merges or is abandoned); a job reads only its own run's output.
- Only a person pushes a `v*` tag: the push publishes to PyPI, and a published version can never be uploaded again.
- No run here retires this repository as a publisher or changes how it publishes; that is the review's recommendation, for a person to decide.
- `.github/icm/` points at the files that own each fact. When they disagree, the owning file is right: correct `.github/icm/` in the same pull request and bump its `verified_commit`.
