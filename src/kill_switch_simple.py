"""
Simplified Kill Switch - No External Dependencies.

Provides emergency stop functionality without structlog.
"""
from pathlib import Path
from datetime import datetime


class KillSwitch:
    """Simplified emergency stop mechanism."""

    def __init__(self, vault_path: Path = Path(".")):
        """Initialize kill switch."""
        self.vault_path = Path(vault_path)
        self.kill_file = self.vault_path / "STOP"

    def is_active(self) -> bool:
        """
        Check if kill switch is active.

        Returns:
            True if system should stop, False if system can run
        """
        return self.kill_file.exists()

    def activate(self, reason: str = "Manual activation"):
        """
        Activate kill switch.

        Args:
            reason: Reason for activation
        """
        with open(self.kill_file, 'w') as f:
            f.write(f"Kill switch activated at {datetime.now().isoformat()}\n")
            f.write(f"Reason: {reason}\n")

    def deactivate(self):
        """Deactivate kill switch."""
        if self.kill_file.exists():
            self.kill_file.unlink()

    def check_and_raise(self):
        """Check kill switch and raise exception if active."""
        if self.is_active():
            raise RuntimeError("Kill switch is active - system halted")
