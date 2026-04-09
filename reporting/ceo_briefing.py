"""
CEO Briefing Generator for Gold Tier Autonomous AI Employee.

Generates comprehensive weekly executive briefings with:
- Executive Summary
- Revenue Summary
- Accounting Summary
- Marketing Performance
- Risk Alerts
- Action Recommendations
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from mcp_server.twitter_handler import TwitterHandler
from mcp_server.instagram_handler import InstagramHandler
from mcp_server.facebook_handler import FacebookHandler

logger = get_logger(__name__, "ceo-briefing.log")


class CEOBriefingGenerator:
    """
    CEO Briefing Generator.

    Aggregates data from multiple sources and generates executive briefings.
    """

    def __init__(self):
        """Initialize CEO briefing generator."""
        self.vault_path = Path(os.getenv("VAULT_PATH", "E:/AI_Employee_Vault"))
        self.briefings_path = self.vault_path / "Briefings"
        self.briefings_path.mkdir(exist_ok=True)

        logger.info("CEO Briefing Generator initialized")

    def generate_briefing(self, week_offset: int = 0) -> Dict[str, Any]:
        """
        Generate CEO briefing for specified week.

        Args:
            week_offset: Week offset (0=current, -1=last week)

        Returns:
            Result dictionary with briefing status and file path
        """
        try:
            logger.info(f"Generating CEO briefing for week offset: {week_offset}")

            # Calculate date range
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday() + (7 * abs(week_offset)))
            week_end = week_start + timedelta(days=6)

            # Gather data from all sources
            briefing_data = {
                "generated_at": datetime.now().isoformat(),
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_end": week_end.strftime("%Y-%m-%d"),
                "financial": self._fetch_financial_data(),
                "marketing": self._fetch_marketing_data(),
                "operations": self._fetch_operations_data(),
                "risks": self._identify_risks()
            }

            # Generate briefing document
            briefing_content = self._format_briefing(briefing_data)

            # Save to file
            filename = f"Monday_CEO_Briefing_{week_start.strftime('%Y-%m-%d')}.md"
            file_path = self.briefings_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(briefing_content)

            logger.info(f"CEO briefing generated successfully: {file_path}")

            return {
                "success": True,
                "file_path": str(file_path),
                "week_start": briefing_data["week_start"],
                "week_end": briefing_data["week_end"],
                "sections": {
                    "financial": briefing_data["financial"].get("success", False),
                    "marketing": briefing_data["marketing"].get("success", False),
                    "operations": True,
                    "risks": True
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate CEO briefing: {e}", exc_info=True)
            return {
                "success": False,
                "error": "CEO_BRIEFING_GENERATION_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _fetch_financial_data(self) -> Dict[str, Any]:
        """Fetch financial data (placeholder - no accounting system connected)."""
        try:
            logger.info("Financial data fetch requested - no accounting system configured")
            return {
                "success": False,
                "message": "No accounting system configured"
            }
        except Exception as e:
            logger.error(f"Failed to fetch financial data: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Financial data unavailable"
            }

    def _fetch_marketing_data(self) -> Dict[str, Any]:
        """Fetch marketing data from social media platforms."""
        try:
            logger.info("Fetching marketing data from social platforms")

            twitter = TwitterHandler()
            instagram = InstagramHandler()
            facebook = FacebookHandler()

            twitter_data = twitter.get_engagement_summary(7)
            instagram_data = instagram.get_engagement_summary(7)
            facebook_data = facebook.get_engagement_summary(7)

            return {
                "success": True,
                "twitter": twitter_data,
                "instagram": instagram_data,
                "facebook": facebook_data,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to fetch marketing data: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Marketing data unavailable"
            }

    def _fetch_operations_data(self) -> Dict[str, Any]:
        """Fetch operational data from task system."""
        try:
            logger.info("Fetching operations data")

            # Check for completed tasks in Done folder
            done_path = self.vault_path / "Done"
            completed_tasks = []

            if done_path.exists():
                for file in done_path.glob("*.md"):
                    completed_tasks.append({
                        "name": file.stem,
                        "completed_at": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })

            return {
                "success": True,
                "completed_tasks": len(completed_tasks),
                "recent_completions": completed_tasks[:10]
            }

        except Exception as e:
            logger.error(f"Failed to fetch operations data: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _identify_risks(self) -> Dict[str, Any]:
        """Identify risks and alerts."""
        risks = []

        # Check for pending approval items
        pending_path = self.vault_path / "Pending_Approval"
        if pending_path.exists():
            pending_count = len(list(pending_path.glob("*.md")))
            if pending_count > 0:
                risks.append({
                    "severity": "medium",
                    "category": "operations",
                    "message": f"{pending_count} items pending approval"
                })

        # Check for failed tasks
        needs_action_path = self.vault_path / "Needs_Action"
        if needs_action_path.exists():
            needs_action_count = len(list(needs_action_path.glob("*.md")))
            if needs_action_count > 5:
                risks.append({
                    "severity": "high",
                    "category": "operations",
                    "message": f"{needs_action_count} tasks need attention"
                })

        return {
            "success": True,
            "risk_count": len(risks),
            "risks": risks
        }

    def _format_briefing(self, data: Dict[str, Any]) -> str:
        """Format briefing data into markdown document."""

        content = f"""# Weekly CEO Briefing

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Period**: {data['week_start']} to {data['week_end']}

---

## Executive Summary

This briefing provides a comprehensive overview of business operations, financial performance, marketing metrics, and risk alerts for the week.

"""

        # Financial Summary
        content += "## Financial Summary\n\n"
        financial = data.get("financial", {})
        if financial.get("success"):
            summary = financial.get("summary", {})
            content += f"- **Total Revenue**: ${summary.get('total_revenue', 0):,.2f}\n"
            content += f"- **Pending Revenue**: ${summary.get('pending_revenue', 0):,.2f}\n"
            content += f"- **Invoice Count**: {summary.get('invoice_count', 0)}\n"
            content += f"- **Posted Invoices**: {summary.get('posted_invoices', 0)}\n"
            content += f"- **Draft Invoices**: {summary.get('draft_invoices', 0)}\n"
            content += f"- **Customer Count**: {summary.get('customer_count', 0)}\n\n"
        else:
            content += f"⚠️ Financial data unavailable: {financial.get('message', 'Unknown error')}\n\n"

        # Marketing Performance
        content += "## Marketing Performance\n\n"
        marketing = data.get("marketing", {})
        if marketing.get("success"):
            # Twitter
            twitter = marketing.get("twitter", {}).get("summary", {})
            content += "### Twitter\n"
            content += f"- **Total Tweets**: {twitter.get('total_tweets', 0)}\n"
            content += f"- **Impressions**: {twitter.get('total_impressions', 0):,}\n"
            content += f"- **Engagements**: {twitter.get('total_engagements', 0)}\n"
            content += f"- **Engagement Rate**: {twitter.get('engagement_rate', 0):.1f}%\n\n"

            # Instagram
            instagram = marketing.get("instagram", {}).get("summary", {})
            content += "### Instagram\n"
            content += f"- **Total Posts**: {instagram.get('total_posts', 0)}\n"
            content += f"- **Reach**: {instagram.get('total_reach', 0):,}\n"
            content += f"- **Likes**: {instagram.get('total_likes', 0)}\n"
            content += f"- **Engagement Rate**: {instagram.get('engagement_rate', 0):.1f}%\n\n"

            # Facebook
            facebook = marketing.get("facebook", {}).get("summary", {})
            content += "### Facebook\n"
            content += f"- **Total Posts**: {facebook.get('total_posts', 0)}\n"
            content += f"- **Reach**: {facebook.get('total_reach', 0):,}\n"
            content += f"- **Engagement**: {facebook.get('total_engagement', 0)}\n\n"
        else:
            content += f"⚠️ Marketing data unavailable: {marketing.get('message', 'Unknown error')}\n\n"

        # Business Operations
        content += "## Business Operations\n\n"
        operations = data.get("operations", {})
        if operations.get("success"):
            content += f"- **Completed Tasks**: {operations.get('completed_tasks', 0)}\n\n"

        # Risk Alerts
        content += "## Risk Alerts\n\n"
        risks = data.get("risks", {})
        if risks.get("risk_count", 0) > 0:
            for risk in risks.get("risks", []):
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk["severity"], "⚪")
                content += f"{severity_emoji} **{risk['category'].title()}**: {risk['message']}\n"
        else:
            content += "✅ No significant risks identified\n"

        content += "\n---\n\n"
        content += "## Action Recommendations\n\n"
        content += "1. Review pending approval items\n"
        content += "2. Follow up on high-engagement social media posts\n"
        content += "3. Monitor draft invoices for completion\n\n"

        content += "---\n\n"
        content += "*Generated by Gold Tier Autonomous AI Employee*\n"

        return content


if __name__ == "__main__":
    # Test CEO briefing generation
    generator = CEOBriefingGenerator()
    result = generator.generate_briefing(week_offset=0)
    print(f"Briefing generation result: {json.dumps(result, indent=2)}")
