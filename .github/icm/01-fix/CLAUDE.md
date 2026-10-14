# 01-fix — fix a defect

One run is one defect in the published package: reproduced against a mocked server, fixed at its cause in both clients, verified the way CI verifies, and proposed as a pull request. `fix:` is the most common subject on `main`, and code-scanning alerts arrive the same way (pull requests #3 and #4).

Stages, in order; inputs, outputs and checks for each are in [CONTEXT.md](CONTEXT.md):

1. [Reproduce](stages/01_reproduce/CONTEXT.md) — make it fail on purpose, through the client.
2. [Fix](stages/02_fix/CONTEXT.md) — change the cause in every copy, watch the reproduction pass.
3. [Verify](stages/03_verify/CONTEXT.md) — the checks CI runs, the pull request, CI green.

A fix does not publish: a person starts `03-release` when it should reach users.
