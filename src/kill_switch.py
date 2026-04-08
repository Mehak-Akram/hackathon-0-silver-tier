"""
Kill switch mechanism for Gold Tier Autonomous AI Employee.

Provides emergency stop functionality to halt autonomous operations
immediately when triggered by file presence or API call.
"""
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime, timezone
from dataclasses import dataclass
import asyncio
import structlog


logger = structlog.get_logger("kill_switch")


@dataclass
class KillSwitchEvent:
    """Record of kill switch activation."""
    triggered_at: datetime
    trigger_method: str  # "file", "api", "manual"
    reason: Optional[str]
    triggered_by: Optional[str]

    def to_dict(self):
        """Convert to dictionary for logging."""
        return {
            "triggered_at": self.triggered_at.isoformat(),
            "trigger_method": self.trigger_method,
            "reason": self.reason,
            "triggered_by": self.triggered_by
        }


class KillSwitch:
    """
    Emergency stop mechanism for autonomous operations.

    Monitors for kill switch activation via:
    1. File presence (KILL_SWITCH file in vault root)
    2. API call (set_active(False))
    3. Manual trigger (trigger() method)

    When activated, all autonomous operations should check is_active()
    and halt immediately if False.
    """

    def __init__(
        self,
        vault_root: Path,
        kill_switch_filename: str = "KILL_SWITCH",
        check_interval: float = 1.0
    ):
        """
        Initialize kill switch.

        Args:
            vault_root: Root directory of the vault
            kill_switch_filename: Name of kill switch file
            check_interval: Interval in seconds to check for file
        """
        self.vault_root = Path(vault_root)
        self.kill_switch_file = self.vault_root / kill_switch_filename
        self.check_interval = check_interval

        self._active = True
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._callbacks: List[Callable] = []
        self._activation_event: Optional[KillSwitchEvent] = None

        logger.info(
            "kill_switch_initialized",
            vault_root=str(self.vault_root),
            kill_switch_file=str(self.kill_switch_file)
        )

    def is_active(self) -> bool:
        """
        Check if system is active (not killed).

        Returns:
            True if active, False if kill switch triggered
        """
        return self._active

    def trigger(
        self,
        reason: Optional[str] = None,
        triggered_by: Optional[str] = None,
        method: str = "manual"
    ):
        """
        Manually trigger kill switch.

        Args:
            reason: Reason for triggering
            triggered_by: Who/what triggered it
            method: Trigger method ("manual", "api", "file")
        """
        if not self._active:
            logger.warning("kill_switch_already_triggered")
            return

        self._active = False
        self._activation_event = KillSwitchEvent(
            triggered_at=datetime.now(timezone.utc),
            trigger_method=method,
            reason=reason,
            triggered_by=triggered_by
        )

        logger.critical(
            "kill_switch_triggered",
            **self._activation_event.to_dict()
        )

        # Execute callbacks
        self._execute_callbacks()

    def set_active(self, active: bool, reason: Optional[str] = None):
        """
        Set kill switch state via API.

        Args:
            active: True to activate system, False to kill
            reason: Reason for state change
        """
        if active and not self._active:
            # Reactivating system
            self._active = True
            self._activation_event = None

            logger.warning(
                "kill_switch_reactivated",
                reason=reason
            )

        elif not active and self._active:
            # Triggering kill switch
            self.trigger(
                reason=reason,
                triggered_by="api",
                method="api"
            )

    def register_callback(self, callback: Callable):
        """
        Register callback to execute when kill switch triggered.

        Args:
            callback: Callable to execute (no arguments)
        """
        self._callbacks.append(callback)
        logger.debug(
            "kill_switch_callback_registered",
            callback_count=len(self._callbacks)
        )

    def _execute_callbacks(self):
        """Execute all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(
                    "kill_switch_callback_failed",
                    error_type=type(e).__name__,
                    error=str(e)
                )

    async def start_monitoring(self):
        """
        Start monitoring for kill switch file.

        Checks for file presence at regular intervals.
        """
        if self._monitoring:
            logger.warning("kill_switch_monitoring_already_started")
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

        logger.info(
            "kill_switch_monitoring_started",
            check_interval=self.check_interval
        )

    async def stop_monitoring(self):
        """Stop monitoring for kill switch file."""
        if not self._monitoring:
            return

        self._monitoring = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("kill_switch_monitoring_stopped")

    async def _monitor_loop(self):
        """Monitor loop that checks for kill switch file."""
        try:
            while self._monitoring:
                # Check if kill switch file exists
                if self.kill_switch_file.exists():
                    # Read reason from file if present
                    reason = None
                    try:
                        content = self.kill_switch_file.read_text(encoding="utf-8").strip()
                        if content:
                            reason = content
                    except Exception as e:
                        logger.warning(
                            "kill_switch_file_read_failed",
                            error=str(e)
                        )

                    # Trigger kill switch
                    self.trigger(
                        reason=reason or "Kill switch file detected",
                        triggered_by="file_monitor",
                        method="file"
                    )

                    # Stop monitoring after trigger
                    break

                # Wait before next check
                await asyncio.sleep(self.check_interval)

        except asyncio.CancelledError:
            logger.debug("kill_switch_monitor_cancelled")
            raise

        except Exception as e:
            logger.error(
                "kill_switch_monitor_error",
                error_type=type(e).__name__,
                error=str(e)
            )

    def get_activation_event(self) -> Optional[KillSwitchEvent]:
        """
        Get kill switch activation event.

        Returns:
            KillSwitchEvent if triggered, None otherwise
        """
        return self._activation_event

    def create_kill_switch_file(self, reason: Optional[str] = None):
        """
        Create kill switch file to trigger via file system.

        Args:
            reason: Reason to write to file
        """
        content = reason or "Kill switch activated"
        self.kill_switch_file.write_text(content, encoding="utf-8")

        logger.warning(
            "kill_switch_file_created",
            path=str(self.kill_switch_file),
            reason=content
        )

    def remove_kill_switch_file(self):
        """Remove kill switch file if it exists."""
        if self.kill_switch_file.exists():
            self.kill_switch_file.unlink()

            logger.info(
                "kill_switch_file_removed",
                path=str(self.kill_switch_file)
            )

    def check_and_raise(self):
        """
        Check if kill switch is active and raise exception if not.

        Raises:
            RuntimeError: If kill switch triggered
        """
        if not self._active:
            event = self._activation_event
            raise RuntimeError(
                f"Kill switch triggered: {event.reason if event else 'Unknown reason'}"
            )


# Global kill switch instance (initialized by application)
kill_switch: Optional[KillSwitch] = None


def initialize_kill_switch(vault_root: Path) -> KillSwitch:
    """
    Initialize global kill switch instance.

    Args:
        vault_root: Root directory of the vault

    Returns:
        KillSwitch instance
    """
    global kill_switch
    kill_switch = KillSwitch(vault_root)
    return kill_switch


def get_kill_switch() -> KillSwitch:
    """
    Get global kill switch instance.

    Returns:
        KillSwitch instance

    Raises:
        RuntimeError: If kill switch not initialized
    """
    if kill_switch is None:
        raise RuntimeError("Kill switch not initialized. Call initialize_kill_switch() first.")
    return kill_switch
