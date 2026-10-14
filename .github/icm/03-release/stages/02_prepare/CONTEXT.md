# 02_prepare — the version-bump pull request

One job: a pull request that changes the two version lines to the approved number, and nothing else.

## Inputs
- Working (this run): `.github/icm/03-release/stages/01_plan/output/plan.md`
- Reference (every run): `.github/icm/_shared/release.md`
- Reference (every run): `.github/icm/_shared/build-and-test.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/architecture.md`.

## Process
1. On a branch from `origin/main`, set the approved version in `pyproject.toml` and `memoryrelay/__init__.py`, the two lines `release.sh` would change. Do not run `release.sh` on the branch: it also tags, and a pushed tag on a branch commit publishes that commit.
2. Commit `chore: bump version to X`.
3. Run `ruff check .`, `black --check .` and `pytest`; build once as the publish job does (`pip install build`, `python -m build`) and confirm the wheel's name carries the new version.
4. Open the pull request to `main`: the version, the pull requests that ship (from `plan.md`), breaking changes named. Never merge it, never tag.
5. Watch the `CI/CD` run on the head commit until all three Python versions are green.

## Outputs
- release-pr.md → output/ — the pull request URL; the diff (two lines); the checks and the build result; the CI status of the head commit.

## Human check
A reviewer reads the diff (the two version lines, nothing else) and the CI result, then merges.
