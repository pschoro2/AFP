# ADR-001: Workflow Engine as State Authority + DB-Led Event Model

- **Status:** Accepted
- **Date:** 2026-03-12
- **Deciders:** Platform Core, Data/Persistence
- **Related:** `technical-plan.md` section 6 and 9

## Context

The orchestrator requires deterministic, auditable state transitions across services (`orchestrator-api`, `workflow-engine`, `agent-runner`, `ci-bridge`).
Multiple components can observe or propose state changes, but a single source of truth is required to prevent divergence.

We must also choose an initial event propagation model to unblock Milestone A:

- Option A: explicit event bus first.
- Option B: DB-led polling/claiming first, with event bus optional later.

## Decision

1. **Workflow engine is the only writer of canonical lifecycle state.**
   - API and workers emit commands/events, never direct lifecycle mutation.
   - Canonical transition logic is centralized in workflow-engine transition table.

2. **Adopt DB-led event model for v1 bootstrap.**
   - Commands/events are written as records in Postgres (`workflow_events`).
   - Workflow engine polls/claims unprocessed events transactionally.
   - State transition + event processing marker are committed atomically.

3. **Event bus remains a future optimization path.**
   - Schema and envelopes will remain transport-agnostic to ease migration.

## Consequences

### Positive
- Deterministic transition authority and easier auditability.
- Fewer moving parts for Milestone A delivery.
- Simpler local development and failure recovery.

### Negative
- Higher DB load from polling during scale-up.
- Event latency bounded by poll interval.
- Requires careful indexing and claim semantics to avoid contention.

## Guardrails

- Transition function rejects illegal transitions with reason codes.
- Every transition stores actor, source event ID, and rationale.
- API cannot bypass workflow-engine transition path.
- Idempotency key required for externally-originated events.

## Follow-ups

- ADR-002: CI provider selection for v1.
- ADR-003: Kubernetes job contract for runner execution.
- ADR-004: Structured log and correlation ID schema.
