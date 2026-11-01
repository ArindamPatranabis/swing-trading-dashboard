# ADR-002: Where microservices are used

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | Constraint 4 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** Constraint 4 asks for microservices where required. Services add ports, start-up order and failure modes, so the bar should be explicit.

**Decision.** A unit becomes a network service only if it (a) must stay running to answer requests, (b) must be deployed or hosted apart from the owner's PC, or (c) holds a dependency or secret that must be kept out of the core. In v1.0 two units qualify: `dashboard_api` (rule a) and the optional `ai_narrator` (rule c: it alone holds an LLM SDK and key). Every other unit is a worker. Because workers share one contract, the library ships a generic `stdash serve <module>` shim that wraps any worker in HTTP if a later need meets the rule, for example hosting one module on a free serverless tier.

**Consequences.** Two processes run while the dashboard is open, not twelve. Promotion is a deployment change, not a rewrite.

**Alternatives rejected.** Full microservices from day one: operational load with no single-user benefit. A pure monolith: breaks constraint 1 and PLAT-FR-03.
