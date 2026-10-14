# 02_port — bring the approved differences across

One job: copy exactly the approved differences from memoryrelay/api at the recorded commit, and nothing else.

## Inputs
- Working (this run): `.github/icm/02-align/stages/01_compare/output/alignment.md`
- Reference (every run): `.github/icm/_shared/conventions.md`
- Reference (every run): `.github/icm/_shared/build-and-test.md`
- Reference (every run): `.github/icm/_shared/gotchas.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/release.md`.

## Process
1. On a branch from `origin/main`, copy each approved file from memoryrelay/api at the sha in `alignment.md`, byte for byte. Do not reformat or "improve" it here: the copy stays a copy.
2. Keep what `alignment.md` says to keep. Do not touch the version (`03-release` sets it), the publish job or `RELEASE.md`.
3. Check the public surface: every name `memoryrelay/__init__.py` exports still imports, and both clients attach the same resources.
4. Run `ruff check .`, `black --check .`, `mypy memoryrelay` and `pytest`, with `MEMORYRELAY_API_KEY` unset. A failure in a ported file is reported, not patched here: it is fixed in memoryrelay/api first, or the person drops that file from the set.
5. Run the comparison again: only the approved exceptions remain.

## Outputs
- change.md → output/ — the memoryrelay/api sha; each file ported; each exception kept and why; the checks' results; the final comparison output.

## Human check
A person reads the diff against `alignment.md`: only the approved differences moved, the final comparison shows only the agreed exceptions, and the checks are green.
