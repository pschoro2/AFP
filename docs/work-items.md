# Work Items Backlog (Seed)

This backlog operationalizes `technical-plan.md` into trackable epics and tasks.

## Epic E1 — Canonical Data + State Machine

### Goal
Establish deterministic workflow persistence and transition authority.

### Tasks
- [ ] E1-T1 Define schema for `runs`, `tasks`, `task_dependencies`.
- [ ] E1-T2 Define schema for `approvals`, `artefacts`, `executions`.
- [ ] E1-T3 Define schema for `logs`, `eval_runs`, `policy_decisions`.
- [ ] E1-T4 Implement lifecycle enum and transition map in workflow engine.
- [ ] E1-T5 Implement transition validator with machine-readable reason codes.
- [ ] E1-T6 Add restart-recovery scenario test for synthetic run progression.

### Dependencies
- None (foundation epic).

### Exit Criteria
- Synthetic run can move through allowed states and rejects invalid transitions.

## Epic E2 — API + Queue Bootstrap

### Goal
Expose minimum control plane and async task dispatch surface.

### Tasks
- [ ] E2-T1 Scaffold API service and health endpoint.
- [ ] E2-T2 Add `POST /runs` and `GET /runs/{run_id}` endpoints.
- [ ] E2-T3 Add `GET /runs/{run_id}/tasks` endpoint.
- [ ] E2-T4 Add queue envelope schema including retry metadata.
- [ ] E2-T5 Add worker loop that emits transition events to workflow engine.

### Dependencies
- Depends on E1 transition contracts and schema.

### Exit Criteria
- API can create run/task records and queue tasks for workflow processing.

## Epic E3 — Artefact Persistence

### Goal
Persist auditable artefact metadata linked to run/task lifecycle.

### Tasks
- [ ] E3-T1 Add artefact registration endpoint.
- [ ] E3-T2 Persist path/checksum/version/producer metadata.
- [ ] E3-T3 Link artefacts to run/task context.
- [ ] E3-T4 Add retrieval query for artefacts by run and task.

### Dependencies
- Depends on E1 core schema.

### Exit Criteria
- Artefacts can be registered and retrieved with deterministic lineage.

## Epic E4 — UI Shell

### Goal
Deliver first operator-facing workflow visibility surface.

### Tasks
- [ ] E4-T1 Scaffold run dashboard shell.
- [ ] E4-T2 Add run detail page shell.
- [ ] E4-T3 Add task state timeline component placeholder.
- [ ] E4-T4 Add DAG panel placeholder rendering dependency list.

### Dependencies
- Depends on E2 API surfaces for minimal data contracts.

### Exit Criteria
- Operator can navigate dashboard -> run detail and inspect placeholder state views.

## Milestone Alignment

- Milestone A: E1 + E2
- Milestone B: E3 (+ approvals in E1/E2 follow-up)
- Milestone F (early UI): E4 shell

## Ownership Proposal

- Platform Core: E1, E2
- Data/Persistence: E1, E3
- UI: E4
- Ops/Policy (future): Milestones D/E/F follow-up epics
