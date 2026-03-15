"""Execution-policy checks for coding tasks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CodingTaskPolicyInput:
    required_skills: set[str]
    declared_skills: set[str]
    task_path: str
    agent_scope_root: str


def validate_coding_task_policy(inp: CodingTaskPolicyInput) -> list[str]:
    """Return reason codes for any policy violations."""
    violations: list[str] = []

    missing_skills = sorted(inp.required_skills - inp.declared_skills)
    if missing_skills:
        violations.append(f"missing_required_skills:{','.join(missing_skills)}")

    normalized_task = inp.task_path.rstrip("/")
    normalized_scope = inp.agent_scope_root.rstrip("/")
    if normalized_scope and not normalized_task.startswith(normalized_scope):
        violations.append("agent_scope_violation")

    return violations
