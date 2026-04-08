"""
Reporting Skills for Gold Tier Autonomous AI Employee.

Provides reporting and briefing generation skills.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional
from datetime import datetime
from src.base_skill import BaseSkill
from reporting.ceo_briefing import CEOBriefingGenerator
from src.retry_logic import with_retry
from shared.logging_config import get_logger

logger = get_logger(__name__, "reporting-skills.log")


class GenerateCEOBriefingSkill(BaseSkill):
    """
    Skill for generating CEO briefing reports.

    Risk Level: Low (read-only aggregation)
    """

    def __init__(self):
        """Initialize CEO briefing generation skill."""
        super().__init__(
            name="generate_ceo_briefing",
            description="Generate weekly CEO briefing report",
            risk_level="low"
        )
        self.briefing_generator = CEOBriefingGenerator()

    @with_retry(max_attempts=3)
    async def execute(self, week_offset: int = 0, **kwargs) -> Dict[str, Any]:
        """
        Execute CEO briefing generation.

        Args:
            week_offset: Week offset (0=current, -1=last week)

        Returns:
            Result dictionary with briefing file path and status
        """
        logger.info(f"Generating CEO briefing for week offset: {week_offset}")

        try:
            result = self.briefing_generator.generate_briefing(week_offset=week_offset)

            if result.get("success"):
                logger.info(f"CEO briefing generated: {result.get('file_path')}")
            else:
                logger.error(f"CEO briefing generation failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"CEO briefing generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "CEO_BRIEFING_ERROR",
                "message": str(e)
            }


class GenerateFinancialReportSkill(BaseSkill):
    """
    Skill for generating financial reports.

    Risk Level: Low (read-only operation)
    """

    def __init__(self):
        """Initialize financial report generation skill."""
        super().__init__(
            name="generate_financial_report",
            description="Generate financial performance report",
            risk_level="low"
        )

    @with_retry(max_attempts=3)
    async def execute(self, report_type: str = "monthly",
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute financial report generation.

        Args:
            report_type: Type of report (daily/weekly/monthly/quarterly)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Result dictionary with report data
        """
        logger.info(f"Generating {report_type} financial report")

        try:
            # Financial data is not available without an accounting system
            logger.warning("Financial report requested but no accounting system configured")
            return {
                "success": False,
                "error": "NO_ACCOUNTING_SYSTEM",
                "message": "No accounting system configured for financial reports"
            }

            # Generate report
            report = {
                "success": True,
                "report_type": report_type,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "generated_at": datetime.now().isoformat(),
                "financial_data": {
                    "revenue": {
                        "total": summary.get("total_revenue", 0),
                        "pending": summary.get("pending_revenue", 0)
                    },
                    "invoices": {
                        "total": summary.get("invoice_count", 0),
                        "posted": summary.get("posted_invoices", 0),
                        "draft": summary.get("draft_invoices", 0)
                    },
                    "customers": {
                        "total": summary.get("customer_count", 0)
                    }
                }
            }

            logger.info(f"Financial report generated: {report_type}")
            return report

        except Exception as e:
            logger.error(f"Financial report generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "FINANCIAL_REPORT_ERROR",
                "message": str(e)
            }


class GenerateMarketingReportSkill(BaseSkill):
    """
    Skill for generating marketing performance reports.

    Risk Level: Low (read-only operation)
    """

    def __init__(self):
        """Initialize marketing report generation skill."""
        super().__init__(
            name="generate_marketing_report",
            description="Generate marketing performance report",
            risk_level="low"
        )

    @with_retry(max_attempts=3)
    async def execute(self, report_type: str = "weekly",
                     days: int = 7, **kwargs) -> Dict[str, Any]:
        """
        Execute marketing report generation.

        Args:
            report_type: Type of report (daily/weekly/monthly)
            days: Number of days to include

        Returns:
            Result dictionary with report data
        """
        logger.info(f"Generating {report_type} marketing report for {days} days")

        try:
            # Import here to avoid circular dependency
            from mcp_server.twitter_handler import TwitterHandler
            from mcp_server.instagram_handler import InstagramHandler
            from mcp_server.facebook_handler import FacebookHandler

            twitter = TwitterHandler()
            instagram = InstagramHandler()
            facebook = FacebookHandler()

            # Fetch social media data
            twitter_data = twitter.get_engagement_summary(days=days)
            instagram_data = instagram.get_engagement_summary(days=days)
            facebook_data = facebook.get_engagement_summary(days=days)

            # Generate report
            report = {
                "success": True,
                "report_type": report_type,
                "period_days": days,
                "generated_at": datetime.now().isoformat(),
                "platforms": {
                    "twitter": twitter_data if twitter_data.get("success") else {"success": False},
                    "instagram": instagram_data if instagram_data.get("success") else {"success": False},
                    "facebook": facebook_data if facebook_data.get("success") else {"success": False}
                },
                "summary": {
                    "total_engagement": 0,
                    "total_reach": 0,
                    "platforms_active": 0
                }
            }

            # Calculate totals
            for platform, data in report["platforms"].items():
                if data.get("success"):
                    report["summary"]["platforms_active"] += 1
                    platform_summary = data.get("summary", {})
                    report["summary"]["total_engagement"] += platform_summary.get("total_engagements", 0)
                    report["summary"]["total_reach"] += platform_summary.get("total_reach", 0)

            logger.info(f"Marketing report generated: {report_type}")
            return report

        except Exception as e:
            logger.error(f"Marketing report generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "MARKETING_REPORT_ERROR",
                "message": str(e)
            }


class GenerateOperationalReportSkill(BaseSkill):
    """
    Skill for generating operational reports.

    Risk Level: Low (read-only operation)
    """

    def __init__(self):
        """Initialize operational report generation skill."""
        super().__init__(
            name="generate_operational_report",
            description="Generate operational performance report",
            risk_level="low"
        )
        self.vault_path = Path("E:/AI_Employee_Vault")

    @with_retry(max_attempts=3)
    async def execute(self, report_type: str = "weekly", **kwargs) -> Dict[str, Any]:
        """
        Execute operational report generation.

        Args:
            report_type: Type of report (daily/weekly/monthly)

        Returns:
            Result dictionary with report data
        """
        logger.info(f"Generating {report_type} operational report")

        try:
            # Count tasks in each folder
            folders = ["Inbox", "Needs_Action", "Pending_Approval", "Done", "Rejected"]
            task_counts = {}

            for folder in folders:
                folder_path = self.vault_path / folder
                if folder_path.exists():
                    task_counts[folder] = len(list(folder_path.glob("*.md")))
                else:
                    task_counts[folder] = 0

            # Generate report
            report = {
                "success": True,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "task_summary": task_counts,
                "metrics": {
                    "total_tasks": sum(task_counts.values()),
                    "completed_tasks": task_counts.get("Done", 0),
                    "pending_tasks": task_counts.get("Needs_Action", 0) + task_counts.get("Inbox", 0),
                    "awaiting_approval": task_counts.get("Pending_Approval", 0),
                    "completion_rate": (task_counts.get("Done", 0) / sum(task_counts.values()) * 100)
                        if sum(task_counts.values()) > 0 else 0
                }
            }

            logger.info(f"Operational report generated: {report_type}")
            return report

        except Exception as e:
            logger.error(f"Operational report generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "OPERATIONAL_REPORT_ERROR",
                "message": str(e)
            }


# Export all reporting skills
__all__ = [
    "GenerateCEOBriefingSkill",
    "GenerateFinancialReportSkill",
    "GenerateMarketingReportSkill",
    "GenerateOperationalReportSkill"
]
