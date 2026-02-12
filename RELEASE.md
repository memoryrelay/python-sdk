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

## Step 2: Initial Release

Once PyPI trusted publishing is configured, run:

```bash
cd /home/ubuntu/.openclaw/workspace/memoryrelay-python-sdk
./release.sh patch
```

This will:
- Create git tag `v0.1.0`
- Push tag to GitHub
- GitHub Actions will automatically:
  - Run tests
  - Build package
  - Publish to PyPI
  - Create GitHub release

## Alternative: Manual First Release

If you want to do the first release manually (to create the PyPI project):

```bash
cd /home/ubuntu/.openclaw/workspace/memoryrelay-python-sdk

# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (you'll need API token)
twine upload dist/*
```

After manual first release, trusted publishing will work automatically.

## Verification

After release:
- Check PyPI: https://pypi.org/project/memoryrelay/
- Check GitHub releases: https://github.com/memoryrelay/python-sdk/releases
- Test install: `pip install memoryrelay`

## Current Status

- ✅ GitHub Actions workflow configured
- ✅ PyPI trusted publishing permissions in workflow
- ✅ Package metadata complete
- ✅ Tests passing (37/37)
- ⏳ PyPI trusted publishing setup (manual step required)
- ⏳ Release tag creation (ready to go)
