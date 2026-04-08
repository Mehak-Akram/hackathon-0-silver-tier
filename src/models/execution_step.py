"""
Execution Step model for Gold Tier Autonomous AI Employee.

Represents a single step in a multi-step task execution.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class StepStatus(str, Enum):
    """Execution step status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class ExecutionStep(BaseModel):
    """
    Execution step entity representing a single step in a multi-step task.

    Attributes:
        step_id: Unique step identifier within task
        task_id: Parent task identifier
        description: Human-readable step description
        action: Action to execute (e.g., "create_invoice", "send_email")
        parameters: Action parameters
        status: Current step status
        result: Execution result data
        error: Error message if step failed
        error_type: Error type classification
        retry_count: Number of retry attempts
        max_retries: Maximum allowed retries
        started_at: Step execution start timestamp
        completed_at: Step completion timestamp
        duration_ms: Execution duration in milliseconds
        dependencies: List of step IDs this step depends on
        metadata: Additional step metadata
    """

    step_id: int = Field(..., description="Step identifier")
    task_id: str = Field(..., description="Parent task ID")
    description: str = Field(..., description="Step description")
    action: str = Field(..., description="Action to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")

    # Status
    status: StepStatus = Field(default=StepStatus.PENDING, description="Step status")

    # Results
    result: Optional[Dict[str, Any]] = Field(default=None, description="Execution result")
    error: Optional[str] = Field(default=None, description="Error message")
    error_type: Optional[str] = Field(default=None, description="Error type")

    # Retry handling
    retry_count: int = Field(default=0, description="Retry attempts")
    max_retries: int = Field(default=3, description="Maximum retries")

    # Timing
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    duration_ms: Optional[float] = Field(default=None, description="Duration in milliseconds")

    # Dependencies
    dependencies: list[int] = Field(default_factory=list, description="Dependent step IDs")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True

    def mark_started(self) -> None:
        """Mark step as started."""
        self.status = StepStatus.EXECUTING
        self.started_at = datetime.now()

    def mark_completed(self, result: Dict[str, Any]) -> None:
        """
        Mark step as completed.

        Args:
            result: Step execution result
        """
        self.status = StepStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self._calculate_duration()

    def mark_failed(self, error: str, error_type: Optional[str] = None) -> None:
        """
        Mark step as failed.

        Args:
            error: Error message
            error_type: Error type classification
        """
        self.status = StepStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        self.error_type = error_type or "UNKNOWN_ERROR"
        self._calculate_duration()

    def mark_retrying(self) -> None:
        """Mark step as retrying."""
        self.status = StepStatus.RETRYING
        self.retry_count += 1

    def mark_skipped(self, reason: str) -> None:
        """
        Mark step as skipped.

        Args:
            reason: Skip reason
        """
        self.status = StepStatus.SKIPPED
        self.completed_at = datetime.now()
        self.metadata["skip_reason"] = reason

    def can_retry(self) -> bool:
        """Check if step can be retried."""
        return self.retry_count < self.max_retries

    def is_transient_error(self) -> bool:
        """
        Check if error is transient (retryable).

        Returns:
            True if error is transient
        """
        transient_errors = [
            "RATE_LIMIT_EXCEEDED",
            "TIMEOUT",
            "CONNECTION_ERROR",
            "NETWORK_ERROR",
            "SERVICE_UNAVAILABLE"
        ]
        return self.error_type in transient_errors

    def _calculate_duration(self) -> None:
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = delta.total_seconds() * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert step to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionStep":
        """
        Create step from dictionary.

        Args:
            data: Step data dictionary

        Returns:
            ExecutionStep instance
        """
        return cls(**data)
