# PyPI Trusted Publishing Setup

## Step 1: Configure PyPI Trusted Publishing

You need to set this up once on PyPI.org:

1. **Go to PyPI.org** (you'll need to do this manually):
   - Visit: https://pypi.org/manage/account/publishing/
   - Click "Add a new publisher"

2. **Fill in the form**:
   - **PyPI Project Name**: `memoryrelay`
   - **Owner**: `memoryrelay`
   - **Repository name**: `python-sdk`
   - **Workflow name**: `ci-cd.yml`
   - **Environment name**: (leave blank)

3. **Save** - PyPI will now trust releases from this GitHub Action

This setting is in force: every `memoryrelay` version on PyPI (0.1.0, 0.1.1, 0.3.0, 0.4.0) was uploaded by `ci-cd.yml` from this repository on a `v*` tag. Renaming or splitting `ci-cd.yml` stops publishing until the publisher above is updated on PyPI.

## Step 2: Release a version

1. **Bump the version.** It is written twice, `pyproject.toml` and `memoryrelay/__init__.py`, and they must agree. From a clean checkout:

   ```bash
   ./release.sh patch   # or minor, major
   ```

   The script bumps both files, commits `chore: bump version to X.Y.Z` and creates the annotated tag `vX.Y.Z` locally. It pushes nothing, refuses a dirty tree, and uses GNU `sed -i` (it fails on macOS).

2. **Get the bump onto `main` with CI green.** If it goes through a pull request, the local tag points at the branch commit, not at `main`: delete it (`git tag -d vX.Y.Z`) and tag the merge commit instead (`git tag -a vX.Y.Z -m "Release vX.Y.Z" <merge-sha>`).

3. **Push the tag.** `git push origin vX.Y.Z`. A `v*` tag publishes whatever commit it points at, so tag only a commit on `main`. The `CI/CD` workflow then:
   - runs the test matrix,
   - builds the wheel and sdist,
   - publishes to PyPI by trusted publishing (`skip-existing: true`: a version PyPI already holds is silently skipped),
   - creates the GitHub release with generated notes and both files.

PyPI never accepts the same version twice: a mistake is fixed by a new patch version, never by moving a tag. Do not upload with `twine` by hand; the trusted publisher is the only uploader.

## Verification

After release:
- Check PyPI: https://pypi.org/project/memoryrelay/ (or `https://pypi.org/pypi/memoryrelay/json`)
- Check GitHub releases: https://github.com/memoryrelay/python-sdk/releases
- Test install: `pip install memoryrelay==X.Y.Z` in a clean environment, then `python -c "import memoryrelay; print(memoryrelay.__version__)"`
