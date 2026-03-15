import unittest
from uuid import uuid4

from workflow_engine import (
    CodingTaskPolicyInput,
    InMemoryQueue,
    QueueEnvelope,
    validate_coding_task_policy,
)


class ExecutionPolicyTests(unittest.TestCase):
    def test_policy_rejects_missing_skills_and_scope_violation(self):
        violations = validate_coding_task_policy(
            CodingTaskPolicyInput(
                required_skills={"python", "testing"},
                declared_skills={"python"},
                task_path="/workspace/AFP/src/orchestrator_api/app.py",
                agent_scope_root="/workspace/AFP/docs",
            )
        )

        self.assertIn("missing_required_skills:testing", violations)
        self.assertIn("agent_scope_violation", violations)

    def test_policy_allows_required_skills_within_scope(self):
        violations = validate_coding_task_policy(
            CodingTaskPolicyInput(
                required_skills={"python", "testing"},
                declared_skills={"python", "testing"},
                task_path="/workspace/AFP/src/workflow_engine/state_machine.py",
                agent_scope_root="/workspace/AFP/src",
            )
        )

        self.assertEqual(violations, [])


class QueueRecoveryTests(unittest.TestCase):
    def test_queue_supports_restart_recovery_from_persisted_envelopes(self):
        persisted = [
            QueueEnvelope(run_id=uuid4(), task_id=uuid4(), attempt=1, max_retries=3),
            QueueEnvelope(run_id=uuid4(), task_id=uuid4(), attempt=2, max_retries=3),
        ]

        restored_queue = InMemoryQueue()
        for env in persisted:
            restored_queue.enqueue(env)

        first = restored_queue.dequeue()
        second = restored_queue.dequeue()
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertEqual(first.task_id, persisted[0].task_id)
        self.assertEqual(second.task_id, persisted[1].task_id)


if __name__ == "__main__":
    unittest.main()
