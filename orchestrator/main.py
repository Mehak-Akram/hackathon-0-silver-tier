"""
Main Orchestrator for Gold Tier Autonomous AI Employee.

Runs the Ralph Wiggum Loop continuously, monitoring for tasks and
executing them autonomously.
"""
import asyncio
import signal
from pathlib import Path
from datetime import datetime, time
from typing import Optional

import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from orchestrator.ralph_loop import RalphWiggumLoop, Task
from reporting.ceo_briefing import CEOBriefingGenerator

logger = get_logger(__name__, "main-orchestrator.log")


class MainOrchestrator:
    """
    Main orchestrator for Gold Tier Autonomous AI Employee.

    Runs continuously, monitoring for tasks and executing scheduled operations.
    """

    def __init__(self):
        """Initialize main orchestrator."""
        self.ralph_loop = RalphWiggumLoop()
        self.ceo_briefing_generator = CEOBriefingGenerator()
        self.vault_path = Path("E:/AI_Employee_Vault")
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.running = False

        logger.info("Main Orchestrator initialized")

    async def start(self):
        """Start the orchestrator loop."""
        self.running = True
        logger.info("Main Orchestrator starting...")

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start background tasks
        tasks = [
            asyncio.create_task(self._task_monitor_loop()),
            asyncio.create_task(self._scheduled_operations_loop())
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Orchestrator tasks cancelled")
        finally:
            self.running = False
            logger.info("Main Orchestrator stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def _task_monitor_loop(self):
        """
        Monitor for new tasks in Needs_Action folder.

        Checks every 30 seconds for new task files.
        """
        logger.info("Task monitor loop started")

        while self.running:
            try:
                await self._check_for_new_tasks()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in task monitor loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait longer on error

    async def _scheduled_operations_loop(self):
        """
        Run scheduled operations (CEO briefing, etc.).

        Checks every minute for scheduled operations.
        """
        logger.info("Scheduled operations loop started")

        last_briefing_date = None

        while self.running:
            try:
                now = datetime.now()

                # Check if it's Monday at 8:00 AM (CEO briefing time)
                if (now.weekday() == 0 and  # Monday
                    now.hour == 8 and
                    now.minute < 5 and  # Within first 5 minutes
                    last_briefing_date != now.date()):

                    logger.info("Triggering weekly CEO briefing generation")
                    await self._generate_ceo_briefing()
                    last_briefing_date = now.date()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in scheduled operations loop: {e}", exc_info=True)
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _check_for_new_tasks(self):
        """Check for new tasks in Needs_Action folder."""
        if not self.needs_action_path.exists():
            return

        task_files = list(self.needs_action_path.glob("*.md"))

        if not task_files:
            return

        logger.info(f"Found {len(task_files)} tasks in Needs_Action")

        for task_file in task_files:
            try:
                # Parse task file
                task = await self._parse_task_file(task_file)

                if task:
                    logger.info(f"Executing task: {task.task_id}")

                    # Execute task with Ralph Wiggum Loop
                    result = await self.ralph_loop.execute_task(task)

                    # Move task file based on result
                    if result.get("status") == "completed":
                        done_path = self.vault_path / "Done"
                        done_path.mkdir(exist_ok=True)
                        task_file.rename(done_path / task_file.name)
                        logger.info(f"Task completed and moved to Done: {task.task_id}")
                    elif result.get("status") == "escalated":
                        # Already handled by Ralph loop (moved to Pending_Approval)
                        task_file.unlink()  # Remove from Needs_Action
                        logger.info(f"Task escalated: {task.task_id}")

            except Exception as e:
                logger.error(f"Error processing task file {task_file}: {e}", exc_info=True)

    async def _parse_task_file(self, task_file: Path) -> Optional[Task]:
        """
        Parse task file into Task object.

        Args:
            task_file: Path to task markdown file

        Returns:
            Task object or None if parsing fails
        """
        try:
            content = task_file.read_text(encoding='utf-8')

            # Simple parsing - extract title and content
            lines = content.strip().split('\n')
            title = lines[0].replace('#', '').strip() if lines else task_file.stem

            # Create task
            task = Task(
                task_id=task_file.stem,
                description=title,
                domain="general"
            )

            # For now, create a simple single-step task
            # In production, this would parse the task file for detailed steps
            task.add_step(
                description=title,
                action="execute_task",
                parameters={"content": content}
            )

            return task

        except Exception as e:
            logger.error(f"Failed to parse task file {task_file}: {e}", exc_info=True)
            return None

    async def _generate_ceo_briefing(self):
        """Generate and deliver CEO briefing."""
        try:
            logger.info("Generating CEO briefing")

            result = self.ceo_briefing_generator.generate_briefing(week_offset=0)

            if result.get("success"):
                logger.info(f"CEO briefing generated: {result.get('file_path')}")

                # Send briefing via email
                try:
                    import os
                    from src.skills.email_skills import SendCEOBriefingSkill

                    ceo_email = os.getenv("CEO_EMAIL")
                    if ceo_email:
                        email_skill = SendCEOBriefingSkill()
                        email_result = await email_skill.execute(
                            briefing_file_path=result.get('file_path'),
                            recipient=ceo_email,
                            week_start=result.get('week_start'),
                            week_end=result.get('week_end')
                        )

                        if email_result.get("success"):
                            logger.info(f"CEO briefing delivered via email to {ceo_email}")
                        else:
                            logger.warning(f"CEO briefing email failed: {email_result.get('message')}")
                    else:
                        logger.warning("CEO_EMAIL not configured, skipping email delivery")

                except Exception as email_error:
                    logger.error(f"Error sending CEO briefing email: {email_error}", exc_info=True)
                    # Don't fail the whole operation if email fails

            else:
                logger.error(f"CEO briefing generation failed: {result.get('message')}")

        except Exception as e:
            logger.error(f"Error generating CEO briefing: {e}", exc_info=True)


async def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("Gold Tier Autonomous AI Employee - Starting")
    logger.info("=" * 80)

    orchestrator = MainOrchestrator()

    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in main orchestrator: {e}", exc_info=True)
        raise
    finally:
        logger.info("Gold Tier Autonomous AI Employee - Stopped")


if __name__ == "__main__":
    asyncio.run(main())
