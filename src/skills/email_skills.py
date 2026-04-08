"""
Email Skills for Gold Tier Autonomous AI Employee.

Provides email sending and notification skills.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional
from src.base_skill import BaseSkill
from mcp_server.email_handler import EmailHandler
from src.retry_logic import with_retry
from shared.logging_config import get_logger

logger = get_logger(__name__, "email-skills.log")


class SendEmailSkill(BaseSkill):
    """
    Skill for sending emails via SMTP.

    Risk Level: Medium (external communication)
    """

    def __init__(self):
        """Initialize send email skill."""
        super().__init__(
            name="send_email",
            description="Send an email via SMTP",
            risk_level="medium"
        )
        self.email_handler = EmailHandler()

    @with_retry(max_attempts=3)
    async def execute(self, to: str, subject: str, body: str,
                     cc: Optional[str] = None, bcc: Optional[str] = None,
                     content_type: str = "text/plain", **kwargs) -> Dict[str, Any]:
        """
        Execute email sending.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            content_type: Content type (text/plain or text/html)

        Returns:
            Result dictionary with send status
        """
        logger.info(f"Sending email to {to}: {subject}")

        try:
            # Validate email address
            if not to or "@" not in to:
                return {
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid recipient email address"
                }

            result = self.email_handler.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                content_type=content_type
            )

            if result.get("success"):
                logger.info(f"Email sent successfully to {to}")
            else:
                logger.error(f"Email send failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Email send error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "EMAIL_SEND_ERROR",
                "message": str(e)
            }


class SendCEOBriefingSkill(BaseSkill):
    """
    Skill for sending CEO briefing via email.

    Risk Level: Medium (executive communication)
    """

    def __init__(self):
        """Initialize CEO briefing email skill."""
        super().__init__(
            name="send_ceo_briefing",
            description="Send CEO briefing via email",
            risk_level="medium"
        )
        self.email_handler = EmailHandler()

    @with_retry(max_attempts=3)
    async def execute(self, briefing_file_path: str, recipient: str,
                     week_start: str, week_end: str, **kwargs) -> Dict[str, Any]:
        """
        Execute CEO briefing email sending.

        Args:
            briefing_file_path: Path to briefing markdown file
            recipient: CEO email address
            week_start: Week start date
            week_end: Week end date

        Returns:
            Result dictionary with send status
        """
        logger.info(f"Sending CEO briefing to {recipient}")

        try:
            # Read briefing content
            briefing_path = Path(briefing_file_path)
            if not briefing_path.exists():
                return {
                    "success": False,
                    "error": "FILE_NOT_FOUND",
                    "message": f"Briefing file not found: {briefing_file_path}"
                }

            briefing_content = briefing_path.read_text(encoding='utf-8')

            # Send email
            subject = f"Weekly CEO Briefing - {week_start} to {week_end}"
            result = self.email_handler.send_email(
                to=recipient,
                subject=subject,
                body=briefing_content,
                content_type="text/plain"
            )

            if result.get("success"):
                logger.info(f"CEO briefing sent successfully to {recipient}")
            else:
                logger.error(f"CEO briefing send failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"CEO briefing send error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "BRIEFING_SEND_ERROR",
                "message": str(e)
            }


class SendNotificationSkill(BaseSkill):
    """
    Skill for sending notification emails.

    Risk Level: Low (internal notification)
    """

    def __init__(self):
        """Initialize notification email skill."""
        super().__init__(
            name="send_notification",
            description="Send notification email",
            risk_level="low"
        )
        self.email_handler = EmailHandler()

    @with_retry(max_attempts=3)
    async def execute(self, to: str, notification_type: str,
                     message: str, details: Optional[Dict[str, Any]] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute notification email sending.

        Args:
            to: Recipient email address
            notification_type: Type of notification (error, success, warning, info)
            message: Notification message
            details: Additional details (optional)

        Returns:
            Result dictionary with send status
        """
        logger.info(f"Sending {notification_type} notification to {to}")

        try:
            # Format notification email
            subject = f"[{notification_type.upper()}] AI Employee Notification"

            body = f"""
AI Employee Notification
========================

Type: {notification_type.upper()}
Time: {kwargs.get('timestamp', 'N/A')}

Message:
{message}
"""

            if details:
                body += "\n\nDetails:\n"
                for key, value in details.items():
                    body += f"  {key}: {value}\n"

            body += "\n---\nGenerated by Gold Tier Autonomous AI Employee"

            result = self.email_handler.send_email(
                to=to,
                subject=subject,
                body=body,
                content_type="text/plain"
            )

            if result.get("success"):
                logger.info(f"Notification sent successfully to {to}")
            else:
                logger.error(f"Notification send failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Notification send error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "NOTIFICATION_SEND_ERROR",
                "message": str(e)
            }


class SendErrorAlertSkill(BaseSkill):
    """
    Skill for sending error alert emails.

    Risk Level: Medium (critical notification)
    """

    def __init__(self):
        """Initialize error alert email skill."""
        super().__init__(
            name="send_error_alert",
            description="Send error alert email",
            risk_level="medium"
        )
        self.email_handler = EmailHandler()

    @with_retry(max_attempts=3)
    async def execute(self, to: str, error_type: str, error_message: str,
                     task_id: Optional[str] = None, severity: str = "medium",
                     **kwargs) -> Dict[str, Any]:
        """
        Execute error alert email sending.

        Args:
            to: Recipient email address
            error_type: Type of error
            error_message: Error message
            task_id: Related task ID (optional)
            severity: Error severity (low/medium/high/critical)

        Returns:
            Result dictionary with send status
        """
        logger.info(f"Sending error alert to {to}: {error_type}")

        try:
            # Format error alert email
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🔴",
                "critical": "🚨"
            }.get(severity, "⚠️")

            subject = f"{severity_emoji} [ERROR ALERT] {error_type}"

            body = f"""
{severity_emoji} AI Employee Error Alert
================================

Severity: {severity.upper()}
Error Type: {error_type}
Time: {kwargs.get('timestamp', 'N/A')}
"""

            if task_id:
                body += f"Task ID: {task_id}\n"

            body += f"""
Error Message:
{error_message}

Action Required:
Please review this error and take appropriate action.

---
Generated by Gold Tier Autonomous AI Employee
"""

            result = self.email_handler.send_email(
                to=to,
                subject=subject,
                body=body,
                content_type="text/plain"
            )

            if result.get("success"):
                logger.info(f"Error alert sent successfully to {to}")
            else:
                logger.error(f"Error alert send failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Error alert send error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ERROR_ALERT_SEND_ERROR",
                "message": str(e)
            }


# Export all email skills
__all__ = [
    "SendEmailSkill",
    "SendCEOBriefingSkill",
    "SendNotificationSkill",
    "SendErrorAlertSkill"
]
