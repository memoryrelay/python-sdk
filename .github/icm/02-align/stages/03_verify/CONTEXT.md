# 03_verify — pull request, CI green

One job: propose the port with what a user of the package will notice, and see CI green on it.

## Inputs
- Working (this run): `.github/icm/02-align/stages/02_port/output/change.md`
- Reference (every run): `.github/icm/_shared/build-and-test.md`
- Reference (every run): `.github/icm/_shared/conventions.md`
- Reference (only when the port should reach users in a version now): `.github/icm/_shared/release.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/architecture.md`.

## Process
1. Open the pull request from the branch to `main`: subject `feat: …` or `fix: …` naming what users gain, body with the memoryrelay/api sha, the files ported, the exceptions kept, and every breaking change for users (the generated release notes are built from it). Never merge it yourself.
2. Watch the `CI/CD` run on the head commit (all three Python versions) and `ICM check` when it runs. A red job is this run's to fix, back at stage 02.
3. Say whether the port should reach users now; if so, the person starts `03-release` after the merge.

## Outputs
- pull-request.md → output/ — the pull request URL; the memoryrelay/api sha; the CI status of the head commit; the breaking changes; whether a release is proposed.

## Human check
A reviewer reads `pull-request.md` and the CI results, then merges or not; nothing reaches PyPI until a person starts a release.
