# Implementation Plan: Gold Tier Autonomous AI Employee

**Branch**: `1-gold-tier-autonomous-employee` | **Date**: 2026-03-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-gold-tier-autonomous-employee/spec.md`

## Summary

Build a fully autonomous AI Employee system capable of managing business operations, accounting, marketing, reporting, and executive briefing. The system implements the "Ralph Wiggum Loop" autonomous reasoning pattern (Plan → Execute → Reflect → Retry) and integrates with multiple external systems via MCP servers (Odoo Community for accounting, Facebook/Instagram/Twitter for social media, Email for communications, and Reporting for CEO briefings). The system operates within Gold Tier constitutional constraints with risk-based action classification, comprehensive audit logging, error recovery, and human approval gates for high-risk operations.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- MCP SDK (Model Context Protocol for external integrations)
- asyncio (for concurrent MCP server connections and autonomous loop)
- pydantic (for data validation and contracts)
- httpx (for async HTTP requests to Odoo JSON-RPC and social media APIs)
- python-dotenv (for secure credential management)
- structlog (for structured JSON logging)

**Storage**:
- File system (Markdown files with YAML frontmatter for task state)
- Audit logs (append-only JSON logs in `/Audit_Logs`)
- No external database required (follows constitutional file-system-first principle)

**Testing**: pytest with async support (pytest-asyncio)
- Contract tests for MCP server interfaces
- Integration tests for Odoo/Social/Email/Reporting MCPs
- Unit tests for Ralph Wiggum Loop logic
- End-to-end tests for CEO Briefing generation

**Target Platform**: Linux/Windows server (self-hosted)
**Project Type**: Single Python application with multiple MCP server processes
**Performance Goals**:
- CEO briefing generation: <10 minutes end-to-end
- Task execution latency: <5 minutes from trigger to completion
- Concurrent task handling: 10+ tasks without degradation
- MCP server response time: <2 seconds per operation

**Constraints**:
- All operations must be auditable (comprehensive logging)
- High-risk operations require human approval
- Accounting write operations require validation + approval
- System must handle MCP server failures gracefully
- Autonomous loop must respect kill switch (`/STOP` file)
- All actions must be reversible or have rollback procedures

**Scale/Scope**:
- Single organization deployment (no multi-tenancy)
- 4 MCP servers (Odoo, Social, Email, Reporting)
- ~50-100 autonomous tasks per week
- Weekly CEO briefing generation
- Audit log retention: 90 days minimum

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gold Tier Requirements

✅ **Principle III - Autonomous Reasoning Loop**: System implements Ralph Wiggum Loop with Plan → Execute → Reflect → Retry pattern
✅ **Principle VII - Risk-Based Approval**: Low-risk actions auto-approve, high-risk require human approval
✅ **Principle VIII - Multiple MCP Servers**: Odoo MCP, Social MCP, Email MCP, Reporting MCP with proper isolation
✅ **Principle XII - Autonomous Reasoning Loop**: Continuous monitoring, risk classification, logging, kill switch
✅ **Principle XIII - Risk Classification**: All actions classified as Low/Medium/High risk with appropriate approval workflows
✅ **Principle XIV - Comprehensive Audit Logging**: All actions logged with timestamp, risk level, approval method, results
✅ **Principle XV - Error Recovery**: Retry logic, circuit breaker, graceful degradation, rollback procedures
✅ **Principle XVI - Multi-Agent Skill Orchestration**: Skills can invoke other skills for complex workflows
✅ **Principle XVII - Cross-Domain Integration**: Personal, business, accounting, marketing domains integrated
✅ **Principle XVIII - Accounting Data Protection**: Read operations auto-approve, write operations require validation + approval

### Constitutional Compliance

- **File System State Management**: ✅ Task state represented by folder location (Inbox → Needs_Action → Plans → Done)
- **Vault Boundary Enforcement**: ✅ All file operations within `E:\AI_Employee_Vault`
- **MCP Server Architecture**: ✅ All external actions route through MCP servers (no direct API calls)
- **Human-in-the-Loop**: ✅ High-risk actions require explicit approval via `/Pending_Approval` folder
- **Plan-Driven Execution**: ✅ All actions originate from Plan.md or autonomous loop decisions (logged)
- **Kill Switch**: ✅ `/STOP` file immediately halts autonomous loop
- **Audit Logging**: ✅ All actions logged to `/Audit_Logs` with full context
- **Rollback Procedures**: ✅ All high-risk actions define rollback procedures

### Violations Requiring Justification

None. This implementation fully complies with Gold Tier constitutional requirements.

## Project Structure

### Documentation (this feature)

```text
specs/1-gold-tier-autonomous-employee/
├── spec.md              # Feature specification (COMPLETED)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   ├── odoo-mcp.yaml
│   ├── social-mcp.yaml
│   ├── email-mcp.yaml
│   └── reporting-mcp.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist (COMPLETED)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── ralph_loop.py           # Autonomous reasoning loop (Plan → Execute → Reflect → Retry)
├── risk_engine.py          # Risk classification engine (Low/Medium/High)
├── audit_logger.py         # Comprehensive audit logging
├── task_scanner.py         # Monitors folders for tasks (Inbox, Needs_Action, Plans)
├── validation_engine.py    # Validates accounting transactions before execution
├── circuit_breaker.py      # Circuit breaker pattern for error handling
├── kill_switch.py          # Kill switch monitoring (/STOP file detection)
├── models/
│   ├── task.py            # Task entity (description, domain, priority, status)
│   ├── execution_step.py  # Execution step entity (step description, status, retry count)
│   ├── ceo_briefing.py    # CEO briefing entity (financial, marketing, operational data)
│   ├── mcp_connection.py  # MCP connection entity (server type, status, health)
│   ├── financial_transaction.py  # Financial transaction entity (from Odoo)
│   ├── social_post.py     # Social media post entity (platform, content, metrics)
│   └── error_log.py       # Error log entity (timestamp, operation, error details)
├── mcp_servers/
│   ├── odoo_mcp.py        # Odoo Community JSON-RPC integration
│   ├── social_mcp.py      # Facebook + Instagram + Twitter integration
│   ├── email_mcp.py       # Email sending and management
│   └── reporting_mcp.py   # CEO Briefing generation and compilation
├── skills/
│   ├── base_skill.py      # Base skill class with error handling and logging
│   ├── odoo_skills.py     # Odoo-specific skills (create invoice, fetch P&L)
│   ├── social_skills.py   # Social media skills (fetch metrics, generate summary)
│   ├── email_skills.py    # Email skills (send briefing, send notification)
│   ├── reporting_skills.py # Reporting skills (generate CEO briefing)
│   └── orchestration_skills.py # Multi-skill workflows
├── utils/
│   ├── file_operations.py # File system operations (read/write/move tasks)
│   ├── retry_logic.py     # Exponential backoff retry implementation
│   └── config.py          # Configuration management (env vars, thresholds)
└── main.py                # Entry point for autonomous loop

tests/
├── contract/
│   ├── test_odoo_mcp_contract.py
│   ├── test_social_mcp_contract.py
│   ├── test_email_mcp_contract.py
│   └── test_reporting_mcp_contract.py
├── integration/
│   ├── test_odoo_integration.py
│   ├── test_social_integration.py
│   ├── test_email_integration.py
│   ├── test_ceo_briefing_e2e.py
│   └── test_ralph_loop_e2e.py
└── unit/
    ├── test_ralph_loop.py
    ├── test_risk_engine.py
    ├── test_audit_logger.py
    ├── test_validation_engine.py
    ├── test_circuit_breaker.py
    └── test_retry_logic.py

mcp_server/              # MCP server configurations (constitutional requirement)
├── odoo_config.yaml
├── social_config.yaml
├── email_config.yaml
└── reporting_config.yaml

.env.example             # Example environment variables (credentials template)
requirements.txt         # Python dependencies
pytest.ini               # Pytest configuration
```

**Structure Decision**: Single Python application with modular MCP server implementations. The autonomous loop (`ralph_loop.py`) orchestrates task execution by monitoring file system state and invoking appropriate skills via MCP servers. All external integrations are isolated in dedicated MCP server modules to maintain constitutional compliance and enable independent testing.

## Complexity Tracking

No constitutional violations. This implementation adheres to all Gold Tier requirements.

## Phase 0: Research & Technology Decisions

### Research Tasks

The following areas require research to resolve technical unknowns and establish implementation patterns:

#### 1. MCP SDK Integration Patterns

**Question**: What is the best practice for implementing multiple concurrent MCP server connections in Python?

**Research Needed**:
- MCP SDK documentation for Python
- Connection pooling strategies for multiple MCP servers
- Error handling patterns for MCP server failures
- Health check and reconnection logic

**Decision Criteria**:
- Must support 4+ concurrent MCP connections
- Must handle connection failures gracefully
- Must provide clear error messages for debugging
- Must integrate with asyncio event loop

#### 2. Odoo Community JSON-RPC Integration

**Question**: How do we authenticate and interact with Odoo Community edition via JSON-RPC?

**Research Needed**:
- Odoo JSON-RPC authentication flow (username/password vs API keys)
- Odoo model access patterns (read, create, write, search)
- Odoo invoice creation API (required fields, validation rules)
- Odoo financial reporting APIs (account.move, account.account)
- Error handling for Odoo API failures

**Decision Criteria**:
- Must support secure authentication (no plaintext passwords in code)
- Must handle Odoo API errors with clear messages
- Must validate invoice data before submission
- Must support read-only operations for reporting

#### 3. Social Media API Integration

**Question**: What are the official API patterns for Facebook, Instagram, and Twitter engagement metrics?

**Research Needed**:
- Facebook Graph API: Page insights, post metrics, authentication (OAuth2)
- Instagram Graph API: Media insights, account metrics, authentication
- Twitter API v2: Tweet metrics, user metrics, authentication (OAuth 2.0)
- Rate limiting strategies for each platform
- Webhook vs polling for real-time updates

**Decision Criteria**:
- Must use official APIs only (no scraping)
- Must handle rate limits gracefully
- Must support OAuth2 token refresh
- Must aggregate metrics across platforms

#### 4. Risk Classification Algorithm

**Question**: How do we implement a deterministic, auditable risk classification engine?

**Research Needed**:
- Rule-based vs ML-based classification (rule-based preferred for auditability)
- Risk scoring algorithms (weighted factors vs decision trees)
- Configurable threshold management
- Risk classification for composite actions (orchestrated skills)

**Decision Criteria**:
- Must be deterministic (same input → same output)
- Must be auditable (clear reasoning for classification)
- Must be configurable (thresholds adjustable by user)
- Must handle edge cases (unknown action types default to high-risk)

#### 5. Audit Logging Infrastructure

**Question**: What is the best practice for comprehensive, append-only audit logging in Python?

**Research Needed**:
- Structured logging libraries (structlog, python-json-logger)
- Append-only file strategies (log rotation, retention policies)
- Log querying and analysis tools
- Performance impact of comprehensive logging

**Decision Criteria**:
- Must be append-only (no modification or deletion)
- Must be human-readable and machine-parseable
- Must support querying by date, action type, risk level
- Must have minimal performance impact

#### 6. Circuit Breaker Pattern Implementation

**Question**: How do we implement circuit breaker pattern for MCP server failures?

**Research Needed**:
- Circuit breaker libraries (pybreaker, circuitbreaker)
- State management (closed, open, half-open)
- Timeout and retry configuration
- Integration with asyncio

**Decision Criteria**:
- Must prevent cascading failures
- Must allow recovery after timeout period
- Must log state transitions
- Must integrate with existing retry logic

#### 7. CEO Briefing Template and Data Aggregation

**Question**: What is the optimal format and structure for CEO briefings?

**Research Needed**:
- Executive summary best practices
- Data visualization in Markdown (tables, charts)
- Email formatting (HTML vs plain text)
- Template engines (Jinja2, Mako)

**Decision Criteria**:
- Must be concise (1-2 pages)
- Must highlight key metrics and trends
- Must be actionable (clear next steps)
- Must support both Markdown and HTML output

### Research Output

All research findings will be documented in `research.md` with the following structure:

```markdown
# Research Findings: Gold Tier Autonomous AI Employee

## 1. MCP SDK Integration Patterns

**Decision**: [Selected approach]
**Rationale**: [Why chosen]
**Alternatives Considered**: [What else was evaluated]
**Implementation Notes**: [Key details for Phase 1]

## 2. Odoo Community JSON-RPC Integration

[Same structure as above]

...
```

## Phase 1: Design & Contracts

### Prerequisites

- `research.md` completed with all technical decisions documented
- All NEEDS CLARIFICATION items from spec.md resolved (2 pending: FR-005 escalation conditions, FR-036 data access permissions)

### Artifacts to Generate

#### 1. Data Model (`data-model.md`)

Extract entities from spec.md and define their structure:

**Entities**:
- Task (description, domain, priority, status, execution_history)
- ExecutionStep (step_description, status, retry_count, error_messages, result_data)
- CEOBriefing (generation_date, financial_summary, marketing_metrics, operational_highlights, risk_alerts)
- MCPConnection (server_type, connection_status, health_check_timestamp, error_count)
- FinancialTransaction (transaction_date, type, amount, category, customer_vendor, invoice_reference)
- SocialMediaPost (platform, post_date, content, engagement_metrics, performance_score)
- ErrorLog (timestamp, operation, error_type, error_message, retry_count, resolution_status)

**Relationships**:
- Task → ExecutionStep (one-to-many)
- CEOBriefing → FinancialTransaction (aggregates)
- CEOBriefing → SocialMediaPost (aggregates)
- ErrorLog → Task (references)

**Validation Rules**:
- Task.domain must be one of: personal, business, accounting, marketing
- Task.status must be one of: pending, in_progress, completed, failed
- FinancialTransaction amounts must balance (debits = credits) for accounting operations
- SocialMediaPost.platform must be one of: facebook, instagram, twitter

#### 2. API Contracts (`contracts/`)

Generate MCP server contracts based on functional requirements:

**Odoo MCP Contract** (`contracts/odoo-mcp.yaml`):
```yaml
mcp_server: odoo
version: 1.0.0
operations:
  - name: authenticate
    method: POST
    endpoint: /jsonrpc
    risk_level: low

  - name: create_invoice
    method: POST
    endpoint: /jsonrpc
    risk_level: high
    requires_validation: true
    requires_approval: true

  - name: fetch_financial_summary
    method: POST
    endpoint: /jsonrpc
    risk_level: low

  - name: generate_profit_loss
    method: POST
    endpoint: /jsonrpc
    risk_level: low
```

**Social MCP Contract** (`contracts/social-mcp.yaml`):
```yaml
mcp_server: social
version: 1.0.0
operations:
  - name: fetch_facebook_metrics
    method: GET
    endpoint: /facebook/insights
    risk_level: low

  - name: fetch_instagram_metrics
    method: GET
    endpoint: /instagram/insights
    risk_level: low

  - name: fetch_twitter_metrics
    method: GET
    endpoint: /twitter/metrics
    risk_level: low

  - name: generate_weekly_summary
    method: POST
    endpoint: /social/summary
    risk_level: low
```

**Email MCP Contract** (`contracts/email-mcp.yaml`):
```yaml
mcp_server: email
version: 1.0.0
operations:
  - name: send_email
    method: POST
    endpoint: /email/send
    risk_level: medium
    requires_template_validation: true
```

**Reporting MCP Contract** (`contracts/reporting-mcp.yaml`):
```yaml
mcp_server: reporting
version: 1.0.0
operations:
  - name: generate_ceo_briefing
    method: POST
    endpoint: /reporting/ceo-briefing
    risk_level: low

  - name: compile_financial_report
    method: POST
    endpoint: /reporting/financial
    risk_level: low
```

#### 3. Quickstart Guide (`quickstart.md`)

Developer onboarding guide with:
- Environment setup (Python 3.11+, dependencies)
- Configuration (`.env` file with Odoo URL, social media API keys)
- MCP server setup (configuration files in `/mcp_server`)
- Running the autonomous loop (`python src/main.py`)
- Testing the system (pytest commands)
- Triggering CEO briefing manually
- Using the kill switch (`touch /STOP`)

#### 4. Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to update agent-specific context with:
- Python 3.11+ as primary language
- MCP SDK for external integrations
- asyncio for concurrent operations
- Odoo Community JSON-RPC integration
- Facebook/Instagram/Twitter API integration
- Risk-based approval workflow
- Comprehensive audit logging

### Constitution Check (Post-Design)

After Phase 1 design artifacts are complete, re-verify:
- ✅ All MCP servers have clear domain boundaries
- ✅ Risk classification is deterministic and auditable
- ✅ Audit logging captures all required fields
- ✅ Rollback procedures defined for high-risk operations
- ✅ Kill switch mechanism is file-based and immediate
- ✅ Accounting validation engine prevents invalid transactions

## Phase 2: Task Generation

**NOT PERFORMED BY THIS COMMAND**. After Phase 1 completion, run `/sp.tasks` to generate `tasks.md` with:
- Testable implementation tasks
- Dependency ordering
- Acceptance criteria for each task
- Test cases for validation

## Implementation Notes

### Critical Path

1. **Phase 0**: Research MCP SDK, Odoo JSON-RPC, social media APIs → `research.md`
2. **Phase 1**: Design data models, MCP contracts, quickstart guide → `data-model.md`, `contracts/`, `quickstart.md`
3. **Phase 2**: Generate implementation tasks → `tasks.md` (via `/sp.tasks`)
4. **Phase 3**: Implement core autonomous loop → `ralph_loop.py`, `risk_engine.py`, `audit_logger.py`
5. **Phase 4**: Implement MCP servers → `odoo_mcp.py`, `social_mcp.py`, `email_mcp.py`, `reporting_mcp.py`
6. **Phase 5**: Implement skills → `odoo_skills.py`, `social_skills.py`, `reporting_skills.py`
7. **Phase 6**: Integration testing → CEO briefing end-to-end test
8. **Phase 7**: Gold Tier activation checklist verification

### Risk Mitigation

- **MCP Server Failures**: Circuit breaker pattern prevents cascading failures
- **Accounting Errors**: Validation engine + human approval for all write operations
- **Autonomous Loop Errors**: Kill switch provides immediate shutdown capability
- **Data Integrity**: Comprehensive audit logging enables full reconstruction of actions
- **Rate Limiting**: Exponential backoff with jitter for all external API calls

### Success Criteria Mapping

From spec.md Success Criteria:
- **SC-001** (CEO briefing by 8:30 AM): Autonomous loop triggers at 8:00 AM, reporting skill completes in <10 min
- **SC-002** (95% task success): Ralph Wiggum Loop with retry logic and error recovery
- **SC-003** (Financial ops <5 min): Odoo MCP optimized for fast JSON-RPC calls
- **SC-004** (Social data <10 min): Parallel API calls to Facebook/Instagram/Twitter
- **SC-005** (90% failure recovery): Circuit breaker + retry logic + graceful degradation
- **SC-006** (Escalation <15 min): Audit logger triggers immediate notification on high-severity errors
- **SC-007** (80% task delegation): Risk-based auto-approval for low-risk operations
- **SC-008** (99% uptime): Circuit breaker prevents system-wide failures
- **SC-009** (Complete audit trails): Comprehensive audit logging with all required fields
- **SC-010** (10 concurrent tasks): asyncio-based concurrent task execution

## Next Steps

1. **Resolve Spec Clarifications**: Address FR-005 (escalation conditions) and FR-036 (data access permissions) before proceeding
2. **Execute Phase 0**: Research all technical unknowns and document in `research.md`
3. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md` based on research findings
4. **Update Agent Context**: Run update script to add Python/MCP/Odoo/Social technologies
5. **Run `/sp.tasks`**: Generate implementation tasks with dependency ordering
6. **Begin Implementation**: Start with core autonomous loop and risk engine

## Architectural Decision Records (ADRs)

The following architecturally significant decisions should be documented as ADRs after planning:

1. **ADR-001**: Ralph Wiggum Loop Pattern for Autonomous Reasoning
   - Decision: Implement Plan → Execute → Reflect → Retry loop
   - Rationale: Enables autonomous multi-step task execution with error recovery
   - Alternatives: Simple task queue, event-driven architecture

2. **ADR-002**: Multiple MCP Servers with Domain Isolation
   - Decision: Separate MCP servers for Odoo, Social, Email, Reporting
   - Rationale: Constitutional requirement, enables independent testing and failure isolation
   - Alternatives: Single monolithic MCP server

3. **ADR-003**: Risk-Based Action Classification
   - Decision: Rule-based risk engine with Low/Medium/High classification
   - Rationale: Deterministic, auditable, configurable; enables autonomous operation with safety
   - Alternatives: ML-based classification, manual approval for all actions

4. **ADR-004**: File-System-First State Management
   - Decision: Task state represented by folder location (Inbox → Needs_Action → Plans → Done)
   - Rationale: Constitutional requirement, human-readable, version-controllable
   - Alternatives: Database state management, in-memory state

5. **ADR-005**: Comprehensive Audit Logging
   - Decision: Append-only structured JSON logs for all actions
   - Rationale: Constitutional requirement, enables accountability and debugging
   - Alternatives: Database audit tables, minimal logging

After Phase 1 completion, run `/sp.adr` to create these ADRs with full context.
