# Shared reference

What every job on this repository draws on. Each file points at the repository file that owns a fact; follow the pointer for the detail, and when the two disagree the owning file is right.

| File | Answers |
|---|---|
| [upstream.md](upstream.md) | which repository publishes `memoryrelay` today, how this copy relates to memoryrelay/api's `sdk/python/`, where a change is written |
| [architecture.md](architecture.md) | the clients, the resources, models and exceptions, and where each lives |
| [build-and-test.md](build-and-test.md) | install, lint, format, type check, tests (mocked and live), what CI runs |
| [conventions.md](conventions.md) | the Python floor, style, the sync and async twins, branches, commits, the record of a change |
| [release.md](release.md) | the version, the tag, what the publish job does, how to see a version on PyPI |
| [gotchas.md](gotchas.md) | traps that already exist in the code or the tooling, one line each |
| [documents.md](documents.md) | every document: which are pinned, which drift, who owns their facts |

Each stage's contract names the files it loads.
