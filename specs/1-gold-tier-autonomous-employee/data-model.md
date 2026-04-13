# Data Model: Gold Tier Autonomous AI Employee

**Feature**: Gold Tier Autonomous AI Employee
**Date**: 2026-03-12
**Source**: Extracted from spec.md and plan.md

## Overview

This document defines the core entities and their relationships for the Gold Tier autonomous AI employee system. All entities are represented as Python dataclasses with Pydantic validation.

---

## Core Entities

### Task

Represents a unit of work assigned to the AI Employee.

**Attributes**:
- `id`: str - Unique task identifier (UUID)
- `description`: str - Natural language description of the task
- `domain`: TaskDomain - Enum: personal, business, accounting, marketing
- `priority`: int - Priority level (1=highest)
- `status`: TaskStatus - Enum: pending, in_progress, completed, failed
- `assigned_date`: datetime - When task was created
- `due_date`: Optional[datetime] - When task should be completed
- `execution_history`: List[ExecutionStep] - Steps taken to complete task
- `result`: Optional[str] - Final result or output
- `error_message`: Optional[str] - Error details if failed
- `file_path`: str - Path to task markdown file in vault

**Relationships**:
- One-to-many with ExecutionStep (task has multiple steps)
- Referenced by ErrorLog

**Validation Rules**:
- `domain` must be one of: personal, business, accounting, marketing
- `status` must be one of: pending, in_progress, completed, failed
- `description` must not be empty
- `assigned_date` must be <= `due_date` if due_date is set

**State Transitions**:
- pending → in_progress (when Ralph Wiggum Loop picks up task)
- in_progress → completed (when all steps succeed)
- in_progress → failed (when max retries exceeded or unrecoverable error)
- failed → in_progress (when user manually retries)

---

### ExecutionStep

Represents a single step in a multi-step task execution.

**Attributes**:
- `id`: str - Unique step identifier (UUID)
- `task_id`: str - Parent task ID
- `step_number`: int - Order in execution sequence (1, 2, 3...)
- `description`: str - What this step does
- `status`: StepStatus - Enum: pending, in_progress, completed, failed, skipped
- `retry_count`: int - Number of retry attempts (default: 0)
- `max_retries`: int - Maximum retry attempts allowed (default: 3)
- `error_message`: Optional[str] - Error details if failed
- `result_data`: Optional[Dict[str, Any]] - Output data from this step
- `started_at`: Optional[datetime] - When step execution began
- `completed_at`: Optional[datetime] - When step finished
- `skill_invoked`: Optional[str] - Name of skill used for this step

**Relationships**:
- Many-to-one with Task (multiple steps belong to one task)

**Validation Rules**:
- `step_number` must be > 0
- `retry_count` must be <= `max_retries`
- `status` must be one of: pending, in_progress, completed, failed, skipped
- `completed_at` must be >= `started_at` if both are set

**State Transitions**:
- pending → in_progress (when step execution begins)
- in_progress → completed (when step succeeds)
- in_progress → failed (when step fails and retry_count >= max_retries)
- failed → in_progress (when retry attempted and retry_count < max_retries)
- pending → skipped (when previous step fails and this step is conditional)

---

### CEOBriefing

Represents a weekly executive summary report.

**Attributes**:
- `id`: str - Unique briefing identifier (UUID)
- `generation_date`: datetime - When briefing was generated
- `week_start`: date - Start of reporting week (Monday)
- `week_end`: date - End of reporting week (Sunday)
- `financial_summary`: FinancialSummary - Revenue, expenses, profit/loss
- `marketing_metrics`: MarketingMetrics - Social media engagement, reach, top posts
- `operational_highlights`: List[str] - Key accomplishments and task completions
- `risk_alerts`: List[RiskAlert] - Failed tasks, system errors, anomalies
- `delivery_status`: DeliveryStatus - Enum: generated, sent, failed
- `recipients`: List[str] - Email addresses of recipients
- `file_path`: str - Path to briefing markdown file

**Relationships**:
- Aggregates data from FinancialTransaction (via Odoo MCP)
- Aggregates data from SocialMediaPost (via Social MCP)
- References Task entities for operational highlights

**Validation Rules**:
- `week_start` must be a Monday
- `week_end` must be a Sunday
- `week_end` must be 6 days after `week_start`
- `generation_date` must be >= `week_end`
- `recipients` must contain at least one valid email address

**Nested Types**:

**FinancialSummary**:
- `total_revenue`: Decimal - Sum of all revenue transactions
- `total_expenses`: Decimal - Sum of all expense transactions
- `net_income`: Decimal - Revenue minus expenses
- `revenue_trend`: str - "up", "down", "stable" compared to previous week
- `top_revenue_sources`: List[Tuple[str, Decimal]] - Top 5 revenue categories
- `top_expense_categories`: List[Tuple[str, Decimal]] - Top 5 expense categories

**MarketingMetrics**:
- `total_engagement`: int - Sum of likes, shares, comments across all platforms
- `total_reach`: int - Total unique users reached
- `follower_growth`: int - Net new followers across all platforms
- `top_posts`: List[SocialMediaPost] - Top 3 performing posts by engagement
- `engagement_trend`: str - "up", "down", "stable" compared to previous week

**RiskAlert**:
- `severity`: str - "low", "medium", "high"
- `category`: str - "task_failure", "system_error", "data_anomaly", "security"
- `description`: str - Human-readable alert message
- `timestamp`: datetime - When alert was detected
- `action_required`: Optional[str] - Recommended action

---

### MCPConnection

Represents a connection to an MCP server.

**Attributes**:
- `id`: str - Unique connection identifier (UUID)
- `server_type`: MCPServerType - Enum: odoo, social, email, reporting
- `connection_status`: ConnectionStatus - Enum: connected, disconnected, error
- `health_check_timestamp`: datetime - Last successful health check
- `error_count`: int - Consecutive errors since last success
- `circuit_breaker_state`: CircuitState - Enum: closed, open, half_open
- `last_error`: Optional[str] - Most recent error message
- `config_path`: str - Path to MCP server config file

**Relationships**:
- Referenced by ErrorLog

**Validation Rules**:
- `server_type` must be one of: odoo, social, email, reporting
- `connection_status` must be one of: connected, disconnected, error
- `circuit_breaker_state` must be one of: closed, open, half_open
- `error_count` must be >= 0

**State Transitions**:
- Circuit breaker closed → open (when error_count >= threshold, default 5)
- Circuit breaker open → half_open (after timeout period, default 5 minutes)
- Circuit breaker half_open → closed (when health check succeeds)
- Circuit breaker half_open → open (when health check fails)

---

### FinancialTransaction

Represents a financial event from Odoo.

**Attributes**:
- `id`: str - Unique transaction identifier (from Odoo)
- `transaction_date`: date - Date of transaction
- `type`: TransactionType - Enum: revenue, expense
- `amount`: Decimal - Transaction amount (always positive)
- `category`: str - Account category (e.g., "Sales", "Marketing", "Payroll")
- `customer_vendor`: Optional[str] - Customer name (revenue) or vendor name (expense)
- `invoice_reference`: Optional[str] - Related invoice number
- `description`: str - Transaction description
- `account_code`: str - Chart of accounts code
- `odoo_id`: int - Odoo internal record ID

**Relationships**:
- Aggregated by CEOBriefing for financial summary

**Validation Rules**:
- `type` must be one of: revenue, expense
- `amount` must be > 0
- `account_code` must exist in Odoo chart of accounts
- `transaction_date` must be within open accounting period

**Business Rules**:
- Revenue transactions must have `customer_vendor` populated
- Expense transactions must have `customer_vendor` populated
- Invoice-related transactions must have `invoice_reference` populated

---

### SocialMediaPost

Represents content on social media platforms.

**Attributes**:
- `id`: str - Unique post identifier (UUID)
- `platform`: SocialPlatform - Enum: facebook, instagram, twitter
- `platform_post_id`: str - Platform-specific post ID
- `post_date`: datetime - When post was published
- `content`: str - Post text/caption
- `media_urls`: List[str] - URLs of attached images/videos
- `engagement_metrics`: EngagementMetrics - Likes, shares, comments, reach
- `performance_score`: float - Calculated engagement rate (0.0-1.0)
- `is_anomaly`: bool - True if engagement >3x average

**Relationships**:
- Aggregated by CEOBriefing for marketing metrics

**Validation Rules**:
- `platform` must be one of: facebook, instagram, twitter
- `performance_score` must be between 0.0 and 1.0
- `post_date` must be <= current time

**Nested Types**:

**EngagementMetrics**:
- `likes`: int - Number of likes/reactions
- `shares`: int - Number of shares/retweets
- `comments`: int - Number of comments/replies
- `reach`: int - Unique users who saw the post
- `impressions`: int - Total times post was displayed
- `engagement_rate`: float - (likes + shares + comments) / reach

**Calculated Fields**:
- `performance_score` = engagement_rate / average_engagement_rate_for_platform
- `is_anomaly` = performance_score > 3.0

---

### ErrorLog

Represents a system error or failure.

**Attributes**:
- `id`: str - Unique error identifier (UUID)
- `timestamp`: datetime - When error occurred
- `operation`: str - What operation was being performed
- `error_type`: str - Error category (e.g., "NetworkError", "ValidationError", "AuthenticationError")
- `error_message`: str - Detailed error message
- `stack_trace`: Optional[str] - Full stack trace if available
- `retry_count`: int - Number of retry attempts made
- `resolution_status`: ResolutionStatus - Enum: unresolved, retrying, resolved, escalated
- `escalation_flag`: bool - True if requires human intervention
- `related_task_id`: Optional[str] - Task ID if error occurred during task execution
- `related_mcp_server`: Optional[MCPServerType] - MCP server if error occurred during MCP call
- `severity`: ErrorSeverity - Enum: low, medium, high

**Relationships**:
- References Task (optional)
- References MCPConnection (optional)

**Validation Rules**:
- `resolution_status` must be one of: unresolved, retrying, resolved, escalated
- `severity` must be one of: low, medium, high
- `retry_count` must be >= 0
- `escalation_flag` must be True if `resolution_status` is "escalated"

**Business Rules**:
- Errors with `severity` = "high" automatically set `escalation_flag` = True
- Errors with `retry_count` >= 3 and `resolution_status` = "unresolved" should be escalated

---

## Enums

### TaskDomain
- `personal` - Personal tasks (reminders, appointments)
- `business` - Business tasks (follow-ups, communications)
- `accounting` - Accounting tasks (invoices, reconciliation)
- `marketing` - Marketing tasks (social posts, campaigns)

### TaskStatus
- `pending` - Task created, not yet started
- `in_progress` - Task currently being executed
- `completed` - Task successfully completed
- `failed` - Task failed after max retries

### StepStatus
- `pending` - Step not yet started
- `in_progress` - Step currently executing
- `completed` - Step successfully completed
- `failed` - Step failed after max retries
- `skipped` - Step skipped due to conditional logic

### MCPServerType
- `odoo` - Odoo Community MCP server
- `social` - Social media MCP server (Facebook, Instagram, Twitter)
- `email` - Email MCP server
- `reporting` - Reporting MCP server

### ConnectionStatus
- `connected` - MCP server is reachable and responding
- `disconnected` - MCP server is not reachable
- `error` - MCP server returned an error

### CircuitState
- `closed` - Circuit breaker closed, requests allowed
- `open` - Circuit breaker open, requests blocked
- `half_open` - Circuit breaker testing, limited requests allowed

### TransactionType
- `revenue` - Income transaction
- `expense` - Expense transaction

### SocialPlatform
- `facebook` - Facebook Page post
- `instagram` - Instagram Business post
- `twitter` - Twitter/X post

### DeliveryStatus
- `generated` - Briefing generated but not yet sent
- `sent` - Briefing successfully delivered
- `failed` - Briefing delivery failed

### ResolutionStatus
- `unresolved` - Error not yet resolved
- `retrying` - Error being retried
- `resolved` - Error successfully resolved
- `escalated` - Error escalated to human

### ErrorSeverity
- `low` - Minor error, system continues normally
- `medium` - Moderate error, degraded functionality
- `high` - Critical error, requires immediate attention

---

## Entity Relationships Diagram

```
Task (1) ──────< (N) ExecutionStep
  │
  │ (referenced by)
  │
  └──────< ErrorLog

CEOBriefing ──aggregates──> FinancialTransaction
            └─aggregates──> SocialMediaPost
            └─references──> Task (for operational highlights)

MCPConnection
  │
  │ (referenced by)
  │
  └──────< ErrorLog

ErrorLog ──references──> Task (optional)
         └─references──> MCPConnection (optional)
```

---

## File System Representation

All entities are persisted as Markdown files with YAML frontmatter in the Obsidian vault:

**Task**: `/Inbox/*.md`, `/Needs_Action/*.md`, `/Plans/*.md`, `/Done/*.md`
**CEOBriefing**: `/Reports/CEO_Briefings/YYYY-MM-DD-briefing.md`
**ErrorLog**: `/Audit_Logs/YYYY-MM-DD-errors.jsonl` (JSON Lines format)
**MCPConnection**: `/mcp_server/*_config.yaml` (configuration) + in-memory state

FinancialTransaction and SocialMediaPost are fetched from external systems (Odoo, social media APIs) and not persisted locally except in aggregated reports.

---

## Notes

- All datetime fields use ISO 8601 format with timezone
- All Decimal fields use Python's `decimal.Decimal` for financial precision
- All entities implement `to_dict()` and `from_dict()` methods for serialization
- All entities implement validation via Pydantic validators
- State transitions are enforced via state machine pattern in business logic
