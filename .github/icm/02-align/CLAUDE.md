# 02-align — bring this copy level with memoryrelay/api

One run is one alignment: what differs between this repository and memoryrelay/api (its `sdk/python/`, or the routes the SDK calls) is listed, the approved part is ported byte for byte, and the result is proposed as a pull request. Pull request #2 (the SDK aligned to the API's schemas, 0.3.0) and #5 (the 0.4.0 tree taken from `sdk/python/`) are the two runs so far. Why the two copies exist, and which one publishes: [upstream.md](../_shared/upstream.md).

Stages, in order; inputs, outputs and checks for each are in [CONTEXT.md](CONTEXT.md):

1. [Compare](stages/01_compare/CONTEXT.md) — every difference, which side is ahead, what to port.
2. [Port](stages/02_port/CONTEXT.md) — the approved differences, copied, checked.
3. [Verify](stages/03_verify/CONTEXT.md) — the pull request, CI green.

An alignment does not publish, and it never moves publishing between the repositories.
