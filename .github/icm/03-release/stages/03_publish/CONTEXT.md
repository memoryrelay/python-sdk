# 03_publish — tag, publish run, version on PyPI

One job: the person's tag on the merge commit becomes a version on PyPI and a GitHub release with both files, and that is checked from the outside.

## Inputs
- Working (this run): `.github/icm/03-release/stages/02_prepare/output/release-pr.md`
- Reference (every run): `.github/icm/_shared/release.md`
- Reference (only when the publish run failed): `.github/icm/_shared/build-and-test.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/architecture.md`.

## Process
1. After the merge, give the person the exact commands for the merge commit on `main`: `git tag -a vX -m "Release vX" <merge sha>` and `git push origin vX`. The agent never pushes a tag; it waits for the person's push.
2. Follow the `CI/CD` run for the tag (`gh run list --repo memoryrelay/python-sdk --branch vX`, then `gh run watch`): the test matrix, then `publish`.
3. Check PyPI: `https://pypi.org/pypi/memoryrelay/json` shows X with today's upload time, and the provenance of its wheel names `memoryrelay/python-sdk` and `ci-cd.yml` ([release.md](../../../_shared/release.md)).
4. Check the GitHub release: `gh release view vX --repo memoryrelay/python-sdk` lists the wheel and the sdist.
5. In a clean virtual environment, `pip install memoryrelay==X`, import it, print `memoryrelay.__version__`.
6. On a red `publish` step, read its log: a trusted-publisher refusal is the PyPI setting in `RELEASE.md`, for a person to change; a build failure goes to `01-fix`. Never move or re-push a tag for a version PyPI already holds.

## Outputs
- published.md → output/ — the tag and its commit; the run URL and result; the PyPI version, upload time and provenance; the GitHub release files; the clean-install output.

## Human check
A person has seen version X on PyPI and the GitHub release with both files.
