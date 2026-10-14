# 01_reproduce — reproduce the reported defect

One job: turn the report into a test that fails on demand, through the client, for the reason reported.

## Inputs
- Working (this run): the report — read whole with what it links: an issue, a red CI run (its failed job log), a code-scanning alert (rule, file, line), a user's call and the answer it got.
- Reference (every run): `.github/icm/_shared/architecture.md`
- Reference (every run): `.github/icm/_shared/build-and-test.md`
- Reference (every run): `.github/icm/_shared/gotchas.md`
- Reference (only when the API may have answered differently from what the SDK expects): `.github/icm/_shared/upstream.md`

Do NOT load: the other pipelines, other runs' output, `.github/icm/_shared/release.md`.

## Process
1. Restate the report as observed versus expected: the client (sync or async), the resource and method, the installed version (`memoryrelay.__version__`), the API's status and body if known.
2. Decide where the defect lives. A route or payload the API changed under the SDK is an alignment: say so and stop (route `align` in the root `AGENTS.md`). A wrong answer from the API itself belongs to memoryrelay/api: say so and stop.
3. Find the code path with [architecture.md](../../../_shared/architecture.md) and name the suspected cause as `path:line`. Note its async twin and, for error parsing, every `_handle_errors` copy ([gotchas.md](../../../_shared/gotchas.md)).
4. Write the failing test in `tests/`, with an `httpx.MockTransport` handler as the neighbouring tests do ([build-and-test.md](../../../_shared/build-and-test.md)). It calls the client, never a copy of its logic. For a code-scanning alert, the alert's rule and location are the reproduction, plus a test where the behaviour can be shown.
5. Run it with `MEMORYRELAY_API_KEY` unset and keep the failing output. If it passes, the reproduction is wrong or the report is: say which, and stop.

## Outputs
- reproduction.md → output/ — the restated report; where the defect lives and why; the suspected cause (`path:line`) and its twins; the test and the command; the failing output; what the reproduction does not cover.

## Human check
A person runs the test, or reads the alert or the log, and confirms it fails for the reported reason and not a neighbouring one.
