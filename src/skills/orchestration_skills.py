"""
Orchestration Skills for Gold Tier Autonomous AI Employee.

Provides multi-skill workflow orchestration capabilities.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional
from src.base_skill import BaseSkill
from src.retry_logic import with_retry
from shared.logging_config import get_logger

logger = get_logger(__name__, "orchestration-skills.log")


class MultiStepWorkflowSkill(BaseSkill):
    """
    Skill for orchestrating multiple skills in sequence.

    Risk Level: Varies based on constituent skills
    """

    def __init__(self, skills: Optional[Dict[str, BaseSkill]] = None):
        """
        Initialize multi-step workflow skill.

        Args:
            skills: Dictionary of available skills {name: skill_instance}
        """
        super().__init__(
            name="multi_step_workflow",
            description="Execute multiple skills in sequence",
            risk_level="medium"
        )
        self.skills = skills or {}

    def register_skill(self, skill: BaseSkill) -> None:
        """
        Register a skill for use in workflows.

        Args:
            skill: Skill instance to register
        """
        self.skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")

    @with_retry(max_attempts=2)
    async def execute(self, steps: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Execute multi-step workflow.

        Args:
            steps: List of step definitions, each containing:
                - skill: Skill name to execute
                - params: Parameters for the skill
                - on_error: Action on error (continue/stop/retry)

        Returns:
            Result dictionary with all step results
        """
        logger.info(f"Executing multi-step workflow with {len(steps)} steps")

        results = []
        failed_steps = []

        try:
            for i, step in enumerate(steps, 1):
                skill_name = step.get("skill")
                params = step.get("params", {})
                on_error = step.get("on_error", "stop")

                logger.info(f"Step {i}/{len(steps)}: Executing {skill_name}")

                # Get skill
                skill = self.skills.get(skill_name)
                if not skill:
                    error_msg = f"Skill not found: {skill_name}"
                    logger.error(error_msg)
                    results.append({
                        "step": i,
                        "skill": skill_name,
                        "success": False,
                        "error": "SKILL_NOT_FOUND",
                        "message": error_msg
                    })
                    failed_steps.append(i)

                    if on_error == "stop":
                        break
                    continue

                # Execute skill
                try:
                    result = await skill.execute(**params)
                    results.append({
                        "step": i,
                        "skill": skill_name,
                        "success": result.get("success", False),
                        "result": result
                    })

                    if not result.get("success"):
                        failed_steps.append(i)
                        logger.warning(f"Step {i} failed: {result.get('message')}")

                        if on_error == "stop":
                            logger.error(f"Stopping workflow at step {i}")
                            break

                except Exception as e:
                    logger.error(f"Step {i} error: {e}", exc_info=True)
                    results.append({
                        "step": i,
                        "skill": skill_name,
                        "success": False,
                        "error": str(e)
                    })
                    failed_steps.append(i)

                    if on_error == "stop":
                        break

            # Workflow summary
            success = len(failed_steps) == 0
            return {
                "success": success,
                "total_steps": len(steps),
                "completed_steps": len(results),
                "failed_steps": failed_steps,
                "results": results
            }

        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "WORKFLOW_EXECUTION_ERROR",
                "message": str(e),
                "results": results
            }


class InvoiceCreationWorkflowSkill(BaseSkill):
    """
    Skill for complete invoice creation workflow.

    NOTE: This skill is deprecated as no accounting system is configured.

    Risk Level: High (financial transaction)
    """

    def __init__(self):
        """Initialize invoice creation workflow skill."""
        super().__init__(
            name="invoice_creation_workflow",
            description="Complete invoice creation workflow (deprecated - no accounting system)",
            risk_level="high"
        )

    @with_retry(max_attempts=2)
    async def execute(self, customer_name: str, customer_email: str,
                     amount: float, description: str,
                     notify_customer: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Execute invoice creation workflow.

        Returns:
            Error result - no accounting system configured
        """
        logger.warning("Invoice creation workflow called but no accounting system is configured")
        return {
            "success": False,
            "error": "NO_ACCOUNTING_SYSTEM",
            "message": "No accounting system configured. This workflow is deprecated."
        }


class WeeklyCEOBriefingWorkflowSkill(BaseSkill):
    """
    Skill for complete weekly CEO briefing workflow.

    Workflow: Generate briefing → Send via email → Log completion

    Risk Level: Medium (executive communication)
    """

    def __init__(self):
        """Initialize weekly CEO briefing workflow skill."""
        super().__init__(
            name="weekly_ceo_briefing_workflow",
            description="Complete weekly CEO briefing workflow",
            risk_level="medium"
        )

    @with_retry(max_attempts=2)
    async def execute(self, ceo_email: str, week_offset: int = 0,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute weekly CEO briefing workflow.

        Args:
            ceo_email: CEO email address
            week_offset: Week offset (0=current, -1=last week)

        Returns:
            Result dictionary with workflow status
        """
        logger.info(f"Starting weekly CEO briefing workflow for {ceo_email}")

        workflow_results = []

        try:
            # Step 1: Generate briefing
            from src.skills.reporting_skills import GenerateCEOBriefingSkill
            briefing_skill = GenerateCEOBriefingSkill()

            logger.info("Step 1: Generating CEO briefing")
            briefing_result = await briefing_skill.execute(week_offset=week_offset)
            workflow_results.append({"step": "generate_briefing", "result": briefing_result})

            if not briefing_result.get("success"):
                return {
                    "success": False,
                    "error": "BRIEFING_GENERATION_FAILED",
                    "message": briefing_result.get("message"),
                    "workflow_results": workflow_results
                }

            # Step 2: Send briefing via email
            from src.skills.email_skills import SendCEOBriefingSkill
            email_skill = SendCEOBriefingSkill()

            logger.info("Step 2: Sending CEO briefing via email")
            email_result = await email_skill.execute(
                briefing_file_path=briefing_result.get("file_path"),
                recipient=ceo_email,
                week_start=briefing_result.get("week_start"),
                week_end=briefing_result.get("week_end")
            )
            workflow_results.append({"step": "send_briefing", "result": email_result})

            if not email_result.get("success"):
                logger.warning(f"Briefing email failed: {email_result.get('message')}")
                # Don't fail workflow if email fails - briefing file still exists

            logger.info("Weekly CEO briefing workflow completed successfully")
            return {
                "success": True,
                "message": "Weekly CEO briefing workflow completed",
                "briefing_file": briefing_result.get("file_path"),
                "email_sent": email_result.get("success", False),
                "workflow_results": workflow_results
            }

        except Exception as e:
            logger.error(f"Weekly CEO briefing workflow error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "WORKFLOW_ERROR",
                "message": str(e),
                "workflow_results": workflow_results
            }


class SocialMediaCampaignWorkflowSkill(BaseSkill):
    """
    Skill for social media campaign workflow.

    Workflow: Fetch metrics → Generate report → Send summary

    Risk Level: Low (read-only with notification)
    """

    def __init__(self):
        """Initialize social media campaign workflow skill."""
        super().__init__(
            name="social_media_campaign_workflow",
            description="Social media campaign analysis workflow",
            risk_level="low"
        )

    @with_retry(max_attempts=2)
    async def execute(self, recipient_email: str, days: int = 7,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute social media campaign workflow.

        Args:
            recipient_email: Report recipient email
            days: Number of days to analyze

        Returns:
            Result dictionary with workflow status
        """
        logger.info(f"Starting social media campaign workflow for {days} days")

        workflow_results = []

        try:
            # Step 1: Generate marketing report
            from src.skills.reporting_skills import GenerateMarketingReportSkill
            report_skill = GenerateMarketingReportSkill()

            logger.info("Step 1: Generating marketing report")
            report_result = await report_skill.execute(
                report_type="weekly",
                days=days
            )
            workflow_results.append({"step": "generate_report", "result": report_result})

            if not report_result.get("success"):
                return {
                    "success": False,
                    "error": "REPORT_GENERATION_FAILED",
                    "message": report_result.get("message"),
                    "workflow_results": workflow_results
                }

            # Step 2: Send report summary via email
            from src.skills.email_skills import SendNotificationSkill
            notification_skill = SendNotificationSkill()

            summary = report_result.get("summary", {})
            logger.info("Step 2: Sending report summary")
            email_result = await notification_skill.execute(
                to=recipient_email,
                notification_type="info",
                message=f"Social Media Campaign Report - Last {days} days",
                details={
                    "total_engagement": summary.get("total_engagement", 0),
                    "total_reach": summary.get("total_reach", 0),
                    "platforms_active": summary.get("platforms_active", 0)
                }
            )
            workflow_results.append({"step": "send_summary", "result": email_result})

            logger.info("Social media campaign workflow completed successfully")
            return {
                "success": True,
                "message": "Social media campaign workflow completed",
                "report": report_result,
                "workflow_results": workflow_results
            }

        except Exception as e:
            logger.error(f"Social media campaign workflow error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "WORKFLOW_ERROR",
                "message": str(e),
                "workflow_results": workflow_results
            }


# Export all orchestration skills
__all__ = [
    "MultiStepWorkflowSkill",
    "InvoiceCreationWorkflowSkill",
    "WeeklyCEOBriefingWorkflowSkill",
    "SocialMediaCampaignWorkflowSkill"
]
