"""Minimal API scaffold for Milestone A/B bootstrap work."""

from dataclasses import asdict, dataclass
from uuid import UUID, uuid4

try:  # pragma: no cover - exercised indirectly in environments with Flask
    from flask import Flask, jsonify, request
except ModuleNotFoundError:  # pragma: no cover - lightweight test fallback
    class _Request:
        def __init__(self) -> None:
            self._json: dict | None = None

        def get_json(self, silent: bool = False):
            return self._json

    request = _Request()

    class _Response:
        def __init__(self, payload, status_code: int):
            self._payload = payload
            self.status_code = status_code

        def get_json(self):
            return self._payload

    def jsonify(payload):
        return payload

    class Flask:
        def __init__(self, name: str):
            self._routes: dict[tuple[str, str], tuple[str, object]] = {}

        def get(self, path: str):
            return self._register("GET", path)

        def post(self, path: str):
            return self._register("POST", path)

        def _register(self, method: str, path: str):
            def decorator(func):
                self._routes[(method, path)] = (path, func)
                return func

            return decorator

        def _match(self, method: str, req_path: str):
            for (m, pattern), (_, func) in self._routes.items():
                if m != method:
                    continue

                p_parts = pattern.strip("/").split("/")
                r_parts = req_path.strip("/").split("/")
                if len(p_parts) != len(r_parts):
                    continue

                args: list[str] = []
                matched = True
                for p, r in zip(p_parts, r_parts):
                    if p.startswith("<") and p.endswith(">"):
                        args.append(r)
                    elif p != r:
                        matched = False
                        break

                if matched:
                    return func, args
            return None, []

        def test_client(self):
            app = self

            class _Client:
                def _call(self, method: str, path: str, json=None):
                    request._json = json
                    func, args = app._match(method, path)
                    if func is None:
                        return _Response({"error": "not_found"}, 404)
                    response = func(*args)
                    if isinstance(response, tuple) and len(response) == 2:
                        payload, status = response
                    else:
                        payload, status = response, 200
                    return _Response(payload, status)

                def get(self, path: str):
                    return self._call("GET", path)

                def post(self, path: str, json=None):
                    return self._call("POST", path, json=json)

            return _Client()


from workflow_engine import LifecycleState, QueueEnvelope, WorkflowEvent, drain_worker_once
from workflow_engine.worker import InMemoryQueue



@dataclass
class Artefact:
    id: UUID
    run_id: UUID
    task_id: UUID | None
    path: str
    checksum: str | None
    version: str | None
    producer: str
    metadata: dict

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
ARTEFACTS: dict[str, Artefact] = {}
EVENTS: list[WorkflowEvent] = []
QUEUE = InMemoryQueue()


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


def _serialize_artefact(artefact: Artefact) -> dict:
    return {
        "id": str(artefact.id),
        "run_id": str(artefact.run_id),
        "task_id": str(artefact.task_id) if artefact.task_id else None,
        "path": artefact.path,
        "checksum": artefact.checksum,
        "version": artefact.version,
        "producer": artefact.producer,
        "metadata": artefact.metadata,
    }


def _serialize_event(event: WorkflowEvent) -> dict[str, str | dict[str, int | None]]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "run_id": str(event.run_id) if event.run_id else None,
        "task_id": str(event.task_id) if event.task_id else None,
        "payload": event.payload,
        "idempotency_key": event.idempotency_key,
        "created_at": event.created_at.isoformat(),
    }


def _enqueue_task(task: Task) -> QueueEnvelope:
    envelope = QueueEnvelope(
        task_id=task.id,
        run_id=task.run_id,
        attempt=task.retry_count + 1,
        max_retries=task.max_retries,
    )
    QUEUE.enqueue(envelope)
    return envelope


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.post("/runs")
def create_run():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title", "untitled-run")

    run_id = uuid4()
    run = Run(id=run_id, title=title, state=LifecycleState.NEW)
    RUNS[str(run_id)] = run

    task_preview = Task(id=uuid4(), run_id=run_id, name="bootstrap-task", state=LifecycleState.READY)
    TASKS[str(task_preview.id)] = task_preview

    run_payload = _serialize_run(run)
    task_payload = _serialize_task(task_preview)
    return jsonify({"id": run_payload["id"], "run": run_payload, "tasks": [task_payload]}), 201


@app.get("/runs/<run_id>")
def get_run(run_id: str):
    run = RUNS.get(run_id)
    if run is None:
        return jsonify({"error": "not_found"}), 404

    return jsonify(_serialize_run(run)), 200


@app.post("/runs/<run_id>/tasks")
def create_task(run_id: str):
    run = RUNS.get(run_id)
    if run is None:
        return jsonify({"error": "not_found"}), 404

    payload = request.get_json(silent=True) or {}
    task = Task(
        id=uuid4(),
        run_id=run.id,
        name=payload.get("name", "unnamed-task"),
        state=LifecycleState.READY,
        max_retries=int(payload.get("max_retries", 3)),
    )
    TASKS[str(task.id)] = task
    _enqueue_task(task)

    return jsonify(_serialize_task(task)), 201


@app.get("/runs/<run_id>/tasks")
def get_run_tasks(run_id: str):
    run = RUNS.get(run_id)
    if run is None:
        return jsonify({"error": "not_found"}), 404

    tasks = [task for task in TASKS.values() if str(task.run_id) == run_id]
    payload = [_serialize_task(task) for task in tasks]
    return jsonify(payload), 200


@app.post("/workers/drain-once")
def workers_drain_once():
    event = drain_worker_once(QUEUE, EVENTS.append)
    if event is None:
        return jsonify({"status": "idle"}), 200

    return jsonify({"status": "processed", "event_id": event.event_id}), 200


@app.post("/artefacts")
def create_artefact():
    payload = request.get_json(silent=True) or {}
    run_id = payload.get("run_id")
    if run_id is None or run_id not in RUNS:
        return jsonify({"error": "run_not_found"}), 404

    task_id = payload.get("task_id")
    if task_id is not None and task_id not in TASKS:
        return jsonify({"error": "task_not_found"}), 404

    artefact = Artefact(
        id=uuid4(),
        run_id=UUID(run_id),
        task_id=UUID(task_id) if task_id else None,
        path=str(payload.get("path", "")),
        checksum=payload.get("checksum"),
        version=payload.get("version"),
        producer=str(payload.get("producer", "unknown")),
        metadata=payload.get("metadata", {}),
    )
    ARTEFACTS[str(artefact.id)] = artefact
    return jsonify(_serialize_artefact(artefact)), 201


@app.get("/runs/<run_id>/artefacts")
def get_run_artefacts(run_id: str):
    if run_id not in RUNS:
        return jsonify({"error": "not_found"}), 404

    task_id = (request.get_json(silent=True) or {}).get("task_id") if hasattr(request, "get_json") else None
    artefacts = [a for a in ARTEFACTS.values() if str(a.run_id) == run_id]
    if task_id:
        artefacts = [a for a in artefacts if str(a.task_id) == task_id]

    return jsonify([_serialize_artefact(a) for a in artefacts]), 200


@app.get("/workflow-events")
def workflow_events():
    return jsonify([_serialize_event(evt) for evt in EVENTS]), 200
