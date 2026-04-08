"""
Models package for Gold Tier Autonomous AI Employee.

Contains all data models and entities used throughout the system.
"""

# Import all models
from src.models.task import Task, TaskStatus, TaskDomain, TaskPriority
from src.models.execution_step import ExecutionStep, StepStatus
from src.models.ceo_briefing import CEOBriefing, BriefingStatus, DataSourceStatus
from src.models.mcp_connection import MCPConnection, MCPServerType, ConnectionStatus, HealthStatus
from src.models.financial_transaction import (
    FinancialTransaction,
    TransactionType,
    TransactionStatus,
    PaymentMethod
)
from src.models.social_post import SocialMediaPost, SocialPlatform, PostStatus, PostType
from src.models.error_log import ErrorLog, ErrorSeverity, ErrorCategory, ResolutionStatus


__all__ = [
    # Task models
    "Task",
    "TaskStatus",
    "TaskDomain",
    "TaskPriority",

    # Execution step models
    "ExecutionStep",
    "StepStatus",

    # CEO Briefing models
    "CEOBriefing",
    "BriefingStatus",
    "DataSourceStatus",

    # MCP Connection models
    "MCPConnection",
    "MCPServerType",
    "ConnectionStatus",
    "HealthStatus",

    # Financial models
    "FinancialTransaction",
    "TransactionType",
    "TransactionStatus",
    "PaymentMethod",

    # Social media models
    "SocialMediaPost",
    "SocialPlatform",
    "PostStatus",
    "PostType",

    # Error log models
    "ErrorLog",
    "ErrorSeverity",
    "ErrorCategory",
    "ResolutionStatus",
]
