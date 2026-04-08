# Personal AI Employee Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.1.0 → 2.0.0
Rationale: Gold Tier amendment - enables fully autonomous operation with comprehensive safety systems

Modified Principles:
- MAJOR: Principle III: Manual/Scheduled Trigger → Autonomous Reasoning Loop (Gold Tier)
- MAJOR: Principle VIII: ONE MCP Server → Multiple MCP Servers (Gold Tier)
- Enhanced Principle VII: Approval workflows now include risk-based auto-approval for low-risk actions
- Enhanced Principle IX: Agent Skills now include orchestration and composition capabilities
- Enhanced Error Handling: Added retry logic, graceful degradation, and comprehensive audit logging

Added Sections:
- Gold Tier Architecture Enhancements
- Principle XII: Autonomous Reasoning Loop
- Principle XIII: Risk-Based Action Classification
- Principle XIV: Comprehensive Audit Logging
- Principle XV: Error Recovery and Graceful Degradation
- Principle XVI: Multi-Agent Skill Orchestration
- Principle XVII: Cross-Domain Integration
- Principle XVIII: Accounting Data Protection
- Gold Tier Folder Structure
- Autonomous Loop specification
- Risk Engine requirements
- CEO Briefing generation workflow

Removed Sections: None (Bronze and Silver Tier principles preserved for backward compatibility)

Templates Requiring Updates:
- ✅ constitution.md (this file)
- ⚠ .specify/templates/plan-template.md (requires Gold Tier risk assessment fields)
- ⚠ .specify/templates/spec-template.md (requires cross-domain integration fields)
- ⚠ .specify/templates/tasks-template.md (requires audit logging fields)
- ⚠ .specify/templates/skill-template.md (requires orchestration and risk classification)

New Components Required:
- Autonomous reasoning loop implementation
- Skill orchestrator service
- Risk engine for action classification
- Audit logger with comprehensive event tracking
- Reporting engine for CEO Briefings
- Odoo Community MCP server
- Social media MCP servers (Facebook, Instagram, Twitter/X)

Follow-up TODOs:
- Implement autonomous reasoning loop with safety constraints
- Configure multiple MCP servers with proper isolation
- Deploy risk engine with configurable thresholds
- Set up comprehensive audit logging infrastructure
- Create CEO Briefing generation pipeline
- Establish accounting data validation rules
- Document rollback and recovery procedures
- Create Gold Tier folder structure
-->

## Core Principles

### I. File System Only Operations (Bronze Tier)

The AI MUST interact with the system exclusively through file system operations within the designated Obsidian vault. No external API calls, network requests, or system calls beyond file I/O are permitted in Bronze Tier.

**Rationale**: This constraint ensures predictable, auditable behavior and eliminates security risks associated with external integrations. All actions leave a traceable file system footprint.

### II. Vault Boundary Enforcement

All file operations MUST occur within the Obsidian vault directory (`E:\AI_Employee_Vault`). The AI MUST NOT read, write, modify, or delete files outside this boundary.

**Rationale**: Strict boundary enforcement prevents accidental data corruption, maintains system integrity, and provides a clear security perimeter for AI operations.

### III. Trigger Model Evolution

**Bronze Tier**: Task processing MUST be initiated manually via Claude CLI commands.

**Silver Tier**: Scheduled Claude reasoning loops with human approval gates.

**Gold Tier**: Fully autonomous reasoning loop ("Ralph Wiggum" mode) with comprehensive safety systems:
- Risk-based action classification (auto-approve low-risk, require approval for high-risk)
- Comprehensive audit logging of all decisions and actions
- Error recovery and graceful degradation
- Reversibility constraints (all autonomous actions must be reversible or have rollback procedures)
- Kill switch capability for immediate shutdown

**Rationale**: Bronze ensures human oversight. Silver adds scheduling with approval. Gold enables true autonomy while maintaining safety through risk classification, logging, and reversibility. The autonomous loop must remain safe, auditable, and stoppable.

### IV. Folder-Based State Management

System state MUST be represented through folder location and structure. State transitions follow the canonical flow:
- `/Inbox` → New items requiring triage
- `/Needs_Action` → Triaged items awaiting execution
- `/Plans` → Items with execution plans ready for implementation
- `/Done` → Completed items

Silver Tier adds:
- `/Pending_Approval` → Actions requiring human approval
- `/Approved` → Actions approved for execution
- `/Rejected` → Actions denied by human review
- `/Skills` → Agent skill definitions
- `/mcp_server` → MCP server configuration and state

File movement between folders represents state changes. No external state databases or registries are permitted.

**Rationale**: Folder-based state is human-readable, version-controllable, and requires no additional infrastructure. Users can understand system state at a glance through file explorer.

### V. Watcher Architecture

**Bronze Tier**: Only ONE file system watcher process may run concurrently. The watcher's sole responsibility is detecting new files in `/Inbox` and notifying the user.

**Silver Tier**: Multiple watchers are permitted for monitoring different folders (Inbox, Pending_Approval, Approved). Each watcher MUST have a single, well-defined responsibility.

**Gold Tier**: Autonomous reasoning loop replaces traditional watchers. The loop continuously monitors system state, evaluates opportunities, and executes actions within safety constraints. Traditional watchers may still be used for specific monitoring needs.

**Rationale**: Bronze Tier's single watcher minimizes complexity. Silver Tier's multiple watchers enable approval workflows. Gold Tier's autonomous loop enables proactive behavior while maintaining safety through risk classification and audit logging.

### VI. No Cloud or External Services (Bronze Tier)

Bronze Tier MUST operate entirely locally. Prohibited:
- Cloud storage synchronization during AI operations
- External API calls (email, messaging, web services)
- Browser automation
- Network-dependent features

**Silver Tier Exceptions**: See Principle VIII (MCP Server Integration) and Principle X (External Action Boundaries) for controlled external access.

**Rationale**: Local-only operation ensures privacy, eliminates network dependencies, and provides a stable foundation before introducing external integrations in higher tiers.

### VII. Human-in-the-Loop Approval

**Silver Tier**: All sensitive actions MUST require explicit human approval before execution.

**Gold Tier**: Risk-based approval with auto-approval for low-risk actions and human approval for high-risk actions.

**Action Classification**:
- **Low-Risk (Auto-Approve)**: Read-only operations, routine reports, standard social posts within guidelines, email responses following templates
- **Medium-Risk (Conditional Auto-Approve)**: Actions within pre-approved parameters and budgets, reversible operations with rollback procedures
- **High-Risk (Human Approval Required)**: Accounting data modifications, off-template communications, budget-exceeding actions, irreversible operations, policy changes

**Approval Workflow (Silver Tier)**:
1. AI generates action plan and writes to `/Pending_Approval`
2. Human reviews plan details, risks, and intended outcomes
3. Human moves file to `/Approved` (consent) or `/Rejected` (denial)
4. AI executes only approved actions
5. Results logged to `/Done` with execution summary

**Approval Workflow (Gold Tier)**:
1. AI generates action plan and classifies risk level using Risk Engine
2. **If Low-Risk**: Auto-approve and execute immediately, log to audit trail
3. **If Medium-Risk**: Check against pre-approved parameters; auto-approve if within bounds, otherwise escalate to human
4. **If High-Risk**: Write to `/Pending_Approval` for human review
5. Human reviews high-risk plans and moves to `/Approved` or `/Rejected`
6. AI executes approved actions via appropriate MCP server
7. All results logged to `/Done` with execution summary and risk classification

**Rationale**: Silver Tier approval gates prevent unauthorized actions. Gold Tier risk-based approval enables autonomous operation for routine tasks while maintaining human oversight for significant decisions. All actions remain auditable regardless of approval method.

### VIII. MCP Server Integration

**Silver Tier**: ONE Model Context Protocol (MCP) server for controlled external integrations.

**Gold Tier**: MULTIPLE MCP servers permitted for cross-domain integration with proper isolation.

**Requirements (All Tiers)**:
- MCP servers MUST be configured in `/mcp_server` directory
- All external actions MUST route through MCP servers (no direct API calls from Claude)
- Each MCP server MUST implement rate limiting and error handling
- MCP server configurations MUST be version-controlled
- Each MCP server MUST have a clear, single domain of responsibility

**Gold Tier MCP Servers**:
- **Odoo Community MCP**: Accounting integration via JSON-RPC (read-only by default, write requires validation)
- **Social Media MCP**: Facebook, Instagram, Twitter/X integration (official APIs only)
- **Email MCP**: Email sending and management
- **Reporting MCP**: CEO Briefing generation and report compilation
- Additional domain-specific MCPs as needed (each requires constitutional amendment)

**Permitted MCP Operations**:
- Email sending (via configured email service)
- Social media posting (Facebook Pages, Instagram Business, Twitter/X via official APIs)
- Accounting data retrieval (Odoo Community via JSON-RPC, read-only)
- Report generation and compilation
- Other approved external integrations documented in MCP server config

**Prohibited**:
- Direct API calls from Claude (must use MCP)
- MCP operations bypassing risk classification
- Personal social media profile automation (only business accounts)
- Accounting data modification without validation workflow
- MCP servers without proper isolation and error handling

**Rationale**: MCP provides a controlled, auditable interface for external integrations. Silver Tier's single server maintains simplicity. Gold Tier's multiple servers enable comprehensive business automation while maintaining isolation and safety through domain-specific boundaries.

### IX. Agent Skills Architecture

**Silver Tier**: All AI functionality MUST be implemented as Agent Skills stored in `/Skills` directory.

**Gold Tier**: Agent Skills with orchestration, composition, and multi-skill workflows.

**Skill Requirements (All Tiers)**:
- Each skill MUST be a self-contained Markdown file
- Skills MUST declare required permissions and external dependencies
- Skills MUST specify approval requirements (auto-approve vs human-approve)
- Skills MUST include error handling and rollback procedures
- Skills MUST declare their risk classification (low/medium/high)

**Gold Tier Skill Enhancements**:
- **Skill Orchestration**: Skills can invoke other skills to create complex workflows
- **Skill Composition**: Multiple skills can be combined into higher-level capabilities
- **Conditional Execution**: Skills can include branching logic based on runtime conditions
- **State Management**: Skills can maintain state across invocations
- **Retry Logic**: Skills MUST implement retry strategies for transient failures
- **Graceful Degradation**: Skills MUST define fallback behavior when dependencies fail

**Skill Categories**:
- **Core Skills**: Fundamental operations (file management, data processing)
- **Integration Skills**: External system interactions (Odoo, social media, email)
- **Reporting Skills**: Data compilation and report generation (CEO Briefing)
- **Orchestration Skills**: Multi-skill workflows and complex automation
- **Monitoring Skills**: System health checks and anomaly detection

**Rationale**: Silver Tier skills provide modularity and clear permission boundaries. Gold Tier orchestration enables complex automation while maintaining safety through composition of audited, tested skills. Users can audit, enable, or disable specific capabilities at any level of granularity.

### X. External Action Boundaries

**Silver Tier Permitted External Actions**:
- Email sending via MCP (with approval)
- Facebook Page posting via official Meta Graph API (with approval)
- Actions explicitly defined in approved skills

**Gold Tier Permitted External Actions**:
- All Silver Tier actions (with risk-based approval)
- Odoo Community accounting data retrieval via JSON-RPC (read-only, auto-approve)
- Odoo Community accounting data modification via JSON-RPC (write operations require validation and approval)
- Instagram Business account posting via official Meta Graph API (with risk-based approval)
- Twitter/X posting via official API (with risk-based approval)
- CEO Briefing generation and compilation (auto-approve)
- Cross-domain data integration for reporting (auto-approve for read-only)
- Multi-skill orchestrated workflows (approval based on highest-risk component)

**Prohibited Actions (All Tiers)**:
- Personal social media profile automation (only business/page accounts)
- Browser automation or web scraping
- Unauthorized API access
- Actions bypassing MCP servers
- Destructive operations without approval and rollback procedures
- Accounting data modification without validation workflow
- Actions that violate platform terms of service
- Operations that cannot be audited or logged

**Rationale**: Clear boundaries prevent misuse while enabling legitimate productivity enhancements. Official APIs ensure compliance with platform terms of service. Gold Tier expands capabilities while maintaining safety through risk classification, validation workflows, and comprehensive audit logging.

### XI. Plan-Driven Execution

**Silver Tier**: All external actions MUST originate from a documented Plan.md file. Ad-hoc external operations are prohibited.

**Gold Tier**: All external actions MUST originate from either:
- A documented Plan.md file (for user-initiated tasks)
- An autonomous reasoning loop decision (for proactive actions, must be logged and auditable)

**Plan Requirements (All Tiers)**:
- Clear objective and success criteria
- List of external actions with justification
- Risk assessment and classification
- Mitigation strategies for identified risks
- Rollback procedure for failures
- Approval checkpoint before execution (or auto-approve justification for low-risk)

**Gold Tier Autonomous Loop Requirements**:
- All autonomous decisions MUST be logged with reasoning
- Autonomous actions MUST follow the same risk classification as planned actions
- Autonomous actions MUST be reversible or have documented rollback procedures
- Autonomous loop MUST respect rate limits and resource budgets
- Autonomous loop MUST have kill switch capability for immediate shutdown

**Rationale**: Plan-driven execution ensures thoughtful design, enables review before action, and provides documentation for audit trails. Gold Tier autonomous loop maintains these guarantees through comprehensive logging and risk-based execution.

### XII. Autonomous Reasoning Loop (Gold Tier)

The autonomous reasoning loop ("Ralph Wiggum" mode) enables proactive task execution within strict safety constraints.

**Loop Behavior**:
- Continuously monitors system state (Inbox, Needs_Action, Plans folders)
- Evaluates opportunities for proactive action (report generation, routine tasks)
- Classifies potential actions by risk level
- Executes low-risk actions automatically
- Escalates high-risk actions to human approval
- Logs all decisions and actions to audit trail
- Respects rate limits and resource budgets
- Operates within defined time windows (configurable)

**Safety Constraints**:
- All actions MUST be reversible or have documented rollback procedures
- Loop MUST respect kill switch for immediate shutdown
- Loop MUST pause on repeated failures (circuit breaker pattern)
- Loop MUST NOT execute actions that exceed resource budgets
- Loop MUST NOT modify accounting data without validation
- Loop MUST maintain comprehensive audit logs of all decisions

**Kill Switch**:
- File-based kill switch: Create `/STOP` file to immediately halt autonomous loop
- Loop checks for kill switch before each action
- Kill switch triggers graceful shutdown with state preservation
- Human review required before re-enabling loop after kill switch activation

**Rationale**: Autonomous operation enables true productivity gains but requires comprehensive safety systems. The loop must be safe, auditable, reversible, and stoppable at all times.

### XIII. Risk-Based Action Classification (Gold Tier)

All actions MUST be classified by risk level to determine approval requirements.

**Risk Classification Criteria**:

**Low-Risk Actions** (Auto-Approve):
- Read-only operations (data retrieval, report viewing)
- Routine reports following established templates
- Social media posts within pre-approved content guidelines
- Email responses using approved templates
- File system operations within vault
- Actions with no external side effects

**Medium-Risk Actions** (Conditional Auto-Approve):
- Actions within pre-approved budgets and parameters
- Reversible operations with tested rollback procedures
- Social media posts requiring minor customization
- Email communications with standard business content
- Data aggregation and compilation for reports

**High-Risk Actions** (Human Approval Required):
- Accounting data modifications (any write operations to Odoo)
- Communications outside approved templates or guidelines
- Actions exceeding budget thresholds
- Irreversible operations without rollback procedures
- Policy or configuration changes
- Actions affecting multiple external systems
- First-time execution of new skill combinations

**Risk Engine Requirements**:
- Risk classification MUST be deterministic and auditable
- Risk thresholds MUST be configurable by user
- Risk classification MUST be logged for every action
- Risk engine MUST err on the side of caution (when uncertain, escalate)

**Rationale**: Risk-based classification enables autonomous operation for routine tasks while maintaining human oversight for significant decisions. Clear criteria ensure consistent, predictable behavior.

### XIV. Comprehensive Audit Logging (Gold Tier)

All actions, decisions, and state changes MUST be logged to a comprehensive audit trail.

**Required Log Entries**:
- Timestamp (ISO 8601 format with timezone)
- Action type and description
- Risk classification
- Approval method (auto-approve, human-approve, or rejected)
- Input data and parameters
- Output results and side effects
- Skill(s) invoked
- MCP server(s) used
- Success/failure status
- Error details (if applicable)
- Rollback actions taken (if applicable)
- User context (if human-initiated)

**Log Storage**:
- Audit logs MUST be stored in `/Audit_Logs` directory
- Logs MUST be append-only (no modification or deletion)
- Logs MUST be human-readable (Markdown format with YAML frontmatter)
- Logs MUST be machine-parseable for analysis
- Logs MUST be retained according to configurable retention policy

**Log Analysis**:
- System MUST support querying logs by date, action type, risk level, status
- System MUST generate summary reports from audit logs
- System MUST detect anomalies and patterns in audit logs
- System MUST alert on suspicious activity or repeated failures

**Rationale**: Comprehensive audit logging provides accountability, enables debugging, supports compliance, and allows users to understand and verify all system behavior.

### XV. Error Recovery and Graceful Degradation (Gold Tier)

The system MUST handle errors gracefully and recover from failures without human intervention when possible.

**Error Handling Requirements**:
- All skills MUST implement error handling for expected failure modes
- All MCP operations MUST include timeout and retry logic
- All external API calls MUST handle rate limiting and transient failures
- All file operations MUST handle concurrent access and locking

**Retry Strategy**:
- Transient failures: Exponential backoff with jitter (max 3 retries)
- Rate limiting: Respect retry-after headers, back off appropriately
- Network failures: Retry with increasing delays
- Permanent failures: Log error, escalate to human, do not retry

**Circuit Breaker Pattern**:
- After N consecutive failures (configurable, default 5), open circuit
- While circuit open, fail fast without attempting operation
- After timeout period (configurable, default 5 minutes), attempt half-open
- If half-open attempt succeeds, close circuit; if fails, reopen circuit

**Graceful Degradation**:
- If MCP server unavailable, log error and continue with reduced functionality
- If external service unavailable, use cached data when appropriate
- If skill fails, attempt fallback skill if defined
- If autonomous loop encounters errors, pause and alert user

**Rollback Procedures**:
- All high-risk actions MUST define rollback procedures
- Rollback MUST be attempted automatically on action failure
- Rollback failures MUST be logged and escalated to human
- Partial rollbacks MUST leave system in consistent state

**Rationale**: Robust error handling enables autonomous operation without constant human intervention. Graceful degradation maintains system utility even when components fail.

### XVI. Multi-Agent Skill Orchestration (Gold Tier)

Skills can orchestrate other skills to create complex, multi-step workflows.

**Orchestration Requirements**:
- Orchestrating skill MUST declare all sub-skills as dependencies
- Orchestrating skill inherits highest risk classification of any sub-skill
- Orchestrating skill MUST handle sub-skill failures gracefully
- Orchestrating skill MUST maintain transaction-like semantics (all-or-nothing when possible)

**Skill Communication**:
- Skills communicate via file system (write intermediate results to temp files)
- Skills MUST NOT share mutable state
- Skills MUST declare input and output contracts
- Skills MUST validate inputs and outputs

**Execution Model**:
- Sequential execution: Skills run one after another
- Parallel execution: Independent skills run concurrently (when safe)
- Conditional execution: Skills run based on runtime conditions
- Retry execution: Failed skills retry according to retry strategy

**Orchestration Patterns**:
- **Pipeline**: Linear sequence of skills (A → B → C)
- **Fan-out/Fan-in**: Parallel execution with aggregation
- **Conditional**: Branch based on conditions
- **Loop**: Repeat skill until condition met (with max iteration limit)

**Rationale**: Orchestration enables complex automation while maintaining modularity and testability. Each skill remains independently auditable and testable.

### XVII. Cross-Domain Integration (Gold Tier)

The system integrates data and actions across multiple business domains.

**Integrated Domains**:
- **Personal Domain**: Tasks, notes, personal productivity
- **Business Domain**: Accounting (Odoo), social media, email, reporting
- **Cross-Domain**: CEO Briefings combining personal and business data

**Integration Requirements**:
- Each domain MUST have clear data ownership and access controls
- Cross-domain operations MUST be explicitly authorized
- Cross-domain data flows MUST be logged in audit trail
- Cross-domain integrations MUST respect domain-specific constraints

**Data Flow Constraints**:
- Personal data MUST NOT be automatically shared to business systems
- Business data MAY be aggregated for personal reporting (read-only)
- Accounting data MUST maintain integrity across all integrations
- Social media content MUST respect platform-specific guidelines

**CEO Briefing Integration**:
- Aggregates data from multiple domains (Odoo, social media, task completion)
- Generated weekly on configurable schedule
- Includes: financial summary, social media metrics, task completion rates, upcoming priorities
- Stored in `/Reports/CEO_Briefings` directory
- Risk classification: Low (read-only aggregation)

**Rationale**: Cross-domain integration enables comprehensive business insights while maintaining clear boundaries and data integrity. CEO Briefings provide high-level visibility without manual data compilation.

### XVIII. Accounting Data Protection (Gold Tier)

Accounting data requires special protection due to financial and compliance implications.

**Read Operations** (Auto-Approve):
- Retrieve account balances, transactions, reports
- Query financial data for reporting
- Access historical accounting records
- Generate financial summaries and analytics

**Write Operations** (Validation + Human Approval Required):
- Create, modify, or delete accounting transactions
- Adjust account balances
- Modify chart of accounts
- Change accounting periods or fiscal year settings

**Validation Requirements for Write Operations**:
- Transaction MUST balance (debits = credits)
- Account codes MUST exist in chart of accounts
- Amounts MUST be within reasonable ranges (configurable thresholds)
- Dates MUST be within open accounting periods
- Required fields MUST be populated
- Business rules MUST be satisfied (e.g., no negative cash)

**Validation Workflow**:
1. AI generates proposed accounting transaction
2. Validation engine checks all requirements
3. If validation fails, reject with detailed error message
4. If validation passes, write to `/Pending_Approval` with validation report
5. Human reviews transaction and validation report
6. Human approves or rejects
7. If approved, execute via Odoo MCP server
8. Log transaction to audit trail with approval details

**Backup and Recovery**:
- Accounting operations MUST be logged with sufficient detail for recovery
- System MUST support querying accounting audit trail
- System MUST alert on accounting data anomalies

**Rationale**: Accounting data is critical for business operations and compliance. Special protection prevents errors, fraud, and compliance violations while enabling read-only automation for reporting.

## Bronze Tier Architecture Constraints

**AI Logic**: Claude Code (Sonnet 4.5) via CLI interface

**Memory Layer**: Local Obsidian vault using Markdown files with YAML frontmatter for metadata

**Perception Layer**: Single file system watcher monitoring `/Inbox` for new `.md` files

**Action Layer**: File system operations only:
- Read files
- Write files
- Move files between folders
- Create/delete files within vault
- Modify file content and frontmatter

**Task Processing**: Manual invocation via `claude` CLI commands

**State Management**: Folder location represents state; no external databases

**Prohibited in Bronze Tier**:
- MCP servers
- External API integrations
- Autonomous loops ("Ralph Wiggum" mode)
- Background daemons beyond the single watcher
- Network operations
- System calls outside file I/O

## Silver Tier Architecture Enhancements

**AI Logic**: Claude Code (Sonnet 4.5) via CLI interface + scheduled reasoning loops (with approval)

**Memory Layer**: Local Obsidian vault (unchanged from Bronze)

**Perception Layer**: Multiple watchers permitted:
- Inbox watcher (detects new tasks)
- Pending_Approval watcher (detects items needing review)
- Approved watcher (detects approved actions ready for execution)

**Action Layer**: File system operations + controlled external actions via MCP:
- All Bronze Tier file operations
- Email sending (via MCP, with approval)
- Facebook Page posting (via MCP, with approval)
- Other MCP-enabled integrations (with approval)

**Task Processing**: Manual invocation + scheduled Claude reasoning loops (requires plan approval)

**State Management**: Folder-based (unchanged) + approval workflow folders

**Required Folder Structure**:
- `/Inbox` - New tasks
- `/Needs_Action` - Triaged tasks
- `/Plans` - Execution plans
- `/Pending_Approval` - Actions awaiting human review
- `/Approved` - Actions approved for execution
- `/Rejected` - Actions denied by human
- `/Done` - Completed tasks
- `/Skills` - Agent skill definitions
- `/mcp_server` - MCP server configuration

**Permitted in Silver Tier**:
- ONE MCP server for external integrations
- Multiple file system watchers (with clear responsibilities)
- Scheduled Claude reasoning loops (with plan approval)
- Email sending via MCP (with approval)
- Facebook Page posting via official Meta Graph API (with approval)
- Agent Skills architecture

**Still Prohibited in Silver Tier**:
- Personal Facebook profile automation
- Browser automation or web scraping
- Direct API calls from Claude (must use MCP)
- Actions without approval workflow
- Autonomous destructive behavior
- Multiple MCP servers

## Gold Tier Architecture Enhancements

**AI Logic**: Claude Code (Sonnet 4.6) via CLI interface + autonomous reasoning loop with comprehensive safety systems

**Memory Layer**: Local Obsidian vault (unchanged from Bronze/Silver)

**Perception Layer**: Autonomous reasoning loop continuously monitors system state:
- Inbox monitoring (detects new tasks)
- Needs_Action monitoring (detects triaged tasks ready for execution)
- Plans monitoring (detects approved plans ready for implementation)
- Pending_Approval monitoring (detects items needing human review)
- Approved monitoring (detects approved actions ready for execution)
- System health monitoring (detects errors, anomalies, resource constraints)

**Action Layer**: File system operations + multiple MCP servers for cross-domain integration:
- All Bronze/Silver Tier file operations
- Odoo Community MCP: Accounting integration (read auto-approve, write requires validation + approval)
- Social Media MCP: Facebook, Instagram, Twitter/X posting (risk-based approval)
- Email MCP: Email sending and management (risk-based approval)
- Reporting MCP: CEO Briefing generation (auto-approve)
- Additional domain-specific MCPs as authorized

**Task Processing**: Manual invocation + scheduled loops + fully autonomous reasoning loop with risk-based execution

**State Management**: Folder-based (unchanged) + approval workflow folders + audit logging

**Required Folder Structure**:
- `/Inbox` - New tasks
- `/Needs_Action` - Triaged tasks
- `/Plans` - Execution plans
- `/Pending_Approval` - Actions awaiting human review
- `/Approved` - Actions approved for execution
- `/Rejected` - Actions denied by human
- `/Done` - Completed tasks
- `/Skills` - Agent skill definitions
- `/mcp_server` - MCP server configurations (multiple servers)
- `/Audit_Logs` - Comprehensive audit trail (append-only)
- `/Reports/CEO_Briefings` - Weekly CEO briefing reports
- `/STOP` - Kill switch file (presence halts autonomous loop)

**Permitted in Gold Tier**:
- Multiple MCP servers with domain isolation
- Fully autonomous reasoning loop with safety constraints
- Risk-based auto-approval for low-risk actions
- Cross-domain data integration for reporting
- Odoo Community accounting integration (read-only auto-approve, write requires validation + approval)
- Social media integration (Facebook Pages, Instagram Business, Twitter/X via official APIs)
- CEO Briefing generation (weekly, auto-approve)
- Multi-agent skill orchestration
- Comprehensive audit logging
- Error recovery and graceful degradation

**Still Prohibited in Gold Tier**:
- Personal social media profile automation (only business accounts)
- Browser automation or web scraping
- Direct API calls from Claude (must use MCP)
- Actions without audit logging
- Accounting data modification without validation workflow
- Autonomous destructive behavior without rollback procedures
- Operations that cannot be reversed or logged

**Safety Systems**:
- Risk Engine: Classifies all actions by risk level
- Audit Logger: Comprehensive logging of all decisions and actions
- Validation Engine: Validates accounting transactions before execution
- Circuit Breaker: Pauses autonomous loop on repeated failures
- Kill Switch: File-based immediate shutdown capability
- Rollback Procedures: All high-risk actions must define rollback procedures

## Operational Model

### Bronze Tier Workflow

1. User creates task file in `/Inbox`
2. File watcher detects new file and notifies user
3. User manually invokes Claude CLI to process inbox
4. Claude reads task, generates plan, moves to appropriate folder
5. User reviews and approves actions
6. Claude executes approved actions, updates state via folder movement
7. Completed tasks move to `/Done`

### Silver Tier Workflow (with Approval Gates)

1. User creates task file in `/Inbox` OR scheduled reasoning loop triggers
2. Watcher detects new file and notifies user
3. Claude processes task and generates execution plan
4. **If plan includes external actions**:
   a. Claude writes detailed action plan to `/Pending_Approval`
   b. Plan includes: objective, actions, risks, rollback procedure
   c. Human reviews plan and moves to `/Approved` or `/Rejected`
   d. Approved watcher detects approved plan
   e. Claude executes approved actions via MCP server
   f. Results logged to `/Done` with execution summary
5. **If plan is file-system only**: Follows Bronze Tier workflow
6. Completed tasks move to `/Done`

### Gold Tier Workflow (Autonomous with Safety Systems)

**User-Initiated Tasks**:
1. User creates task file in `/Inbox` OR scheduled reasoning loop triggers
2. Autonomous loop detects new file
3. Claude processes task and generates execution plan
4. Risk Engine classifies plan and all component actions
5. **If all actions are Low-Risk**:
   a. Auto-approve and execute immediately via appropriate MCP servers
   b. Log all actions to audit trail with risk classification
   c. Results written to `/Done` with execution summary
6. **If any actions are Medium-Risk**:
   a. Check against pre-approved parameters and budgets
   b. If within bounds: auto-approve and execute
   c. If outside bounds: escalate to `/Pending_Approval` for human review
7. **If any actions are High-Risk**:
   a. Claude writes detailed action plan to `/Pending_Approval`
   b. Plan includes: objective, actions, risk assessment, validation results (if accounting), rollback procedure
   c. Human reviews plan and moves to `/Approved` or `/Rejected`
   d. Approved watcher detects approved plan
   e. Claude executes approved actions via MCP servers
   f. Results logged to `/Done` with execution summary and approval details
8. **Error Handling**:
   a. On transient failure: retry with exponential backoff (max 3 attempts)
   b. On permanent failure: execute rollback procedure if defined
   c. Log error details to audit trail
   d. If rollback fails or N consecutive failures: open circuit breaker, alert user
9. Completed tasks move to `/Done` with comprehensive execution log

**Autonomous Proactive Actions**:
1. Autonomous reasoning loop evaluates opportunities (e.g., weekly CEO Briefing generation)
2. Loop generates action plan and classifies risk
3. For low-risk proactive actions (e.g., report generation): auto-approve and execute
4. For higher-risk proactive actions: follow standard approval workflow
5. All autonomous decisions logged with reasoning to audit trail
6. Loop respects rate limits, resource budgets, and time windows
7. Loop checks for kill switch (`/STOP` file) before each action
8. Loop pauses on circuit breaker activation, alerts user

**CEO Briefing Generation** (Weekly, Auto-Approve):
1. Autonomous loop triggers on configured schedule (e.g., Monday 8 AM)
2. Reporting skill orchestrates data collection:
   a. Query Odoo MCP for financial summary (revenue, expenses, cash position)
   b. Query Social Media MCP for engagement metrics (reach, engagement, follower growth)
   c. Query file system for task completion rates and upcoming priorities
3. Reporting skill compiles data into CEO Briefing template
4. Briefing written to `/Reports/CEO_Briefings/YYYY-MM-DD-briefing.md`
5. Action logged to audit trail (risk: low, approval: auto)
6. Optional: Email briefing to configured recipient via Email MCP

**Kill Switch Activation**:
1. User creates `/STOP` file in vault root
2. Autonomous loop detects kill switch on next iteration
3. Loop immediately halts, preserves current state
4. Loop logs shutdown reason to audit trail
5. User reviews audit logs and system state
6. User removes `/STOP` file to re-enable loop (requires explicit action)

### File Format Standards

All task and state files MUST use:
- Markdown format (`.md` extension)
- YAML frontmatter for structured metadata
- Human-readable content body
- ISO 8601 dates (YYYY-MM-DD)

### Error Handling

**Bronze/Silver Tier**:
When operations fail:
- Claude MUST log error details in file frontmatter
- File MUST remain in current folder (no state transition)
- User MUST be notified with actionable error message
- No silent failures permitted
- For external actions: rollback procedure MUST be executed if defined in plan

**Gold Tier Enhancements**:
When operations fail:
- All Bronze/Silver Tier requirements apply
- Error MUST be logged to audit trail with full context
- Retry strategy MUST be applied for transient failures (exponential backoff, max 3 attempts)
- Circuit breaker MUST open after N consecutive failures (default: 5)
- Rollback procedure MUST be executed automatically if defined
- Rollback failures MUST be logged and escalated to human
- Autonomous loop MUST pause on circuit breaker activation
- User MUST be alerted for high-severity errors or circuit breaker activation
- Error patterns MUST be analyzed for anomaly detection

**Error Severity Classification**:
- **Low**: Transient failures, retryable errors, expected edge cases
- **Medium**: Repeated transient failures, degraded functionality, partial rollback success
- **High**: Permanent failures, rollback failures, circuit breaker activation, data integrity issues

**Error Response by Severity**:
- **Low**: Log, retry, continue operation
- **Medium**: Log, retry with backoff, alert if pattern detected
- **High**: Log, execute rollback, pause autonomous loop, alert user immediately

## Governance

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Version number MUST be incremented according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications, wording improvements, non-semantic changes
3. Amendment date MUST be recorded in `Last Amended` field
4. Sync Impact Report MUST be generated and prepended as HTML comment
5. Dependent templates MUST be reviewed and updated for consistency

### Compliance

- All features and implementations MUST comply with these principles
- Violations MUST be documented and justified in Architecture Decision Records (ADRs)
- Constitution supersedes all other guidance documents
- When principles conflict with implementation convenience, principles win
- Silver Tier features MUST NOT be enabled until approval workflow is implemented
- Gold Tier features MUST NOT be enabled until all safety systems are operational:
  - Risk Engine with configurable thresholds
  - Comprehensive audit logging infrastructure
  - Error recovery and circuit breaker implementation
  - Kill switch mechanism
  - All required MCP servers configured and tested
  - Validation engine for accounting operations
  - Rollback procedures defined for all high-risk actions

**Gold Tier Activation Checklist**:
- [ ] Risk Engine deployed and tested
- [ ] Audit logging infrastructure operational
- [ ] Circuit breaker pattern implemented
- [ ] Kill switch mechanism tested
- [ ] Odoo Community MCP server configured
- [ ] Social Media MCP servers configured (Facebook, Instagram, Twitter/X)
- [ ] Email MCP server configured
- [ ] Reporting MCP server configured
- [ ] Accounting validation engine deployed
- [ ] All high-risk skills have documented rollback procedures
- [ ] CEO Briefing generation tested
- [ ] Autonomous reasoning loop tested in sandbox environment
- [ ] User trained on kill switch and approval workflows

### Version Control

This constitution is version-controlled in Git. All amendments create a new commit with:
- Clear commit message describing the change
- Updated version number
- Sync Impact Report in file

### Review Cadence

Constitution MUST be reviewed:
- Before each tier upgrade (Bronze → Silver → Gold → Platinum)
- When architectural constraints change
- When new capabilities are added
- After any security incident or safety system failure
- When new MCP servers are added
- When risk classification thresholds are modified
- Quarterly at minimum for Gold Tier (increased from annually due to autonomous operation)

**Gold Tier Review Requirements**:
- Audit log analysis for anomalies and patterns
- Risk classification accuracy assessment
- Circuit breaker activation review
- Rollback procedure effectiveness evaluation
- MCP server performance and error rate review
- User satisfaction with autonomous operation
- Safety system effectiveness assessment

**Version**: 2.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-03-10
