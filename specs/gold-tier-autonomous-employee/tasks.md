# Tasks: Gold Tier Autonomous AI Employee

**Input**: Design documents from `/specs/gold-tier-autonomous-employee/`
**Prerequisites**: plan.md ✓, spec.md ✓, ADRs ✓

**Organization**: Tasks are organized by implementation phase from plan.md. Each phase has clear deliverables and exit criteria.

## Format: `[ID] [P?] [Phase] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Phase]**: Which phase this task belongs to (P0, P1, P2, etc.)

---

## Phase 0: Research & Discovery (Week 1)

**Goal**: Validate external API access, understand Odoo schema, prototype MCP tool structure

**Exit Criteria**:
- Successfully created test invoice in Odoo via JSON-RPC
- Successfully fetched engagement metrics from all social platforms
- Successfully sent test email
- MCP tool prototype working with Claude

### Odoo API Research

- [ ] T001 [P] [P0] Set up local Odoo Community Edition 17.0 using Docker
  - Pull official Odoo Docker image
  - Configure PostgreSQL container
  - Access Odoo web interface at localhost:8069
  - Create test database
  - **Acceptance**: Odoo running and accessible

- [ ] T002 [P0] Test Odoo JSON-RPC authentication flow
  - Write Node.js script to authenticate via /jsonrpc endpoint
  - Test with test database credentials
  - Verify session UID returned
  - **Acceptance**: Script successfully authenticates and returns UID

- [ ] T003 [P0] Identify Odoo models for invoices (account.move)
  - Use Odoo web interface to explore Accounting module
  - Document account.move model fields
  - Document account.move.line model fields (invoice lines)
  - **Acceptance**: Documented invoice model structure

- [ ] T004 [P0] Identify Odoo models for financial reports
  - Explore account.report model
  - Document P&L report structure
  - Document balance sheet structure
  - **Acceptance**: Documented financial report models

- [ ] T005 [P0] Document required Odoo permissions
  - Identify user groups needed (Accounting/Billing)
  - Document API access permissions
  - Create test user with appropriate permissions
  - **Acceptance**: Documented permission requirements

- [ ] T006 [P0] Prototype invoice creation via JSON-RPC
  - Write script to create test invoice
  - Include invoice lines with products
  - Verify invoice appears in Odoo UI
  - **Acceptance**: Test invoice created successfully via API

### Social Media API Research

- [ ] T007 [P] [P0] Create Facebook/Instagram developer app
  - Register at developers.facebook.com
  - Create new app
  - Add Instagram Graph API product
  - Get App ID and App Secret
  - **Acceptance**: Developer app created with credentials

- [ ] T008 [P0] Test Facebook Graph API authentication (OAuth 2.0)
  - Implement OAuth 2.0 flow
  - Get user access token
  - Test token with /me endpoint
  - **Acceptance**: Successfully authenticated and retrieved user data

- [ ] T009 [P0] Test Facebook/Instagram engagement metrics endpoints
  - Test /page/insights endpoint
  - Test /media/insights endpoint (Instagram)
  - Document available metrics (likes, comments, shares, reach)
  - **Acceptance**: Successfully retrieved engagement data

- [ ] T010 [P] [P0] Create Twitter developer account
  - Apply for developer account at developer.twitter.com
  - Create new app
  - Get API keys and tokens
  - **Acceptance**: Twitter developer account with API credentials

- [ ] T011 [P0] Test Twitter API v2 authentication
  - Implement OAuth 2.0 flow
  - Get access token
  - Test with /users/me endpoint
  - **Acceptance**: Successfully authenticated with Twitter API

- [ ] T012 [P0] Test Twitter engagement metrics endpoints
  - Test /tweets endpoint with metrics
  - Document available metrics (likes, retweets, replies)
  - **Acceptance**: Successfully retrieved tweet metrics

- [ ] T013 [P0] Document rate limits for all social platforms
  - Facebook: 200 calls/hour per user
  - Instagram: 200 calls/hour per user
  - Twitter: 300 requests/15min per app
  - **Acceptance**: Rate limits documented in research.md

### Email Integration Research

- [ ] T014 [P] [P0] Test SMTP connection (Gmail)
  - Configure Gmail App Password
  - Test connection with Nodemailer
  - Send test email
  - **Acceptance**: Test email sent successfully

- [ ] T015 [P] [P0] Test IMAP connection for inbox reading
  - Configure IMAP access
  - Connect with node-imap
  - Retrieve inbox messages
  - **Acceptance**: Successfully retrieved inbox messages

- [ ] T016 [P0] Verify OAuth 2.0 flow for Gmail
  - Set up Google Cloud project
  - Enable Gmail API
  - Implement OAuth 2.0 flow
  - Test with Gmail API
  - **Acceptance**: OAuth 2.0 authentication working

- [ ] T017 [P0] Test email sending with attachments
  - Create test PDF attachment
  - Send email with attachment via SMTP
  - Verify receipt
  - **Acceptance**: Email with attachment received

### MCP Protocol Research

- [ ] T018 [P] [P0] Review MCP SDK documentation
  - Read @modelcontextprotocol/sdk docs
  - Understand server creation pattern
  - Understand tool definition format
  - **Acceptance**: MCP concepts understood

- [ ] T019 [P0] Create minimal MCP server prototype
  - Initialize Node.js project
  - Install MCP SDK
  - Create server with 1 test tool
  - **Acceptance**: MCP server runs without errors

- [ ] T020 [P0] Test MCP tool invocation from Claude
  - Configure Claude to connect to test server
  - Invoke test tool
  - Verify response
  - **Acceptance**: Claude successfully invokes MCP tool

- [ ] T021 [P0] Understand MCP error handling patterns
  - Test error responses
  - Document error format
  - Test retry behavior
  - **Acceptance**: Error handling patterns documented

### Documentation

- [ ] T022 [P0] Create research.md with all findings
  - Document API endpoints and authentication flows
  - Document rate limits and quotas
  - Document discovered constraints
  - Include code examples from prototypes
  - **Acceptance**: research.md complete with all Phase 0 findings

**Phase 0 Checkpoint**: All external APIs validated, MCP prototype working, research.md complete

---

## Phase 1: Design & Contracts (Week 2)

**Goal**: Define data models, API contracts, and detailed architecture

### Data Model Design

- [ ] T023 [P] [P1] Define TypeScript interfaces for Odoo MCP tool inputs/outputs in specs/gold-tier-autonomous-employee/data-model.md
- [ ] T024 [P] [P1] Define TypeScript interfaces for Social MCP tool inputs/outputs
- [ ] T025 [P] [P1] Define TypeScript interfaces for Email MCP tool inputs/outputs
- [ ] T026 [P] [P1] Define TypeScript interfaces for Reporting MCP tool inputs/outputs
- [ ] T027 [P] [P1] Define database schema for task history (SQLite)
- [ ] T028 [P] [P1] Define database schema for cached data
- [ ] T029 [P] [P1] Define CEO briefing data structure

### API Contract Definition

- [ ] T030 [P] [P1] Document Odoo MCP tools contract in specs/gold-tier-autonomous-employee/contracts/odoo-mcp.md
- [ ] T031 [P] [P1] Document Social MCP tools contract in contracts/social-mcp.md
- [ ] T032 [P] [P1] Document Email MCP tools contract in contracts/email-mcp.md
- [ ] T033 [P] [P1] Document Reporting MCP tools contract in contracts/reporting-mcp.md
- [ ] T034 [P1] Define error codes and error response format across all contracts
- [ ] T035 [P1] Define retry policies per tool in contracts

### Architecture Refinement

- [ ] T036 [P] [P1] Design Ralph Wiggum Loop state machine diagram
- [ ] T037 [P] [P1] Design task queue structure
- [ ] T038 [P] [P1] Design logging and observability strategy
- [ ] T039 [P] [P1] Design secret management approach (.env structure)
- [ ] T040 [P] [P1] Design backup and recovery strategy

### Documentation

- [ ] T041 [P1] Write specs/gold-tier-autonomous-employee/quickstart.md with setup steps

**Phase 1 Checkpoint**: All contracts defined, data models documented, quickstart guide ready

---

## Phase 2: Foundation (Weeks 3-4)

**Goal**: Implement core infrastructure, shared utilities, and Odoo MCP server

### Monorepo Setup

- [ ] T042 [P2] Initialize monorepo with npm workspaces at repository root
- [ ] T043 [P] [P2] Set up TypeScript configuration (base + per-package)
- [ ] T044 [P] [P2] Set up Jest for testing
- [ ] T045 [P] [P2] Set up ESLint and Prettier
- [ ] T046 [P2] Create packages/shared package with common types
- [ ] T047 [P2] Set up Docker Compose for local development

### Shared Infrastructure (packages/shared)

- [ ] T048 [P] [P2] Implement structured logging in packages/shared/src/logger/
- [ ] T049 [P] [P2] Implement error classes hierarchy in packages/shared/src/errors/
- [ ] T050 [P] [P2] Implement retry utility with exponential backoff in packages/shared/src/utils/
- [ ] T051 [P] [P2] Implement circuit breaker utility in packages/shared/src/utils/
- [ ] T052 [P] [P2] Implement configuration loader in packages/shared/src/config/
- [ ] T053 [P2] Write unit tests for shared utilities (80%+ coverage)

### Odoo MCP Server (packages/odoo-mcp)

- [ ] T054 [P2] Implement JSON-RPC client in packages/odoo-mcp/src/odoo-client/client.ts
- [ ] T055 [P2] Implement authentication in packages/odoo-mcp/src/odoo-client/auth.ts
- [ ] T056 [P2] Implement connection pooling in odoo-client
- [ ] T057 [P] [P2] Implement create_invoice tool in packages/odoo-mcp/src/tools/create-invoice.ts
- [ ] T058 [P] [P2] Implement get_financial_summary tool in packages/odoo-mcp/src/tools/get-financial-summary.ts
- [ ] T059 [P] [P2] Implement get_profit_loss tool in packages/odoo-mcp/src/tools/get-profit-loss.ts
- [ ] T060 [P2] Implement error handling and retry logic in Odoo MCP
- [ ] T061 [P2] Write unit tests for Odoo MCP (mock Odoo responses)
- [ ] T062 [P2] Write integration tests for Odoo MCP (against test Odoo instance)
- [ ] T063 [P2] Create Dockerfile for Odoo MCP server
- [ ] T064 [P2] Update contracts/odoo-mcp.md with actual implementation details

### Agent Storage (agent/src/storage)

- [ ] T065 [P2] Set up SQLite database in agent/src/storage/db.ts
- [ ] T066 [P2] Create migration system in agent/src/storage/migrations/
- [ ] T067 [P] [P2] Implement task history table schema
- [ ] T068 [P] [P2] Implement cached data table schema
- [ ] T069 [P] [P2] Implement audit log table schema
- [ ] T070 [P2] Write database access layer
- [ ] T071 [P2] Write unit tests for storage layer

**Phase 2 Checkpoint**: Odoo MCP server functional, shared infrastructure ready, 80%+ test coverage

---

## Phase 3: Integration (Weeks 5-6)

**Goal**: Implement Social, Email, and Reporting MCP servers

### Social MCP Server (packages/social-mcp)

- [ ] T072 [P] [P3] Implement Facebook Graph API client in packages/social-mcp/src/clients/facebook.ts
- [ ] T073 [P] [P3] Implement Instagram Graph API client in packages/social-mcp/src/clients/instagram.ts
- [ ] T074 [P] [P3] Implement Twitter API v2 client in packages/social-mcp/src/clients/twitter.ts
- [ ] T075 [P3] Implement OAuth 2.0 token refresh logic
- [ ] T076 [P] [P3] Implement get_engagement_summary tool in packages/social-mcp/src/tools/
- [ ] T077 [P] [P3] Implement schedule_post tool with approval workflow
- [ ] T078 [P3] Implement rate limit handling
- [ ] T079 [P3] Write unit tests for Social MCP (mock API responses)
- [ ] T080 [P3] Write integration tests (against test accounts)
- [ ] T081 [P3] Create Dockerfile for Social MCP server

### Email MCP Server (packages/email-mcp)

- [ ] T082 [P] [P3] Implement SMTP client in packages/email-mcp/src/clients/smtp.ts
- [ ] T083 [P] [P3] Implement IMAP client in packages/email-mcp/src/clients/imap.ts
- [ ] T084 [P3] Implement OAuth 2.0 for Gmail
- [ ] T085 [P] [P3] Implement send_email tool in packages/email-mcp/src/tools/
- [ ] T086 [P] [P3] Implement get_inbox_summary tool
- [ ] T087 [P3] Implement attachment handling
- [ ] T088 [P3] Write unit tests for Email MCP
- [ ] T089 [P3] Write integration tests (test email account)
- [ ] T090 [P3] Create Dockerfile for Email MCP server

### Reporting MCP Server (packages/reporting-mcp)

- [ ] T091 [P3] Implement MCP client to call other servers in packages/reporting-mcp/src/
- [ ] T092 [P] [P3] Implement business summary aggregator in packages/reporting-mcp/src/aggregators/business.ts
- [ ] T093 [P] [P3] Implement financial summary aggregator in aggregators/financial.ts
- [ ] T094 [P] [P3] Implement marketing summary aggregator in aggregators/marketing.ts
- [ ] T095 [P] [P3] Implement risk detection logic in aggregators/risks.ts
- [ ] T096 [P3] Implement generate_ceo_briefing tool in packages/reporting-mcp/src/tools/
- [ ] T097 [P] [P3] Implement Markdown formatter in packages/reporting-mcp/src/formatters/
- [ ] T098 [P3] Write unit tests for Reporting MCP
- [ ] T099 [P3] Write integration tests (mock other MCP servers)
- [ ] T100 [P3] Create Dockerfile for Reporting MCP server

### Docker Compose Integration

- [ ] T101 [P3] Add all 4 MCP servers to docker-compose.yml
- [ ] T102 [P3] Configure networking between containers
- [ ] T103 [P3] Configure environment variables in .env.example
- [ ] T104 [P3] Add health checks to all services
- [ ] T105 [P3] Test full stack startup with docker-compose up

**Phase 3 Checkpoint**: All 4 MCP servers operational, can generate CEO briefing

---

## Phase 4: Autonomy (Weeks 7-8)

**Goal**: Implement Ralph Wiggum Loop and autonomous task orchestration

### Ralph Wiggum Loop (agent/src/ralph-wiggum-loop)

- [ ] T106 [P] [P4] Implement Planner in agent/src/ralph-wiggum-loop/planner.ts
- [ ] T107 [P] [P4] Implement Executor in agent/src/ralph-wiggum-loop/executor.ts
- [ ] T108 [P] [P4] Implement Reflector in agent/src/ralph-wiggum-loop/reflector.ts
- [ ] T109 [P] [P4] Implement Retry logic in agent/src/ralph-wiggum-loop/retry.ts
- [ ] T110 [P4] Implement guardrails (max iterations, token budget, circuit breaker)
- [ ] T111 [P4] Write unit tests for each Ralph Wiggum phase
- [ ] T112 [P4] Write integration tests for full loop

### MCP Client (agent/src/mcp-client)

- [ ] T113 [P4] Implement MCP client to connect to all 4 servers in agent/src/mcp-client/client.ts
- [ ] T114 [P4] Implement connection management
- [ ] T115 [P4] Implement tool discovery
- [ ] T116 [P4] Implement tool invocation with error handling
- [ ] T117 [P4] Write unit tests for MCP client

### Task Definitions (agent/src/tasks)

- [ ] T118 [P] [P4] Define CEO briefing task in agent/src/tasks/ceo-briefing.ts
- [ ] T119 [P] [P4] Define invoice creation task in agent/src/tasks/invoice-creation.ts
- [ ] T120 [P] [P4] Define social posting task in agent/src/tasks/social-posting.ts
- [ ] T121 [P4] Implement task queue
- [ ] T122 [P4] Implement task scheduler (cron-like)
- [ ] T123 [P4] Write tests for each task type

### Agent Orchestrator

- [ ] T124 [P4] Implement main agent loop in agent/src/index.ts
- [ ] T125 [P4] Implement task dispatcher
- [ ] T126 [P4] Implement result aggregation
- [ ] T127 [P4] Implement error escalation
- [ ] T128 [P4] Implement graceful shutdown
- [ ] T129 [P4] Create Dockerfile for agent
- [ ] T130 [P4] Add agent to docker-compose.yml

### End-to-End Testing

- [ ] T131 [P4] Test autonomous CEO briefing generation
- [ ] T132 [P4] Test autonomous invoice creation
- [ ] T133 [P4] Test error recovery scenarios
- [ ] T134 [P4] Test graceful degradation (MCP server down)
- [ ] T135 [P4] Test circuit breaker activation

**Phase 4 Checkpoint**: Agent autonomously generates CEO briefing, error recovery working

---

## Phase 5: Reporting & Scheduling (Week 9)

**Goal**: Implement weekly CEO briefing automation and daily alerts

- [ ] T136 [P] [P5] Implement cron scheduler for weekly briefings
- [ ] T137 [P] [P5] Implement daily alert checker
- [ ] T138 [P5] Implement timezone handling
- [ ] T139 [P5] Configure Monday 9:00 AM briefing schedule
- [ ] T140 [P] [P5] Implement alert detection logic
- [ ] T141 [P] [P5] Implement severity classification
- [ ] T142 [P5] Implement alert deduplication (max 3/day)
- [ ] T143 [P5] Implement alert delivery (email + Slack)
- [ ] T144 [P] [P5] Implement week-over-week comparison
- [ ] T145 [P] [P5] Implement trend analysis
- [ ] T146 [P5] Implement top 3 recommendations generation
- [ ] T147 [P5] Implement executive summary (3 bullets)
- [ ] T148 [P5] Enhance Markdown formatting
- [ ] T149 [P5] Implement email delivery with PDF attachment
- [ ] T150 [P5] Implement delivery confirmation
- [ ] T151 [P5] Write tests for scheduling and alerting

**Phase 5 Checkpoint**: Weekly briefings automated, daily alerts operational

---

## Phase 6: Hardening & Production (Weeks 10-11)

**Goal**: Security audit, performance optimization, production deployment

### Security Audit

- [ ] T152 [P] [P6] Review all API key storage (must be in env vars)
- [ ] T153 [P] [P6] Review authentication flows
- [ ] T154 [P] [P6] Review data encryption
- [ ] T155 [P] [P6] Review audit logging
- [ ] T156 [P6] Run security scanner (npm audit, Snyk)
- [ ] T157 [P6] Fix all critical and high vulnerabilities
- [ ] T158 [P6] Document security measures

### Performance Optimization

- [ ] T159 [P6] Profile CEO briefing generation
- [ ] T160 [P6] Optimize slow queries/API calls
- [ ] T161 [P6] Implement caching where appropriate
- [ ] T162 [P6] Load test with 100 concurrent tasks
- [ ] T163 [P6] Verify latency targets (p95 < thresholds)
- [ ] T164 [P6] Optimize Docker images (multi-stage builds)

### Observability

- [ ] T165 [P] [P6] Set up structured logging to files
- [ ] T166 [P] [P6] Implement distributed tracing (trace IDs)
- [ ] T167 [P] [P6] Implement metrics collection
- [ ] T168 [P6] Set up log rotation
- [ ] T169 [P6] Document observability setup

### Alerting & Monitoring

- [ ] T170 [P] [P6] Implement health check endpoints
- [ ] T171 [P] [P6] Set up uptime monitoring
- [ ] T172 [P6] Configure critical alerts
- [ ] T173 [P6] Configure warning alerts
- [ ] T174 [P6] Test alert delivery
- [ ] T175 [P6] Document on-call procedures

### Runbooks

- [ ] T176 [P] [P6] Write runbook: Restart MCP server
- [ ] T177 [P] [P6] Write runbook: Clear task queue
- [ ] T178 [P] [P6] Write runbook: Regenerate CEO briefing
- [ ] T179 [P] [P6] Write runbook: Rotate API keys
- [ ] T180 [P] [P6] Write runbook: Investigate failed task
- [ ] T181 [P] [P6] Write runbook: Backup and restore

### Production Deployment

- [ ] T182 [P6] Set up production environment (VM or cloud)
- [ ] T183 [P6] Configure production environment variables
- [ ] T184 [P6] Set up SSL/TLS certificates
- [ ] T185 [P6] Deploy Docker Compose stack
- [ ] T186 [P6] Run smoke tests in production
- [ ] T187 [P6] Configure automated backups
- [ ] T188 [P6] Test backup/restore procedures

### Documentation

- [ ] T189 [P] [P6] Update README with production setup
- [ ] T190 [P] [P6] Document environment variables
- [ ] T191 [P] [P6] Document backup/restore procedures
- [ ] T192 [P] [P6] Document troubleshooting guide
- [ ] T193 [P6] Create architecture diagram
- [ ] T194 [P6] Validate quickstart.md against production

**Phase 6 Checkpoint**: Production deployment complete, first CEO briefing delivered

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Research)**: No dependencies - start immediately
- **Phase 1 (Design)**: Depends on Phase 0 completion
- **Phase 2 (Foundation)**: Depends on Phase 1 completion
- **Phase 3 (Integration)**: Depends on Phase 2 completion (Odoo MCP + shared infrastructure)
- **Phase 4 (Autonomy)**: Depends on Phase 3 completion (all 4 MCP servers operational)
- **Phase 5 (Reporting)**: Depends on Phase 4 completion (Ralph Wiggum Loop working)
- **Phase 6 (Hardening)**: Depends on Phase 5 completion (full system functional)

### Parallel Opportunities

- Within Phase 0: T001, T007, T010, T014, T015, T018 can run in parallel (different APIs)
- Within Phase 2: T048-T052 (shared utilities) can run in parallel
- Within Phase 2: T057-T059 (Odoo tools) can run in parallel after T054-T056 complete
- Within Phase 3: All 3 MCP servers (Social, Email, Reporting) can be developed in parallel
- Within Phase 4: T106-T109 (Ralph Wiggum components) can run in parallel
- Within Phase 6: Most security, performance, and documentation tasks can run in parallel

### Critical Path

Phase 0 → Phase 1 → Phase 2 (Odoo MCP) → Phase 3 (All MCPs) → Phase 4 (Autonomy) → Phase 5 (Scheduling) → Phase 6 (Production)

**Estimated Duration**: 11 weeks (as per plan.md)

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

1. Complete Phase 0: Research & Discovery
2. Complete Phase 1: Design & Contracts
3. Complete Phase 2: Foundation (Odoo MCP only)
4. **STOP and VALIDATE**: Test Odoo MCP independently
5. Continue with Phase 3-6 if Phase 2 successful

### Incremental Delivery

- After Phase 2: Odoo integration working (can create invoices, fetch financial data)
- After Phase 3: All integrations working (social, email, reporting)
- After Phase 4: Autonomous operations working (Ralph Wiggum Loop)
- After Phase 5: Automated briefings and alerts
- After Phase 6: Production-ready system

### Risk Mitigation

- Test each MCP server independently before integration
- Implement circuit breakers and retry logic early
- Use feature flags for autonomous operations
- Maintain dry-run mode for invoice creation
- Require approval for high-value operations

---

## Notes

- [P] tasks = can run in parallel (different files, no dependencies)
- [Phase] label maps task to specific implementation phase
- Each phase should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate phase independently
- All file paths assume monorepo structure from plan.md
- Test coverage target: 80%+ for all packages
