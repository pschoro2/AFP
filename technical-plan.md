# Technical Plan (Initial Draft)

This document starts the implementation-oriented technical plan derived from `plan.md`.
It converts strategy into concrete delivery tracks, milestones, and first engineering tasks.

## 1) Planning Goals

- Turn the orchestrator vision into a staged build plan with explicit dependencies.
- Define implementation seams so multiple engineers/agents can work in parallel.
- Establish the minimum evidence and quality bars required to move between phases.

## 2) Delivery Tracks

We will execute across seven coordinated tracks.

1. **Platform Core**
   - Orchestrator API skeleton
   - Workflow engine and state transitions
   - Queue and scheduler integration

2. **Data and Persistence**
   - Postgres schema for runs/tasks/artefacts/executions
   - Artefact versioning and Git linkage
   - Audit and policy decision recording

3. **Agent Runtime**
   - Agent template registry and YAML loading
   - Runner abstraction and execution lifecycle
   - Pod/job execution contract

4. **Quality Gates and Policy**
   - Unit/integration/eval evidence ingestion
   - Policy engine rules and block conditions
   - Merge recommendation and enforcement flow

5. **Developer Workflow Integration**
   - Branch and PR workflow hooks
   - CI provider bridge (starting with one provider)
   - Check-state synchronization

6. **Operator UI**
   - Run list/detail pages
   - DAG and lifecycle visualizations
   - Approval queue and evidence viewer

7. **Observability and Operations**
   - Structured logging and trace correlation
   - Metrics for throughput/failure/retry
   - Runtime controls (pause/resume/retry/stop)

## 3) Target Architecture (Implementation View)

### Services

- `orchestrator-api`: external API and request validation.
- `workflow-engine`: canonical lifecycle transitions and gate evaluation.
- `agent-runner`: dispatch and monitor task executions.
- `policy-engine` (module first, service later): merge and gate decisions.
- `ci-bridge`: adapter to CI status and required checks.

### Infrastructure

- Redis for queueing and delayed retries.
- Postgres for run/task/policy/evidence metadata.
- Git-backed artefact store for generated documents and reports.
- Kubernetes jobs/pods for isolated task execution.

### Contract Boundaries

- API never mutates task state directly; it emits commands/events.
- Workflow engine is sole authority for canonical state changes.
- Agent runner writes candidate outcomes + evidence; workflow decides advancement.
- Policy engine reads evidence and returns allow/block with machine-readable reasons.

## 4) Milestones and Sequencing

## Milestone A — Core Workflow Skeleton

**Objective:** Persist runs/tasks and drive deterministic state transitions without real agents.

**Deliverables**
- Minimal API routes for run/task creation and state query.
- State machine implementation for nominal and failure side-states.
- Basic queue producer/consumer with retry metadata.
- Postgres migrations for core entities.

**Exit Criteria**
- Synthetic run progresses through stubbed states and survives restarts.

## Milestone B — Artefacts and Approvals

**Objective:** Introduce artefact storage, approval workflows, and blocked transitions.

**Deliverables**
- Artefact model + Git path/reference persistence.
- Approval request/decision API and workflow transitions.
- UI views for pending approvals and artefact inspection.

**Exit Criteria**
- Run cannot advance across gated states without required approval records.

## Milestone C — Planning Pipeline

**Objective:** Produce master plan DAG and task-plan documents from templates.

**Deliverables**
- Planner agent interfaces (stubbed model calls at first).
- DAG storage + dependency validation.
- Delegated task-plan template and renderer.

**Exit Criteria**
- Approved master plan produces executable task nodes with per-task plans.

## Milestone D — Execution + Unit Evidence

**Objective:** Execute scoped coding tasks in isolated jobs and ingest unit-test evidence.

**Deliverables**
- Runner-to-pod contract and manifest defaults.
- Structured execution result envelope and artefact capture.
- Unit-test evidence ingestion and required-gate checks.

**Exit Criteria**
- Workflow blocks completion when unit evidence is absent or invalid.

## Milestone E — PR Validation + Merge Policy

**Objective:** Add integration/eval gates and merge recommendation policy.

**Deliverables**
- CI bridge for status and required check ingestion.
- Eval result ingestion and acceptance-criteria mapping.
- Merge policy decision endpoint and rationale records.

**Exit Criteria**
- Merge recommendation is deterministic and fully evidence-backed.

## Milestone F — UX Hardening + Operations

**Objective:** Make system operable under concurrent runs and failure pressure.

**Deliverables**
- Live logs, failure heatmap, and retry controls.
- Role-sensitive approval actions.
- Operational metrics dashboards.

**Exit Criteria**
- Operators can manage multiple active runs without direct DB intervention.

## 5) First Backlog Slice (Next 2 Weeks)

### Epic 1: Canonical Data + State Machine

1. Define SQL schema for:
   - runs, tasks, task_dependencies, approvals,
   - artefacts, executions, logs, eval_runs, policy_decisions.
2. Implement lifecycle enum/state transition table.
3. Add validation helpers for legal transitions and reason codes.

### Epic 2: API + Queue Bootstrap

1. Scaffold API project with health, run create, run get, task list endpoints.
2. Integrate Redis queue with task enqueue + retry metadata.
3. Add worker loop that emits transition events to workflow engine.

### Epic 3: Artefact Persistence

1. Add artefact registration endpoint.
2. Persist path/checksum/version/producer metadata.
3. Support linking artefacts to run and task context.

### Epic 4: UI Shell

1. Scaffold run dashboard and run detail pages.
2. Add task state timeline component.
3. Add placeholder DAG panel with dependency list rendering.

## 6) Technical Decisions to Lock Early

- **Primary CI/Git provider for v1:** choose one first-class integration target.
- **Execution substrate:** Kubernetes Job vs alternative runner abstraction.
- **Schema migration tooling:** one migration workflow for all services.
- **Event model:** DB-led polling vs explicit event bus for workflow events.
- **Observability baseline:** structured log schema and correlation IDs.

## 7) Risks and Mitigations (Execution-Level)

- **State divergence across services**
  - Mitigation: enforce workflow engine as single writer for canonical states.
- **Non-reproducible task execution**
  - Mitigation: pinned images, immutable inputs, deterministic manifests.
- **Approval bypass through direct APIs**
  - Mitigation: policy checks in workflow transitions, not only UI controls.
- **Agent output schema drift**
  - Mitigation: strict schema validation + hard fail on malformed outputs.

## 8) Definition of Done for This Planning Stage

This initial technical planning stage is complete when:

1. Milestones A–F are accepted by stakeholders.
2. First backlog slice is imported into issue tracker with owners.
3. Core architecture decision log (ADR list) is created for open decisions.
4. Milestone A implementation begins from an agreed state-machine contract.

## 9) Immediate Next Actions

1. Convert this plan into tracked work items (epics + tasks).
2. Create ADR-001 for workflow state authority and event model.
3. Draft initial SQL migration for core tables.
4. Scaffold orchestrator API and workflow engine modules.
