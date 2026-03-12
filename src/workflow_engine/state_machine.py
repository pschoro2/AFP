"""Canonical lifecycle transition rules for orchestrator tasks/runs."""

from dataclasses import dataclass
from enum import Enum


class LifecycleState(str, Enum):
    NEW = "new"
    ENRICHED = "enriched"
    PLANNED = "planned"
    AWAITING_APPROVAL = "awaiting_approval"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    UNIT_PASS = "unit_pass"
    PR_OPEN = "pr_open"
    INTEGRATION_PASS = "integration_pass"
    MERGED = "merged"
    BLOCKED = "blocked"
    FAILED = "failed"
    NEEDS_HUMAN = "needs_human"
    CANCELLED = "cancelled"


ALLOWED_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.NEW: {LifecycleState.ENRICHED, LifecycleState.CANCELLED},
    LifecycleState.ENRICHED: {LifecycleState.PLANNED, LifecycleState.BLOCKED, LifecycleState.NEEDS_HUMAN},
    LifecycleState.PLANNED: {LifecycleState.AWAITING_APPROVAL, LifecycleState.BLOCKED},
    LifecycleState.AWAITING_APPROVAL: {LifecycleState.READY, LifecycleState.NEEDS_HUMAN, LifecycleState.CANCELLED},
    LifecycleState.READY: {LifecycleState.IN_PROGRESS, LifecycleState.CANCELLED},
    LifecycleState.IN_PROGRESS: {LifecycleState.UNIT_PASS, LifecycleState.FAILED, LifecycleState.BLOCKED},
    LifecycleState.UNIT_PASS: {LifecycleState.PR_OPEN, LifecycleState.FAILED},
    LifecycleState.PR_OPEN: {LifecycleState.INTEGRATION_PASS, LifecycleState.FAILED},
    LifecycleState.INTEGRATION_PASS: {LifecycleState.MERGED, LifecycleState.FAILED},
    LifecycleState.MERGED: set(),
    LifecycleState.BLOCKED: {LifecycleState.NEEDS_HUMAN, LifecycleState.READY, LifecycleState.CANCELLED},
    LifecycleState.FAILED: {LifecycleState.READY, LifecycleState.CANCELLED},
    LifecycleState.NEEDS_HUMAN: {LifecycleState.READY, LifecycleState.CANCELLED},
    LifecycleState.CANCELLED: set(),
}


@dataclass(frozen=True)
class TransitionResult:
    valid: bool
    from_state: LifecycleState
    to_state: LifecycleState
    reason_code: str


def apply_transition(from_state: LifecycleState, to_state: LifecycleState) -> TransitionResult:
    if to_state in ALLOWED_TRANSITIONS[from_state]:
        return TransitionResult(True, from_state, to_state, "ok")

    if from_state == to_state:
        return TransitionResult(False, from_state, to_state, "no_op_transition_forbidden")

    if not ALLOWED_TRANSITIONS[from_state]:
        return TransitionResult(False, from_state, to_state, "terminal_state")

    return TransitionResult(False, from_state, to_state, "illegal_transition")
