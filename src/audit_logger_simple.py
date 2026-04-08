"""
Simplified Audit Logger - No External Dependencies.

Provides JSON-based audit logging without requiring structlog.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Dict
from contextlib import contextmanager


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


class AuditLogger:
    """
    Simplified audit logger for AI Employee actions.

    Provides JSON-based logging without external dependencies.
    """

    def __init__(self, log_dir: Path = Path("Audit_Logs")):
        """Initialize audit logger."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create today's log file
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"{today}-audit.jsonl"

    def _write_log(self, log_entry: Dict[str, Any]):
        """Write a log entry to the JSONL file."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_event(
        self,
        event_type: str,
        action: str = None,
        risk_level: str = None,
        details: Optional[Dict[str, Any]] = None,
        approval_method: Optional[str] = None,
        approved_by: Optional[str] = None,
        severity: Optional[str] = None
    ):
        """
        Log an event.

        Args:
            event_type: Type of event (e.g., "invoice_created")
            action: Action taken (e.g., "create_invoice") - optional
            risk_level: Risk level (low/medium/high) - optional
            details: Additional details
            approval_method: How it was approved
            approved_by: Who approved it
            severity: Severity level (for compatibility) - optional
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "details": details or {},
            "system": "gold_tier_autonomous_employee",
            "version": "1.0.0"
        }

        if action:
            log_entry["action"] = action
        if risk_level:
            log_entry["risk_level"] = risk_level
        if severity:
            log_entry["severity"] = severity
        if approval_method:
            log_entry["approval_method"] = approval_method
        if approved_by:
            log_entry["approved_by"] = approved_by

        self._write_log(log_entry)

    @contextmanager
    def log_action(
        self,
        action_type: str,
        description: str,
        risk_level: str = "low",
        approval_method: Optional[str] = None,
        approved_by: Optional[str] = None,
        **context
    ):
        """
        Context manager for logging actions with automatic success/failure tracking.

        Usage:
            with logger.log_action("create_invoice", "Creating invoice", risk_level="high"):
                # perform action
                pass
        """
        action_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        # Log action start
        start_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_id": action_id,
            "event_type": "action_started",
            "action_type": action_type,
            "description": description,
            "risk_level": risk_level,
            "context": context,
            "system": "gold_tier_autonomous_employee"
        }

        if approval_method:
            start_entry["approval_method"] = approval_method
        if approved_by:
            start_entry["approved_by"] = approved_by

        self._write_log(start_entry)

        try:
            yield

            # Log success
            success_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_id": action_id,
                "event_type": "action_completed",
                "action_type": action_type,
                "status": "success",
                "system": "gold_tier_autonomous_employee"
            }
            self._write_log(success_entry)

        except Exception as e:
            # Log failure
            error_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_id": action_id,
                "event_type": "action_failed",
                "action_type": action_type,
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "system": "gold_tier_autonomous_employee"
            }
            self._write_log(error_entry)
            raise

    def get_recent_logs(self, limit: int = 100) -> list:
        """Get recent log entries."""
        if not self.log_file.exists():
            return []

        logs = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))

        return logs[-limit:]
