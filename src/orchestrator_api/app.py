"""Minimal API scaffold for Milestone A."""

from dataclasses import asdict, dataclass
from uuid import UUID, uuid4

from flask import Flask, jsonify

from workflow_engine import LifecycleState


@dataclass
class Run:
    id: UUID
    title: str
    state: LifecycleState


app = Flask(__name__)
RUNS: dict[str, Run] = {}


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.post("/runs")
def create_run() -> tuple[dict[str, str], int]:
    run_id = uuid4()
    run = Run(id=run_id, title="seed-run", state=LifecycleState.NEW)
    RUNS[str(run_id)] = run
    payload = asdict(run)
    payload["id"] = str(payload["id"])
    payload["state"] = payload["state"].value
    return payload, 201


@app.get("/runs/<run_id>")
def get_run(run_id: str):
    run = RUNS.get(run_id)
    if run is None:
        return jsonify({"error": "not_found"}), 404

    payload = asdict(run)
    payload["id"] = str(payload["id"])
    payload["state"] = payload["state"].value
    return jsonify(payload), 200
