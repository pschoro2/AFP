"""In-memory worker loop that emits workflow events for queued tasks."""

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from workflow_engine import LifecycleState, apply_transition


@dataclass
class QueueEnvelope:
    task_id: UUID
    run_id: UUID
    retry_count: int
    max_retries: int
    reason: str
    enqueued_at: datetime


@dataclass
class WorkflowEvent:
    event_type: str
    run_id: UUID
    task_id: UUID
    status: str
    reason_code: str
    emitted_at: datetime


class InMemoryQueue:
    """Minimal queue facade used to bootstrap worker behavior in Milestone A."""

    def __init__(self) -> None:
        self._items: deque[QueueEnvelope] = deque()

    def put(self, envelope: QueueEnvelope) -> None:
        self._items.append(envelope)

    def get(self) -> QueueEnvelope | None:
        if not self._items:
            return None
        return self._items.popleft()


def worker_tick(queue: InMemoryQueue, task_state: LifecycleState) -> tuple[WorkflowEvent | None, LifecycleState]:
    """Consume one queue item and emit a workflow transition event."""
    envelope = queue.get()
    if envelope is None:
        return None, task_state

    transition = apply_transition(task_state, LifecycleState.IN_PROGRESS)
    next_state = LifecycleState.IN_PROGRESS if transition.valid else task_state
    event = WorkflowEvent(
        event_type="task.transition_attempted",
        run_id=envelope.run_id,
        task_id=envelope.task_id,
        status="applied" if transition.valid else "rejected",
        reason_code=transition.reason_code,
        emitted_at=datetime.now(timezone.utc),
    )
    return event, next_state
