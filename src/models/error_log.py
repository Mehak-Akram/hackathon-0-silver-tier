"""
Error Log model for Gold Tier Autonomous AI Employee.

Represents a system error or failure.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories."""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ResolutionStatus(str, Enum):
    """Error resolution status."""
    UNRESOLVED = "unresolved"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    IGNORED = "ignored"


class ErrorLog(BaseModel):
    """
    Error Log entity representing a system error or failure.

    Attributes:
        error_id: Unique error identifier
        timestamp: When error occurred
        severity: Error severity level
        category: Error category
        error_type: Specific error type (e.g., "RATE_LIMIT_EXCEEDED")
        error_message: Human-readable error message

        operation: Operation that failed
        component: System component where error occurred
        task_id: Related task ID (if applicable)

        stack_trace: Full stack trace
        context: Additional error context

        retry_count: Number of retry attempts
        resolution_status: Current resolution status
        resolved_at: When error was resolved
        resolution_notes: Resolution details

        escalation_flag: Whether error requires escalation
        escalated_at: When error was escalated
        escalated_to: Who error was escalated to

        metadata: Additional error metadata
    """

    error_id: str = Field(..., description="Unique error identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    severity: ErrorSeverity = Field(..., description="Error severity")
    category: ErrorCategory = Field(default=ErrorCategory.UNKNOWN, description="Error category")
    error_type: str = Field(..., description="Specific error type")
    error_message: str = Field(..., description="Error message")

    # Context
    operation: str = Field(..., description="Failed operation")
    component: str = Field(..., description="System component")
    task_id: Optional[str] = Field(default=None, description="Related task ID")

    # Details
    stack_trace: Optional[str] = Field(default=None, description="Stack trace")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")

    # Retry tracking
    retry_count: int = Field(default=0, description="Retry attempts")

    # Resolution
    resolution_status: ResolutionStatus = Field(default=ResolutionStatus.UNRESOLVED, description="Resolution status")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")
    resolution_notes: Optional[str] = Field(default=None, description="Resolution details")

    # Escalation
    escalation_flag: bool = Field(default=False, description="Escalation required")
    escalated_at: Optional[datetime] = Field(default=None, description="Escalation timestamp")
    escalated_to: Optional[str] = Field(default=None, description="Escalation recipient")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True

    def mark_in_progress(self) -> None:
        """Mark error resolution as in progress."""
        self.resolution_status = ResolutionStatus.IN_PROGRESS

    def mark_resolved(self, notes: Optional[str] = None) -> None:
        """
        Mark error as resolved.

        Args:
            notes: Resolution notes
        """
        self.resolution_status = ResolutionStatus.RESOLVED
        self.resolved_at = datetime.now()
        if notes:
            self.resolution_notes = notes

    def mark_escalated(self, escalated_to: str, reason: Optional[str] = None) -> None:
        """
        Mark error as escalated.

        Args:
            escalated_to: Who error was escalated to
            reason: Escalation reason
        """
        self.resolution_status = ResolutionStatus.ESCALATED
        self.escalation_flag = True
        self.escalated_at = datetime.now()
        self.escalated_to = escalated_to
        if reason:
            self.metadata["escalation_reason"] = reason

    def mark_ignored(self, reason: str) -> None:
        """
        Mark error as ignored.

        Args:
            reason: Why error was ignored
        """
        self.resolution_status = ResolutionStatus.IGNORED
        self.metadata["ignore_reason"] = reason

    def increment_retry(self) -> None:
        """Increment retry counter."""
        self.retry_count += 1

    def is_transient(self) -> bool:
        """
        Check if error is transient (retryable).

        Returns:
            True if error is transient
        """
        transient_types = [
            "RATE_LIMIT_EXCEEDED",
            "TIMEOUT",
            "CONNECTION_ERROR",
            "NETWORK_ERROR",
            "SERVICE_UNAVAILABLE",
            "TEMPORARY_FAILURE"
        ]
        return self.error_type in transient_types

    def is_critical(self) -> bool:
        """Check if error is critical."""
        return self.severity == ErrorSeverity.CRITICAL

    def requires_immediate_attention(self) -> bool:
        """
        Check if error requires immediate attention.

        Returns:
            True if error is critical or escalated
        """
        return self.is_critical() or self.escalation_flag

    def get_age_minutes(self) -> float:
        """
        Get error age in minutes.

        Returns:
            Age in minutes
        """
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() / 60

    def add_context(self, key: str, value: Any) -> None:
        """
        Add context information.

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert error log to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert error log to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorLog":
        """
        Create error log from dictionary.

        Args:
            data: Error log data dictionary

        Returns:
            ErrorLog instance
        """
        return cls(**data)

    @classmethod
    def from_exception(
        cls,
        error_id: str,
        exception: Exception,
        operation: str,
        component: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        task_id: Optional[str] = None
    ) -> "ErrorLog":
        """
        Create error log from exception.

        Args:
            error_id: Unique error identifier
            exception: Exception object
            operation: Operation that failed
            component: System component
            severity: Error severity
            task_id: Related task ID

        Returns:
            ErrorLog instance
        """
        import traceback

        error_type = type(exception).__name__
        error_message = str(exception)
        stack_trace = traceback.format_exc()

        # Categorize error
        category = ErrorCategory.UNKNOWN
        if "network" in error_message.lower() or "connection" in error_message.lower():
            category = ErrorCategory.NETWORK
        elif "auth" in error_message.lower():
            category = ErrorCategory.AUTHENTICATION
        elif "permission" in error_message.lower():
            category = ErrorCategory.AUTHORIZATION
        elif "validation" in error_message.lower():
            category = ErrorCategory.VALIDATION

        return cls(
            error_id=error_id,
            severity=severity,
            category=category,
            error_type=error_type,
            error_message=error_message,
            operation=operation,
            component=component,
            task_id=task_id,
            stack_trace=stack_trace
        )
