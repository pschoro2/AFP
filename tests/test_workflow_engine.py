import unittest
from uuid import uuid4

from workflow_engine import InMemoryQueue, LifecycleState, QueueEnvelope, apply_transition, drain_worker_once


class WorkflowEngineTests(unittest.TestCase):
    def test_valid_and_invalid_transitions(self):
        ok = apply_transition(LifecycleState.NEW, LifecycleState.ENRICHED)
        bad = apply_transition(LifecycleState.NEW, LifecycleState.MERGED)
        self.assertTrue(ok.valid)
        self.assertEqual(ok.reason_code, "ok")
        self.assertFalse(bad.valid)
        self.assertEqual(bad.reason_code, "illegal_transition")

    def test_queue_drain_emits_event(self):
        queue = InMemoryQueue()
        events = []
        envelope = QueueEnvelope(run_id=uuid4(), task_id=uuid4(), max_retries=4)
        queue.enqueue(envelope)

        event = drain_worker_once(queue, events.append)
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, "task.execution.dequeued")
        self.assertEqual(event.payload["attempt"], 1)
        self.assertEqual(queue.size(), 0)
        self.assertEqual(len(events), 1)


if __name__ == "__main__":
    unittest.main()
