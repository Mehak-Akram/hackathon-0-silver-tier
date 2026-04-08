"""
Ralph Wiggum Loop - Autonomous Task Execution Pattern.

Implements the Plan → Execute → Reflect → Retry pattern for autonomous
multi-step task execution with error recovery and escalation.

Named after the Ralph Wiggum Loop pattern for autonomous reasoning.
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from src.retry_logic import with_retry, MCP_RETRY_CONFIG

logger = get_logger(__name__, "ralph-loop.log")


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class ExecutionStep:
    """Represents a single execution step in a multi-step task."""

    def __init__(self, step_id: int, description: str, action: str, parameters: Dict[str, Any]):
        """
        Initialize execution step.

        Args:
            step_id: Step identifier
            description: Human-readable description
            action: Action to execute (e.g., "create_invoice", "send_email")
            parameters: Action parameters
        """
        self.step_id = step_id
        self.description = description
        self.action = action
        self.parameters = parameters
        self.status = TaskStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "action": self.action,
            "parameters": self.parameters,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Task:
    """Represents a multi-step task for autonomous execution."""

    def __init__(self, task_id: str, description: str, domain: str = "general"):
        """
        Initialize task.

        Args:
            task_id: Unique task identifier
            description: Task description
            domain: Task domain (personal/business/accounting/marketing)
        """
        self.task_id = task_id
        self.description = description
        self.domain = domain
        self.status = TaskStatus.PENDING
        self.steps: List[ExecutionStep] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None

    def add_step(self, description: str, action: str, parameters: Dict[str, Any]) -> ExecutionStep:
        """Add execution step to task."""
        step = ExecutionStep(
            step_id=len(self.steps) + 1,
            description=description,
            action=action,
            parameters=parameters
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "domain": self.domain,
            "status": self.status.value,
            "steps": [step.to_dict() for step in self.steps],
            "execution_history": self.execution_history,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }


class RalphWiggumLoop:
    """
    Ralph Wiggum Loop - Autonomous Task Executor.

    Implements Plan → Execute → Reflect → Retry pattern for autonomous
    multi-step task execution.
    """

    def __init__(self, mcp_client=None):
        """
        Initialize Ralph Wiggum Loop.

        Args:
            mcp_client: MCP client for executing actions
        """
        self.mcp_client = mcp_client
        self.active_tasks: Dict[str, Task] = {}
        self.vault_path = Path("E:/AI_Employee_Vault")
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.pending_approval_path.mkdir(exist_ok=True)

        logger.info("Ralph Wiggum Loop initialized")

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute task using Plan → Execute → Reflect → Retry pattern.

        Args:
            task: Task to execute

        Returns:
            Execution result
        """
        try:
            logger.info(f"Starting task execution: {task.task_id} - {task.description}")

            task.status = TaskStatus.PLANNING
            task.started_at = datetime.now()
            self.active_tasks[task.task_id] = task

            # PLAN: Break down task into steps (already done during task creation)
            await self._plan_phase(task)

            # EXECUTE: Execute each step
            task.status = TaskStatus.EXECUTING
            for step in task.steps:
                step_result = await self._execute_step(task, step)

                # REFLECT: Analyze step result
                reflection = await self._reflect_phase(task, step, step_result)

                # RETRY: If step failed and retries available
                if not step_result.get("success") and step.retry_count < step.max_retries:
                    task.status = TaskStatus.RETRYING
                    logger.info(f"Retrying step {step.step_id}: {step.description}")
                    step.retry_count += 1

                    # Retry with adjusted parameters if needed
                    adjusted_params = await self._adjust_parameters(step, step_result)
                    if adjusted_params:
                        step.parameters = adjusted_params

                    step_result = await self._execute_step(task, step)
                    reflection = await self._reflect_phase(task, step, step_result)

                # If step still failed after retries, escalate
                if not step_result.get("success"):
                    logger.error(f"Step {step.step_id} failed after {step.retry_count} retries")
                    task.status = TaskStatus.FAILED
                    task.error = f"Step {step.step_id} failed: {step.error}"
                    await self._escalate_task(task)
                    return task.to_dict()

            # All steps completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()

            logger.info(f"Task completed successfully: {task.task_id}")

            return task.to_dict()

        except Exception as e:
            logger.error(f"Task execution error: {e}", exc_info=True)
            task.status = TaskStatus.FAILED
            task.error = str(e)
            await self._escalate_task(task)
            return task.to_dict()

        finally:
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

    async def _plan_phase(self, task: Task) -> None:
        """
        PLAN phase: Validate task plan and steps.

        Args:
            task: Task to plan
        """
        logger.info(f"Planning task: {task.task_id}")

        # Log plan
        task.execution_history.append({
            "phase": "plan",
            "timestamp": datetime.now().isoformat(),
            "steps_count": len(task.steps),
            "steps": [{"id": s.step_id, "description": s.description} for s in task.steps]
        })

        logger.info(f"Task plan created with {len(task.steps)} steps")

    async def _execute_step(self, task: Task, step: ExecutionStep) -> Dict[str, Any]:
        """
        EXECUTE phase: Execute a single step.

        Args:
            task: Parent task
            step: Step to execute

        Returns:
            Execution result
        """
        logger.info(f"Executing step {step.step_id}: {step.description}")

        step.status = TaskStatus.EXECUTING
        step.started_at = datetime.now()

        try:
            # Execute action via MCP client
            if self.mcp_client:
                result = await self._call_mcp_action(step.action, step.parameters)
            else:
                # Simulated execution for testing
                result = {
                    "success": True,
                    "message": f"Simulated execution of {step.action}",
                    "timestamp": datetime.now().isoformat()
                }

            step.result = result
            step.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            step.completed_at = datetime.now()

            if not result.get("success"):
                step.error = result.get("message", "Unknown error")

            logger.info(f"Step {step.step_id} completed: success={result.get('success')}")

            return result

        except Exception as e:
            logger.error(f"Step {step.step_id} execution error: {e}", exc_info=True)
            step.status = TaskStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()

            return {
                "success": False,
                "error": "EXECUTION_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _reflect_phase(self, task: Task, step: ExecutionStep, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        REFLECT phase: Analyze step execution result.

        Args:
            task: Parent task
            step: Executed step
            result: Execution result

        Returns:
            Reflection analysis
        """
        logger.info(f"Reflecting on step {step.step_id} result")

        reflection = {
            "step_id": step.step_id,
            "success": result.get("success", False),
            "timestamp": datetime.now().isoformat()
        }

        # Analyze result
        if result.get("success"):
            reflection["analysis"] = "Step completed successfully"
            reflection["next_action"] = "continue"
        else:
            error_type = result.get("error", "UNKNOWN_ERROR")
            reflection["analysis"] = f"Step failed with error: {error_type}"

            # Determine if retry is appropriate
            if step.retry_count < step.max_retries:
                if error_type in ["RATE_LIMIT_EXCEEDED", "TIMEOUT", "CONNECTION_ERROR"]:
                    reflection["next_action"] = "retry"
                    reflection["reason"] = "Transient error, retry recommended"
                elif error_type in ["CREDENTIALS_NOT_CONFIGURED", "AUTHENTICATION_FAILED"]:
                    reflection["next_action"] = "escalate"
                    reflection["reason"] = "Configuration issue, human intervention required"
                else:
                    reflection["next_action"] = "retry"
                    reflection["reason"] = "Unknown error, retry with adjusted parameters"
            else:
                reflection["next_action"] = "escalate"
                reflection["reason"] = "Max retries exceeded"

        # Log reflection
        task.execution_history.append({
            "phase": "reflect",
            "step_id": step.step_id,
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection
        })

        return reflection

    async def _adjust_parameters(self, step: ExecutionStep, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Adjust step parameters based on failure analysis.

        Args:
            step: Failed step
            result: Failure result

        Returns:
            Adjusted parameters or None
        """
        error_type = result.get("error", "UNKNOWN_ERROR")

        # For rate limit errors, no parameter adjustment needed (just wait)
        if error_type == "RATE_LIMIT_EXCEEDED":
            await asyncio.sleep(5)  # Wait before retry
            return None

        # For other errors, return original parameters
        return None

    async def _call_mcp_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP action via client.

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            Action result
        """
        if not self.mcp_client:
            raise Exception("MCP client not configured")

        # Call MCP tool
        result = await self.mcp_client.call_tool(action, parameters)
        return result

    async def _escalate_task(self, task: Task) -> None:
        """
        Escalate failed task to human oversight.

        Args:
            task: Failed task
        """
        logger.warning(f"Escalating task to human oversight: {task.task_id}")

        task.status = TaskStatus.ESCALATED

        # Create escalation file
        escalation_file = self.pending_approval_path / f"{task.task_id}_escalation.md"

        content = f"""# Task Escalation: {task.description}

**Task ID**: {task.task_id}
**Domain**: {task.domain}
**Status**: {task.status.value}
**Created**: {task.created_at.strftime("%Y-%m-%d %H:%M")}
**Failed**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Error

{task.error}

## Execution History

"""

        for i, step in enumerate(task.steps, 1):
            content += f"### Step {i}: {step.description}\n\n"
            content += f"- **Action**: {step.action}\n"
            content += f"- **Status**: {step.status.value}\n"
            content += f"- **Retry Count**: {step.retry_count}\n"

            if step.error:
                content += f"- **Error**: {step.error}\n"

            content += "\n"

        content += "## Required Action\n\n"
        content += "Please review this task and take appropriate action:\n"
        content += "1. Fix the underlying issue\n"
        content += "2. Retry the task manually\n"
        content += "3. Mark as resolved\n\n"

        with open(escalation_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Escalation file created: {escalation_file}")


async def main():
    """Test Ralph Wiggum Loop."""
    loop = RalphWiggumLoop()

    # Create test task
    task = Task(
        task_id="test_001",
        description="Test multi-step task execution",
        domain="business"
    )

    # Add steps
    task.add_step(
        description="Create test customer",
        action="create_customer",
        parameters={"name": "Test Customer", "email": "test@example.com"}
    )

    task.add_step(
        description="Create test invoice",
        action="create_invoice",
        parameters={"customer_name": "Test Customer", "amount": 1000.0, "description": "Test invoice"}
    )

    # Execute task
    result = await loop.execute_task(task)
    print(f"Task execution result:\n{json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
