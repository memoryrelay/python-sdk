# 03-release — publish a version to PyPI

One run is one version: the number agreed, both version lines bumped in a reviewed pull request, the tag pushed by a person on the merge commit, and the version seen on PyPI and in the GitHub release. Four so far: `v0.1.0`, `v0.1.1`, `v0.3.0`, `v0.4.0`. Today this repository is the publisher; if that moves to memoryrelay/api, this job stops here ([upstream.md](../_shared/upstream.md)).

Stages, in order; inputs, outputs and checks for each are in [CONTEXT.md](CONTEXT.md):

1. [Plan](stages/01_plan/CONTEXT.md) — what ships and which number.
2. [Prepare](stages/02_prepare/CONTEXT.md) — the version-bump pull request.
3. [Publish](stages/03_publish/CONTEXT.md) — the tag, the publish run, the version on PyPI.

A published version is final: PyPI never accepts it twice.
