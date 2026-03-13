"""Minimal API scaffold for Milestone A/B bootstrap work."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from flask import Flask, jsonify

from agent_runner import InMemoryQueue, QueueEnvelope
from workflow_engine import LifecycleState


@dataclass
class Run:
    id: UUID
    title: str
    state: LifecycleState


@dataclass
class Task:
    id: UUID
    run_id: UUID
    name: str
    state: LifecycleState
    retry_count: int = 0
    max_retries: int = 3


app = Flask(__name__)
RUNS: dict[str, Run] = {}
TASKS: dict[str, Task] = {}
TASK_QUEUE = InMemoryQueue()


def _serialize_run(run: Run) -> dict[str, str]:
    payload = asdict(run)
    payload["id"] = str(payload["id"])
    payload["state"] = payload["state"].value
    return payload


def _serialize_task(task: Task) -> dict[str, str | int]:
    payload = asdict(task)
    payload["id"] = str(payload["id"])
    payload["run_id"] = str(payload["run_id"])
    payload["state"] = payload["state"].value
    return payload


def _enqueue_task(task: Task, reason: str) -> QueueEnvelope:
    envelope = QueueEnvelope(
        task_id=task.id,
        run_id=task.run_id,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
        reason=reason,
        enqueued_at=datetime.now(timezone.utc),
    )
    TASK_QUEUE.put(envelope)
    return envelope


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.post("/runs")
def create_run() -> tuple[dict[str, str | list[dict[str, str | int]]], int]:
    run_id = uuid4()
    run = Run(id=run_id, title="seed-run", state=LifecycleState.NEW)
    RUNS[str(run_id)] = run

    task = Task(id=uuid4(), run_id=run_id, name="bootstrap-task", state=LifecycleState.READY)
    TASKS[str(task.id)] = task
    _enqueue_task(task, reason="run_created")

    return {
        "run": _serialize_run(run),
        "tasks": [_serialize_task(task)],
    }, 201


@app.get("/runs/<run_id>")
def get_run(run_id: str):
    run = RUNS.get(run_id)
    if run is None:
        return jsonify({"error": "not_found"}), 404

    return jsonify(_serialize_run(run)), 200


@app.get("/runs/<run_id>/tasks")
def get_run_tasks(run_id: str):
    run = RUNS.get(run_id)
    if run is None:
        return jsonify({"error": "not_found"}), 404

    tasks = [task for task in TASKS.values() if str(task.run_id) == run_id]
    return jsonify({"run_id": run_id, "tasks": [_serialize_task(task) for task in tasks]}), 200
