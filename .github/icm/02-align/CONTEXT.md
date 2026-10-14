# 02-align — the pipeline

List what differs from memoryrelay/api, port only what a person approved, and prove the copy the way CI will.

| Stage | Job | Input | Output | Human check |
|---|---|---|---|---|
| [`01_compare`](stages/01_compare/CONTEXT.md) | what differs from memoryrelay/api | the trigger | `output/alignment.md` | A person approves the list of differences to port, and decides what happens to each change that exists only here. |
| [`02_port`](stages/02_port/CONTEXT.md) | bring the approved differences across | 01_compare's `alignment.md` | `output/change.md` | A person reads the diff against `alignment.md`: only the approved differences moved, the final comparison shows only the agreed exceptions, and the checks are green. |
| [`03_verify`](stages/03_verify/CONTEXT.md) | pull request, CI green | 02_port's `change.md` | `output/pull-request.md` | A reviewer reads `pull-request.md` and the CI results, then merges or not; nothing reaches PyPI until a person starts a release. |
