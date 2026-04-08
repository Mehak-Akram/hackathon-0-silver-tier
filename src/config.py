"""
Configuration management for Gold Tier Autonomous AI Employee.

Handles environment variable loading, validation, and configuration
access with type safety and defaults.
"""
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import os
from enum import Enum
import structlog


logger = structlog.get_logger("config")


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


@dataclass
class FacebookConfig:
    """Facebook API configuration."""
    access_token: str
    page_id: str

    @classmethod
    def from_env(cls) -> "FacebookConfig":
        """Load from environment variables."""
        return cls(
            access_token=os.getenv("FB_ACCESS_TOKEN", ""),
            page_id=os.getenv("FB_PAGE_ID", "")
        )

    def is_configured(self) -> bool:
        """Check if configuration is complete."""
        return bool(self.access_token and self.page_id)


@dataclass
class InstagramConfig:
    """Instagram API configuration."""
    access_token: str
    account_id: str

    @classmethod
    def from_env(cls) -> "InstagramConfig":
        """Load from environment variables."""
        return cls(
            access_token=os.getenv("IG_ACCESS_TOKEN", ""),
            account_id=os.getenv("IG_ACCOUNT_ID", "")
        )

    def is_configured(self) -> bool:
        """Check if configuration is complete."""
        return bool(self.access_token and self.account_id)


@dataclass
class TwitterConfig:
    """Twitter API configuration."""
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str

    @classmethod
    def from_env(cls) -> "TwitterConfig":
        """Load from environment variables."""
        return cls(
            api_key=os.getenv("TWITTER_API_KEY", ""),
            api_secret=os.getenv("TWITTER_API_SECRET", ""),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        )

    def is_configured(self) -> bool:
        """Check if configuration is complete."""
        return bool(
            self.api_key and
            self.api_secret and
            self.access_token and
            self.access_token_secret
        )


@dataclass
class EmailConfig:
    """Email SMTP configuration."""
    host: str
    port: int
    username: str
    password: str
    ceo_email: str

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Load from environment variables."""
        return cls(
            host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            ceo_email=os.getenv("CEO_EMAIL", "")
        )

    def is_configured(self) -> bool:
        """Check if configuration is complete."""
        return bool(
            self.host and
            self.username and
            self.password and
            self.ceo_email
        )


@dataclass
class RiskEngineConfig:
    """Risk engine configuration."""
    high_threshold: float
    medium_threshold: float
    max_retries: int
    circuit_breaker_threshold: int
    circuit_breaker_timeout: int

    @classmethod
    def from_env(cls) -> "RiskEngineConfig":
        """Load from environment variables."""
        return cls(
            high_threshold=float(os.getenv("RISK_HIGH_THRESHOLD", "0.7")),
            medium_threshold=float(os.getenv("RISK_MEDIUM_THRESHOLD", "0.4")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            circuit_breaker_threshold=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
            circuit_breaker_timeout=int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "300"))
        )


@dataclass
class AutonomousLoopConfig:
    """Autonomous loop configuration."""
    enabled: bool
    loop_interval_seconds: int
    ceo_briefing_day: str
    ceo_briefing_hour: int

    @classmethod
    def from_env(cls) -> "AutonomousLoopConfig":
        """Load from environment variables."""
        enabled_str = os.getenv("ENABLE_AUTONOMOUS_LOOP", "false").lower()
        return cls(
            enabled=enabled_str in ("true", "1", "yes"),
            loop_interval_seconds=int(os.getenv("LOOP_INTERVAL_SECONDS", "60")),
            ceo_briefing_day=os.getenv("CEO_BRIEFING_DAY", "monday").lower(),
            ceo_briefing_hour=int(os.getenv("CEO_BRIEFING_HOUR", "8"))
        )


@dataclass
class PathConfig:
    """File system path configuration."""
    vault_root: Path
    inbox: Path
    needs_action: Path
    plans: Path
    done: Path
    pending_approval: Path
    approved: Path
    rejected: Path
    audit_logs: Path
    reports: Path
    ceo_briefings: Path

    @classmethod
    def from_vault_root(cls, vault_root: Optional[Path] = None) -> "PathConfig":
        """
        Create path configuration from vault root.

        Args:
            vault_root: Root directory of the vault (defaults to current directory)
        """
        if vault_root is None:
            vault_root = Path.cwd()
        else:
            vault_root = Path(vault_root)

        return cls(
            vault_root=vault_root,
            inbox=vault_root / "Inbox",
            needs_action=vault_root / "Needs_Action",
            plans=vault_root / "Plans",
            done=vault_root / "Done",
            pending_approval=vault_root / "Pending_Approval",
            approved=vault_root / "Approved",
            rejected=vault_root / "Rejected",
            audit_logs=vault_root / "Audit_Logs",
            reports=vault_root / "Reports",
            ceo_briefings=vault_root / "Reports" / "CEO_Briefings"
        )

    def ensure_directories(self):
        """Create all directories if they don't exist."""
        for path in [
            self.inbox,
            self.needs_action,
            self.plans,
            self.done,
            self.pending_approval,
            self.approved,
            self.rejected,
            self.audit_logs,
            self.reports,
            self.ceo_briefings
        ]:
            path.mkdir(parents=True, exist_ok=True)


class Config:
    """
    Central configuration manager.

    Loads and validates all configuration from environment variables.
    """

    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            env_file: Optional path to .env file
        """
        # Load .env file if provided
        if env_file and env_file.exists():
            self._load_env_file(env_file)

        # Load all configurations
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        self.facebook = FacebookConfig.from_env()
        self.instagram = InstagramConfig.from_env()
        self.twitter = TwitterConfig.from_env()
        self.email = EmailConfig.from_env()
        self.risk_engine = RiskEngineConfig.from_env()
        self.autonomous_loop = AutonomousLoopConfig.from_env()
        self.paths = PathConfig.from_vault_root(os.getenv("VAULT_ROOT"))

        # Ensure directories exist
        self.paths.ensure_directories()

        logger.info(
            "configuration_loaded",
            environment=self.environment.value,
            log_level=self.log_level,
            autonomous_loop_enabled=self.autonomous_loop.enabled,
            vault_root=str(self.paths.vault_root)
        )

    def _load_env_file(self, env_file: Path):
        """
        Load environment variables from .env file.

        Args:
            env_file: Path to .env file
        """
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue

                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

            logger.info("env_file_loaded", path=str(env_file))

        except Exception as e:
            logger.warning(
                "env_file_load_failed",
                path=str(env_file),
                error=str(e)
            )

    def validate(self) -> Dict[str, list]:
        """
        Validate configuration completeness.

        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []

        # Check email configuration
        if not self.email.is_configured():
            warnings.append("Email configuration incomplete - CEO briefing delivery disabled")

        # Check social media configurations
        if not self.facebook.is_configured():
            warnings.append("Facebook configuration incomplete - Facebook integration disabled")
        if not self.instagram.is_configured():
            warnings.append("Instagram configuration incomplete - Instagram integration disabled")
        if not self.twitter.is_configured():
            warnings.append("Twitter configuration incomplete - Twitter integration disabled")

        # Check autonomous loop
        if self.autonomous_loop.enabled:
            if not self.email.is_configured():
                errors.append("Autonomous loop enabled but email not configured - cannot send CEO briefings")

        # Log validation results
        if errors:
            logger.error("configuration_validation_failed", errors=errors)
        if warnings:
            logger.warning("configuration_validation_warnings", warnings=warnings)

        return {"errors": errors, "warnings": warnings}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary (for logging/debugging).

        Sensitive values are masked.
        """
        return {
            "environment": self.environment.value,
            "log_level": self.log_level,
            "facebook": {
                "configured": self.facebook.is_configured()
            },
            "instagram": {
                "configured": self.instagram.is_configured()
            },
            "twitter": {
                "configured": self.twitter.is_configured()
            },
            "email": {
                "configured": self.email.is_configured(),
                "ceo_email": self.email.ceo_email
            },
            "autonomous_loop": {
                "enabled": self.autonomous_loop.enabled,
                "loop_interval_seconds": self.autonomous_loop.loop_interval_seconds,
                "ceo_briefing_day": self.autonomous_loop.ceo_briefing_day,
                "ceo_briefing_hour": self.autonomous_loop.ceo_briefing_hour
            },
            "paths": {
                "vault_root": str(self.paths.vault_root)
            }
        }


# Global configuration instance
config: Optional[Config] = None


def load_config(env_file: Optional[Path] = None) -> Config:
    """
    Load global configuration.

    Args:
        env_file: Optional path to .env file

    Returns:
        Config instance
    """
    global config
    config = Config(env_file)
    return config


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Config instance

    Raises:
        RuntimeError: If configuration not loaded
    """
    if config is None:
        raise RuntimeError("Configuration not loaded. Call load_config() first.")
    return config
