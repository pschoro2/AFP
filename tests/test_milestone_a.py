import unittest

from uuid import uuid4

from orchestrator_api.app import EVENTS, QUEUE, RUNS, TASKS, app
from workflow_engine import LifecycleState, QueueEnvelope, apply_transition


class MilestoneATests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        RUNS.clear()
        TASKS.clear()
        EVENTS.clear()
        while QUEUE.dequeue() is not None:
            pass

    def test_state_machine_rejects_illegal_transition(self):
        result = apply_transition(LifecycleState.NEW, LifecycleState.MERGED)
        self.assertFalse(result.valid)
        self.assertEqual(result.reason_code, "illegal_transition")

    def test_run_task_queue_and_worker_flow(self):
        run_resp = self.client.post("/runs", json={"title": "demo"})
        self.assertEqual(run_resp.status_code, 201)
        run_id = run_resp.get_json()["id"]

        task_resp = self.client.post(
            f"/runs/{run_id}/tasks",
            json={"name": "build", "max_retries": 2},
        )
        self.assertEqual(task_resp.status_code, 201)
        self.assertEqual(QUEUE.size(), 1)

        list_resp = self.client.get(f"/runs/{run_id}/tasks")
        self.assertEqual(list_resp.status_code, 200)
        tasks = list_resp.get_json()
        self.assertEqual(len(tasks), 1)

        drain_resp = self.client.post("/workers/drain-once")
        self.assertEqual(drain_resp.status_code, 200)
        self.assertEqual(drain_resp.get_json()["status"], "processed")
        self.assertEqual(QUEUE.size(), 0)

        events_resp = self.client.get("/workflow-events")
        self.assertEqual(events_resp.status_code, 200)
        events = events_resp.get_json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "task.execution.dequeued")

    def test_retry_envelope_next_attempt(self):
        envelope = QueueEnvelope(run_id=uuid4(), task_id=uuid4(), attempt=1, max_retries=3)
        second = envelope.next_attempt()
        self.assertEqual(second.attempt, 2)


if __name__ == "__main__":
    unittest.main()
