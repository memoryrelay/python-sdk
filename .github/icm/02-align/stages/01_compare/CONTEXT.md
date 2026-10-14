# 01_compare — what differs from memoryrelay/api

One job: every difference between this repository and memoryrelay/api `sdk/python/` at one commit, with the side that is ahead and a proposal of what to port.

## Inputs
- Working (this run): the trigger — a merged memoryrelay/api pull request touching `sdk/python/` or a route the SDK calls, or a call that answers 404 or 422 against production.
- Reference (every run): `.github/icm/_shared/upstream.md`
- Reference (every run): `.github/icm/_shared/architecture.md`
- Reference (only when tests or examples differ): `.github/icm/_shared/build-and-test.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/release.md`.

## Process
1. Get memoryrelay/api at `main` (a clone outside this worktree, fetched; never its working tree) and record the commit sha.
2. Compare: `diff -r memoryrelay <api>/sdk/python/memoryrelay`, then `tests/`, `examples/`, `README.md`, `QUICKSTART.md` and `pyproject.toml` (dependencies, `requires-python`, version).
3. For each difference, say which side is ahead and why: `git log --oneline -- sdk/python/<file>` there, `git log --oneline -- <file>` here. A change that exists only here (a fix made here first) is listed apart: porting over it would revert it.
4. When the trigger is a route change, list each path the SDK calls that changed (`_base_url}/v` in the resources, `_PREFIX` in `memoryrelay/resources/icm.py`), with the API commit that changed it.
5. Propose the set to port, what stays as it is here (this repository's `pyproject.toml` description, URLs and release tooling are its own), and the version consequence: patch, minor, or breaking (named).

## Outputs
- alignment.md → output/ — the memoryrelay/api sha; every difference, its side and its cause; changes that exist only here; the proposed set to port and to keep; the version consequence.

## Human check
A person approves the list of differences to port, and decides what happens to each change that exists only here.
