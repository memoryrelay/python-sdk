# 03_verify — checks, pull request, CI green

One job: prove the fix the way CI proves it, and propose it so the description can serve as its release note.

## Inputs
- Working (this run): `.github/icm/01-fix/stages/02_fix/output/change.md`
- Reference (every run): `.github/icm/_shared/build-and-test.md`
- Reference (every run): `.github/icm/_shared/conventions.md`
- Reference (only when the fix should reach users in a version now): `.github/icm/_shared/release.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/architecture.md`.

## Process
1. Run what CI runs ([build-and-test.md](../../../_shared/build-and-test.md)): `ruff check .`, `black --check .`, `mypy memoryrelay`, `pytest --cov=memoryrelay`. Keep the output.
2. Open the pull request from a branch to `main`, subject `fix: …`. The body holds the reproduction, the cause, the evidence, what a user of the package will notice (the generated release notes are built from it), and whether memoryrelay/api `sdk/python/` has the same defect. Never merge it yourself.
3. Watch the `CI/CD` run on the head commit (all three Python versions) and `ICM check` when it runs. A red job is this run's to fix, back at stage 02 if the cause is in the change.
4. Say whether the fix should reach users now; if so, the person starts `03-release` after the merge ([release.md](../../../_shared/release.md)).

## Outputs
- pull-request.md → output/ — the pull request URL; the checks run and their results; the CI status of the head commit; the memoryrelay/api note; whether a release is proposed.

## Human check
A reviewer reads `pull-request.md` and the CI results, then merges or not; nothing reaches PyPI until a person starts a release.
