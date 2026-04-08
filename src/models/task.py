"""
Task model for Gold Tier Autonomous AI Employee.

Represents a unit of work assigned to the AI Employee.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class TaskDomain(str, Enum):
    """Task domain classification."""
    PERSONAL = "personal"
    BUSINESS = "business"
    ACCOUNTING = "accounting"
    MARKETING = "marketing"
    GENERAL = "general"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """
    Task entity representing a unit of work.

    Attributes:
        task_id: Unique task identifier
        description: Human-readable task description
        domain: Task domain (personal/business/accounting/marketing)
        status: Current task status
        priority: Task priority level
        created_at: Task creation timestamp
        started_at: Task execution start timestamp
        completed_at: Task completion timestamp
        due_date: Optional deadline for task completion
        assigned_to: Optional assignee (user or agent)
        execution_history: List of execution events
        metadata: Additional task metadata
        error: Error message if task failed
        retry_count: Number of retry attempts
        max_retries: Maximum allowed retries
    """

    task_id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Task description")
    domain: TaskDomain = Field(default=TaskDomain.GENERAL, description="Task domain")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    due_date: Optional[datetime] = Field(default=None, description="Due date")

    # Assignment
    assigned_to: Optional[str] = Field(default=None, description="Assignee")

    # Execution tracking
    execution_history: List[Dict[str, Any]] = Field(default_factory=list, description="Execution events")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Error handling
    error: Optional[str] = Field(default=None, description="Error message")
    retry_count: int = Field(default=0, description="Retry attempts")
    max_retries: int = Field(default=3, description="Maximum retries")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True

    def add_execution_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Add execution event to history.

        Args:
            event_type: Type of event (e.g., "started", "completed", "failed")
            details: Event details
        """
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        })

    def mark_started(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.add_execution_event("started", {"status": self.status})

    def mark_completed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark task as completed.

        Args:
            result: Optional task result data
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.add_execution_event("completed", {"status": self.status, "result": result})

    def mark_failed(self, error: str) -> None:
        """
        Mark task as failed.

        Args:
            error: Error message
        """
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
        self.add_execution_event("failed", {"status": self.status, "error": error})

    def mark_escalated(self, reason: str) -> None:
        """
        Mark task as escalated to human oversight.

        Args:
            reason: Escalation reason
        """
        self.status = TaskStatus.ESCALATED
        self.add_execution_event("escalated", {"status": self.status, "reason": reason})

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment retry counter."""
        self.retry_count += 1
        self.add_execution_event("retry", {"retry_count": self.retry_count})

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert task to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Create task from dictionary.

        Args:
            data: Task data dictionary

        Returns:
            Task instance
        """
        return cls(**data)
