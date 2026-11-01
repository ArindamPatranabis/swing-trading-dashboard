# ADR-012: Momentum's two screens become two modules

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | Spec 3 vs Screen A |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** The PRD treats Momentum as one module with two screens. But Screen A (Spec 3) runs on daily bars and Screen B (Spec 4) on completed weekly bars, they have separate specs, and Spec 3 still differs from PRD Screen A (open question Q1 in Spec 3).

**Decision.** Build `momentum_rs_rsi` and `momentum_rs_ichimoku` as separate modules with their own cadence, cache keys, versions and tests. The dashboard still shows them as two tabs in one Momentum section.

**Consequences.** Resolving Spec 3's open question, or rewriting either screen, touches one package. Shared indicator code (RS ratio, ATR) is duplicated in each or moved into the contract library only if it is pure and stable.

**Alternatives rejected.** One module with two screens: a change to one screen re-versions and re-tests the other.
