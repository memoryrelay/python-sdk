# 02_fix — change the cause, not the symptom

One job: the smallest change at the defect's cause that turns the reproduction green without weakening it, in the sync and async clients alike.

## Inputs
- Working (this run): `.github/icm/01-fix/stages/01_reproduce/output/reproduction.md`
- Reference (every run): `.github/icm/_shared/conventions.md`
- Reference (every run): `.github/icm/_shared/gotchas.md`
- Reference (only when the fix changes what is sent to the API or how its answer is read): `.github/icm/_shared/upstream.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/release.md`.

## Process
1. Read the reproduction and its suspected cause. Confirm the cause in the code before changing anything; if it moved, record where it really is.
2. Change the cause. Do not edit the reproduction to make it pass; if it was wrong, go back to stage 01.
3. Keep the public surface: names exported in `memoryrelay/__init__.py`, method signatures, return types and exception classes. If the fix needs a new method or a breaking change, stop: it is written in memoryrelay/api first ([upstream.md](../../../_shared/upstream.md), "Where a change is written").
4. Move every copy: the async twin of each class touched, and every `_handle_errors` when error parsing changes ([conventions.md](../../../_shared/conventions.md)).
5. Look at the same file in memoryrelay/api `sdk/python/` and record whether it has the same defect. Do not change that repository.
6. Run the reproduction (green now), then `ruff check .`, `black --check .`, `mypy memoryrelay` (read it: CI does not fail on it) and `pytest`.
7. If the fix is a lesson, add one line to [gotchas.md](../../../_shared/gotchas.md) with its source.

## Outputs
- change.md → output/ — the cause in one paragraph; each file changed and why; the twins and copies moved; whether memoryrelay/api has the same defect; the reproduction's passing output; the checks' results.

## Human check
A person reads the diff beside the reproduction: it removes the cause, the async twin and every copy moved with it, the public surface is unchanged; and decides from `change.md` whether memoryrelay/api needs the same fix.
