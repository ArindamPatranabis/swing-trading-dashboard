# ADR-007: No LLM in the core; AI narrator is an opt-in plugin

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | Constraint 3 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** `requirements.txt` pins the `anthropic` SDK, yet the AI features (AI-FR-01 to 03) are "Could" items for v0.3, and constraint 3 says the system must run without any LLM.

**Decision.** The core install (`stdash` plus every module, adapter and view) contains no LLM SDK and makes no LLM calls. The bottom-of-page summary is built by the `summary` view from templates over contract fields, for example a line naming the regime, how many stocks each screen returned and the next high-impact release. "Why flagged" notes are built from the `rules_passed` list each row already carries. The AI narrator is a separate package (`stdash[ai]`), off by default, run as its own service, reading contract JSON only, behind a provider-neutral interface. Its text is shown only if the grounding check passes (every number exists in module outputs); otherwise the template summary is shown.

**Consequences.** Running cost is $0 by default. AI-FR-02 is met without AI. Removing the narrator changes nothing else.

**Alternatives rejected.** Keeping the SDK in core with a feature flag: the dependency, its updates and the temptation to use it stay in every module's environment.
