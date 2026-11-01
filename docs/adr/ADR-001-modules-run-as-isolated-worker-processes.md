# ADR-001: Modules run as isolated worker processes

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | PRD Q8 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** PRD Q8 asks whether modules should be worker processes or local HTTP services. There is one user on one Windows PC, about ten modules, and runs happen on demand. The runtime must isolate failures, run modules in parallel, enforce timeouts and let each module be tested alone.

**Decision.** Each module exposes one function, `run(raw_dir, params, as_of) -> ModuleOutput`, wrapped by a CLI from the contract library. The orchestrator starts each module as its own subprocess with a timeout (default 120 s, set in `module.toml`), runs up to CPU cores − 1 at once, and reads the JSON file the module writes. A crash, timeout or schema-invalid file becomes status "unavailable" with the reason and the last good as-of time.

**Consequences.** A pandas crash or memory blow-up in one module cannot stop another, because each has its own interpreter. Tests run the same CLI against a fixture folder. There are no ports or health checks to manage. The cost is under a second of interpreter start-up per module, well inside the 60 s and 5 min budgets.

**Alternatives rejected.** Threads in one process: no hard timeout and a native crash takes everything down. One local HTTP service per module: ten long-running processes, ports and health checks for a single user, which threatens the 5-minute setup goal (NFR-13). Docker per module: Docker Desktop is heavy on Windows and adds nothing a subprocess does not.
