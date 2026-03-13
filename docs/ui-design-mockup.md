# UI Design Mockup — Agent Workflow Orchestrator

## Source Alignment
This mockup is grounded in the workflow and backlog documentation:
- End-to-end lifecycle and HITL checkpoints from `docs/plan.md`
- Milestone/UI shell goals from `docs/technical-plan.md` and `docs/work-items.md`
- State-authority model from `docs/adrs/ADR-001-workflow-state-authority-and-event-model.md`

## Screen 1: Run Dashboard (Operator Home)

### Purpose
Provide a high-signal control surface to start, monitor, pause, and inspect workflow runs.

### Layout (wireframe)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Top Nav: [Orchestrator] [Runs] [Approvals] [Artefacts] [Policies] [Profile]│
├──────────────────────────────────────────────────────────────────────────────┤
│ Header: Runs Dashboard                     [ + New Run ] [ Filter ▾ ]       │
│ Subheader: "Deterministic workflow control and approval visibility"         │
├──────────────────────────────────────────────────────────────────────────────┤
│ KPI Row                                                                      │
│ ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────────────┐ │
│ │ Active Runs │ │ Awaiting HITL│ │ Blocked Runs │ │ Merge-Ready This Week │ │
│ │ 12          │ │ 4            │ │ 2            │ │ 7                     │ │
│ └─────────────┘ └──────────────┘ └──────────────┘ └───────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│ Main Grid                                                                     │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ Run List Table                                                           │ │
│ │ ID      Branch     Stage          Approval     Risk     Updated   Action │ │
│ │ R-318   feat/e1    Master Plan    Pending      Medium   2m ago    View   │ │
│ │ R-317   feat/e2    Execution      Approved     Low      6m ago    View   │ │
│ │ R-316   hotfix/a   PR Validation  Blocked      High     11m ago   View   │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ ┌──────────────────────────┐  ┌───────────────────────────────────────────┐ │
│ │ Queue/Worker Health      │  │ Approval Inbox                            │ │
│ │ - runner-1 healthy       │  │ - R-318 Architecture sign-off (P1)        │ │
│ │ - runner-2 retrying      │  │ - R-320 Delegated Plan approval (P2)      │ │
│ │ - redis depth: 24        │  │ [Review all]                               │ │
│ └──────────────────────────┘  └───────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Screen 2: Run Detail (Primary Validation View)

### Purpose
Expose state timeline, DAG dependencies, logs, artefacts, and gate evidence in one place.

### Layout (wireframe)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Breadcrumb: Runs / R-318                                                     │
│ Title: Run R-318 — "Milestone A bootstrap"                                  │
│ Status: IN_PROGRESS  Risk: MEDIUM  Owner: platform-core                      │
│ Actions: [Pause] [Stop] [Retry Failed] [Open PR]                             │
├──────────────────────────────────────────────────────────────────────────────┤
│ Left (70%)                                         │ Right (30%)             │
│ ┌───────────────────────────────────────────────┐  │ ┌──────────────────────┐│
│ │ Stage Timeline                               │  │ │ Approval Panel       ││
│ │ Enrichment ✓ -> Architecture ✓ -> Planning ✓ │  │ │ Current Gate: HITL   ││
│ │ -> Delegated Plan ✓ -> Execution ⏳          │  │ │ Needed from: Lead Eng││
│ └───────────────────────────────────────────────┘  │ │ [Approve] [Request ..]││
│ ┌───────────────────────────────────────────────┐  │ └──────────────────────┘│
│ │ Dependency DAG Panel                          │  │ ┌──────────────────────┐│
│ │ [E1-T1]──>[E1-T4]──>[E2-T2]                   │  │ │ Policy/Gate Summary  ││
│ │    └────>[E1-T5]                              │  │ │ Unit tests: PASS     ││
│ │ [E1-T2]──>[E2-T4]                             │  │ │ Integration: PENDING ││
│ └───────────────────────────────────────────────┘  │ │ Eval suite: PENDING  ││
│ ┌───────────────────────────────────────────────┐  │ └──────────────────────┘│
│ │ Logs (stream + filter)                        │  │ ┌──────────────────────┐│
│ │ [time] [agent] [state event] [reason code]    │  │ │ Artefact Links       ││
│ │ 10:42 executor STATE=RUNNING                  │  │ │ req.md               ││
│ │ 10:43 executor TEST_PASS count=27             │  │ │ arch.md              ││
│ │ 10:44 qa NEEDS_HUMAN reason=CI_PIPELINE_WAIT  │  │ │ plan-master.md       ││
│ └───────────────────────────────────────────────┘  │ │ test-report.xml      ││
│                                                    │ └──────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
```

## Visual Language

### Color semantics
- `RUNNING`: blue
- `PENDING_APPROVAL`: amber
- `BLOCKED`: red
- `PASSED`: green
- `NEEDS_HUMAN`: purple

### Component patterns
- Dense table for run scanning.
- Expandable timeline for stage-level details.
- DAG panel with node status chips and edge-direction arrows.
- Log viewer with correlation-id filter and reason-code badges.
- Sticky approval/policy side panel for immediate gate decisions.

## UX Rules (Derived from System Principles)
- Never hide blocked state causes; always show reason code + source event.
- Approval-required transitions must have explicit call-to-action and actor list.
- Test/eval evidence must be visible above fold before merge recommendation.
- Every state mutation shown in UI must map to a canonical workflow event.

## Suggested First Implementation Slice
1. Dashboard shell with mocked KPI cards and run table.
2. Run detail shell with timeline and DAG placeholders.
3. Approval side panel with action buttons (non-functional in v1 shell).
4. Read-only artefact list and log stream placeholder blocks.

## Validation Checklist
- Does dashboard expose pending approvals clearly enough?
- Is timeline readable for non-authors reviewing a run?
- Is DAG useful at this fidelity, or should we start with a dependency list?
- Are policy/test gates visually distinct and unambiguous?
- Should approval panel remain sticky while scrolling logs?
