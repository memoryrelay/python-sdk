---
verified_at: 2026-10-14
verified_commit: 33feede6e95571a80cd8d0e53fe46cf68a51c5d0
---

# Upstream — who publishes, and where the SDK is written

## Who publishes today

- **This repository.** The `publish` job of `.github/workflows/ci-cd.yml:53-88` runs on a pushed `v*` tag and uploads with PyPI trusted publishing (`id-token: write`, line 58); `RELEASE.md:11-16` names this repository and `ci-cd.yml` as the trusted publisher. The PyPI package name and version are `pyproject.toml:6-7`.
- Check it, never assume it: `https://pypi.org/pypi/memoryrelay/json` gives the current version and each upload time; `https://pypi.org/integrity/memoryrelay/<version>/memoryrelay-<version>-py3-none-any.whl/provenance` names the repository and workflow that uploaded that file. On 2026-10-14 both said 0.4.0, uploaded 2026-10-04 by `memoryrelay/python-sdk` `ci-cd.yml`, the run for tag `v0.4.0`.
- memoryrelay/api has no workflow that publishes to PyPI (its `.github/workflows/` at `main`); its `sdk/python/pyproject.toml` declares the same package name, `memoryrelay`.

## The plan to move publishing (not done)

- memoryrelay/api [`docs/plans/2026-10-04-plugin-alignment-review.md`](https://github.com/memoryrelay/api/blob/main/docs/plans/2026-10-04-plugin-alignment-review.md), section "4. SDKs" and Recommendation 4, proposes making `sdk/python/` there the one publisher and retiring this repository as a publisher. That document owns the plan; its client table still says PyPI 0.3.0, written before 0.4.0 was published from here.
- Until a person carries it out, a release is cut here ([release.md](release.md)). Moving the trusted publisher, removing the `publish` job or archiving this repository is that decision, never a step of a fix, align or release run.

## How this copy relates to memoryrelay/api

- The 0.4.0 tree here was taken from memoryrelay/api `sdk/python/` (pull request #5, merged 2026-10-03, whose description records that `memoryrelay/` was identical to memoryrelay/api `sdk/python/memoryrelay` at `cea4bed`). `tests/`, `examples/`, `README.md` and `QUICKSTART.md` have counterparts there too; `pyproject.toml` differs at least in its description.
- That copy keeps moving. To see where the two stand: a checkout of memoryrelay/api and `diff -r memoryrelay <api>/sdk/python/memoryrelay`, or `gh api` on one file at a time. A difference is work for [02-align](../02-align/CLAUDE.md), not a reason to edit either side by hand.

## Where a change is written

- A new method, resource or option: in memoryrelay/api `sdk/python/` first (its `feature` route), where the API and its tests live, then ported here by `02-align`; written only here, the next port reverts it.
- A defect: fixed here by `01-fix` when it ships in a published version; the run says whether memoryrelay/api `sdk/python/` has the same defect, and a person decides whether it is fixed there too.
