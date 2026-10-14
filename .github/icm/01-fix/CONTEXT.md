# 01-fix — the pipeline

Make it fail, make it pass for the right reason in every copy, and prove it the way CI will.

| Stage | Job | Input | Output | Human check |
|---|---|---|---|---|
| [`01_reproduce`](stages/01_reproduce/CONTEXT.md) | reproduce the reported defect | the report | `output/reproduction.md` | A person runs the test, or reads the alert or the log, and confirms it fails for the reported reason and not a neighbouring one. |
| [`02_fix`](stages/02_fix/CONTEXT.md) | change the cause, not the symptom | 01_reproduce's `reproduction.md` | `output/change.md` | A person reads the diff beside the reproduction: it removes the cause, the async twin and every copy moved with it, the public surface is unchanged; and decides from `change.md` whether memoryrelay/api needs the same fix. |
| [`03_verify`](stages/03_verify/CONTEXT.md) | checks, pull request, CI green | 02_fix's `change.md` | `output/pull-request.md` | A reviewer reads `pull-request.md` and the CI results, then merges or not; nothing reaches PyPI until a person starts a release. |
