# 01_plan — what ships and which number

One job: what has merged since the last version, whether this repository still publishes, and the number to give it.

## Inputs
- Working (this run): the request — merged changes to ship, or a version asked for.
- Reference (every run): `.github/icm/_shared/release.md`
- Reference (every run): `.github/icm/_shared/upstream.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/architecture.md`.

## Process
1. Read what is published: `https://pypi.org/pypi/memoryrelay/json` (version, upload times) and `gh release list --repo memoryrelay/python-sdk`; the last tag is `git describe --tags --abbrev=0 origin/main`.
2. Confirm this repository still publishes ([upstream.md](../../../_shared/upstream.md)): the provenance of the last version names `memoryrelay/python-sdk` and `ci-cd.yml`, and the publish job is still in `.github/workflows/ci-cd.yml`. If publishing has moved to memoryrelay/api, say so and stop.
3. List what ships: `git log --format='%h %s' v<last>..origin/main`, each merged pull request with what a user notices.
4. Choose the number: while the version is 0.x, a breaking change takes the next minor (0.3.0 was one), anything else the next patch. Check it is not already on PyPI.
5. Name anything that should land first (an open fix, the `User-Agent` version in [gotchas.md](../../../_shared/gotchas.md)) and leave the choice to the person.

## Outputs
- plan.md → output/ — the published version and the last tag; that this repository still publishes, with the evidence; the pull requests that ship; the proposed number and why; anything proposed to land first.

## Human check
A person approves the version number.
