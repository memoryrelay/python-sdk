# 03-release — the pipeline

Decide the number, bump it in a pull request, and follow the tag to PyPI.

| Stage | Job | Input | Output | Human check |
|---|---|---|---|---|
| [`01_plan`](stages/01_plan/CONTEXT.md) | what ships and which number | the request | `output/plan.md` | A person approves the version number. |
| [`02_prepare`](stages/02_prepare/CONTEXT.md) | the version-bump pull request | 01_plan's `plan.md` | `output/release-pr.md` | A reviewer reads the diff (the two version lines, nothing else) and the CI result, then merges. |
| [`03_publish`](stages/03_publish/CONTEXT.md) | tag, publish run, version on PyPI | 02_prepare's `release-pr.md` | `output/published.md` | A person has seen version X on PyPI and the GitHub release with both files. |
