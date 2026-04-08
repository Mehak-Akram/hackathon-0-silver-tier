"""
Audit logging infrastructure for Gold Tier Autonomous AI Employee.

Provides comprehensive, structured logging with complete context for compliance,
debugging, and analysis. All actions are logged with risk classification,
approval tracking, and execution results.
"""
import structlog
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Dict
from contextlib import contextmanager
from uuid import uuid4


class RiskLevel(str, Enum):
    """Risk classification for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalMethod(str, Enum):
    """How an action was approved."""
    AUTO_APPROVED = "auto_approved"
    HUMAN_APPROVED = "human_approved"
    REJECTED = "rejected"
    PENDING = "pending"


# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)


class ActionLogContext:
    """Context object for tracking action outputs and side effects."""

    def __init__(self, logger):
        self.logger = logger
        self.output_data: Dict[str, Any] = {}
        self.side_effects: list = []
        self.error_details: Dict[str, Any] = {}

    def set_output(self, data: Dict[str, Any]):
        """Set output data for the action."""
        self.output_data.update(data)

    def add_side_effect(self, effect: str, details: Optional[Dict[str, Any]] = None):
        """Record a side effect of the action."""
        self.side_effects.append({
            "effect": effect,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def set_error_details(self, details: Dict[str, Any]):
        """Set additional error context."""
        self.error_details.update(details)


class AuditLogger:
    """
    Audit logger for AI Employee actions.

    Provides structured, append-only logging with complete context
    for compliance, debugging, and analysis.
    """

    def __init__(self, log_dir: Path = Path("Audit_Logs")):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory for audit log files
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Get logger instance
        self.logger = structlog.get_logger("audit")

    @contextmanager
    def log_action(
        self,
        action_type: str,
        description: str,
        risk_level: RiskLevel,
        approval_method: ApprovalMethod,
        input_data: Optional[Dict[str, Any]] = None,
        **extra_context
    ):
        """
        Context manager for logging actions with automatic success/failure tracking.

        Usage:
            with audit_logger.log_action(
                action_type="email.send",
                description="Send weekly CEO briefing",
                risk_level=RiskLevel.MEDIUM,
                approval_method=ApprovalMethod.AUTO_APPROVED,
                input_data={"recipient": "ceo@company.com"}
            ) as log:
                result = send_email(...)
                log.set_output({"message_id": result.id})

        Args:
            action_type: Dot-notation action identifier
            description: Human-readable action description
            risk_level: Risk classification
            approval_method: How action was approved
            input_data: Input parameters and data
            **extra_context: Additional context fields

        Yields:
            ActionLogContext: Context object for setting output and side effects
        """
        action_id = self._generate_action_id()
        start_time = datetime.now(timezone.utc)

        # Bind context for this action
        log = self.logger.bind(
            action_id=action_id,
            action_type=action_type,
            description=description,
            risk_level=risk_level.value,
            approval_method=approval_method.value,
            input_data=input_data or {},
            started_at=start_time.isoformat(),
            **extra_context
        )

        context = ActionLogContext(log)

        try:
            log.info("action_started")
            yield context

            # Success path
            end_time = datetime.now(timezone.utc)
            duration_ms = (end_time - start_time).total_seconds() * 1000

            log.info(
                "action_completed",
                status="success",
                output_data=context.output_data,
                side_effects=context.side_effects,
                completed_at=end_time.isoformat(),
                duration_ms=round(duration_ms, 2)
            )

        except Exception as e:
            # Failure path
            end_time = datetime.now(timezone.utc)
            duration_ms = (end_time - start_time).total_seconds() * 1000

            log.error(
                "action_failed",
                status="failure",
                error_type=type(e).__name__,
                error_message=str(e),
                error_details=context.error_details,
                output_data=context.output_data,
                side_effects=context.side_effects,
                completed_at=end_time.isoformat(),
                duration_ms=round(duration_ms, 2),
                exc_info=True
            )
            raise

    def log_approval_decision(
        self,
        action_id: str,
        decision: ApprovalMethod,
        approver: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """
        Log an approval decision for a pending action.

        Args:
            action_id: ID of the action being approved/rejected
            decision: Approval decision
            approver: Who made the decision
            reason: Reason for decision
        """
        self.logger.info(
            "approval_decision",
            action_id=action_id,
            decision=decision.value,
            approver=approver,
            reason=reason,
            decided_at=datetime.now(timezone.utc).isoformat()
        )

    def _generate_action_id(self) -> str:
        """Generate unique action ID."""
        return f"act_{uuid4().hex[:12]}"


# Global audit logger instance
audit_logger = AuditLogger()
