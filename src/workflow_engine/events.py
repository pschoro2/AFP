"""Workflow event contracts for DB-led event processing."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class WorkflowEvent:
    """Transport-agnostic event emitted by API/worker and consumed by workflow engine."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = "task.transition.requested"
    run_id: UUID | None = None
    task_id: UUID | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class QueueEnvelope:
    """Queue contract carrying retry metadata for task execution."""

    run_id: UUID
    task_id: UUID
    attempt: int = 1
    max_retries: int = 3
    not_before_epoch_ms: int | None = None

    def can_retry(self) -> bool:
        return self.attempt < self.max_retries

    def next_attempt(self) -> "QueueEnvelope":
        if not self.can_retry():
            raise ValueError("retry_limit_reached")

        return QueueEnvelope(
            run_id=self.run_id,
            task_id=self.task_id,
            attempt=self.attempt + 1,
            max_retries=self.max_retries,
            not_before_epoch_ms=self.not_before_epoch_ms,
        )
