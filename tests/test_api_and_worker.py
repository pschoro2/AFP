import unittest
from datetime import datetime, timezone
from uuid import uuid4

from agent_runner import InMemoryQueue, QueueEnvelope, worker_tick
from workflow_engine import LifecycleState

try:
    from orchestrator_api.app import TASKS, RUNS, app
except ModuleNotFoundError:  # pragma: no cover - environment dependency
    app = None
    TASKS = RUNS = None


@unittest.skipIf(app is None, "Flask is not installed in this environment")
class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        RUNS.clear()
        TASKS.clear()
        self.client = app.test_client()

    def test_create_run_and_fetch_tasks(self) -> None:
        create_response = self.client.post("/runs")
        self.assertEqual(create_response.status_code, 201)
        body = create_response.get_json()

        run_id = body["run"]["id"]
        self.assertEqual(body["run"]["state"], "new")
        self.assertEqual(len(body["tasks"]), 1)

        get_tasks_response = self.client.get(f"/runs/{run_id}/tasks")
        self.assertEqual(get_tasks_response.status_code, 200)
        tasks_body = get_tasks_response.get_json()
        self.assertEqual(len(tasks_body), 1)
        self.assertEqual(tasks_body[0]["run_id"], run_id)
        self.assertEqual(tasks_body[0]["state"], "ready")


class WorkerLoopTests(unittest.TestCase):
    def test_worker_tick_emits_transition_event(self) -> None:
        queue = InMemoryQueue()
        envelope = QueueEnvelope(
            task_id=uuid4(),
            run_id=uuid4(),
            retry_count=0,
            max_retries=3,
            reason="run_created",
            enqueued_at=datetime.now(timezone.utc),
        )
        queue.put(envelope)

        event, state = worker_tick(queue, LifecycleState.READY)

        self.assertIsNotNone(event)
        self.assertEqual(state, LifecycleState.IN_PROGRESS)
        assert event is not None
        self.assertEqual(event.status, "applied")
        self.assertEqual(event.reason_code, "ok")


if __name__ == "__main__":
    unittest.main()
