---
verified_at: 2026-10-15
verified_commit: b398f4ade5053147138b820135d12fdaf215ad2f
---

# Gotchas — traps already in the code or the tooling

- The `User-Agent` header is hard-coded `memoryrelay-python/0.1.0` (`memoryrelay/client.py:61`, `memoryrelay/async_client.py:61`) and `release.sh` does not bump it, so every version reports 0.1.0 to the API.
- `mypy` never fails CI (`.github/workflows/ci-cd.yml:41`, `continue-on-error`); run it and read it, do not trust the green tick.
- Error handling is copied per class: `_handle_errors` in each sync and async resource (`memoryrelay/resources/memories.py:310` and `:651`, and the same in agents, entities and extraction) plus `_raise_for` in `memoryrelay/resources/icm.py:32`. A fix to error parsing moves in every copy.
- `tests/test_integration.py:20-27` hits production when `MEMORYRELAY_API_KEY` starts with `mem_`, and a developer's shell often has one set. Unset it for `pytest` unless the live run is intended.
- `release.sh` uses GNU `sed -i` (lines 60-61); on macOS it fails before committing.
- A `v*` tag publishes whatever commit it points at, on a branch or not (`.github/workflows/ci-cd.yml:4-6` and `:56`); tag only a commit on `main`.
- `memoryrelay/` is a copy of memoryrelay/api `sdk/python/memoryrelay`: a change made only here is reverted by the next port, and one made only there never ships until it is ported ([upstream.md](upstream.md)).
