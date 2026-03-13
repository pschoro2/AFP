"""Minimal in-memory queue + worker loop for Milestone A bootstrap."""

from collections import deque
from dataclasses import dataclass
from typing import Callable

from .events import QueueEnvelope, WorkflowEvent


@dataclass
class InMemoryQueue:
    _items: deque[QueueEnvelope]

    def __init__(self) -> None:
        self._items = deque()

    def enqueue(self, envelope: QueueEnvelope) -> None:
        self._items.append(envelope)

    def dequeue(self) -> QueueEnvelope | None:
        if not self._items:
            return None

        return self._items.popleft()

    def size(self) -> int:
        return len(self._items)


def drain_worker_once(
    queue: InMemoryQueue,
    emit_event: Callable[[WorkflowEvent], None],
) -> WorkflowEvent | None:
    """Consume one queue message and emit a workflow transition event."""
    envelope = queue.dequeue()
    if envelope is None:
        return None

    event = WorkflowEvent(
        event_type="task.execution.dequeued",
        run_id=envelope.run_id,
        task_id=envelope.task_id,
        payload={
            "attempt": envelope.attempt,
            "max_retries": envelope.max_retries,
            "not_before_epoch_ms": envelope.not_before_epoch_ms,
        },
        idempotency_key=f"{envelope.task_id}:{envelope.attempt}",
    )
    emit_event(event)
    return event
