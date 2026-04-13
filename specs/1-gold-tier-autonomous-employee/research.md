# Research Findings: Gold Tier Autonomous AI Employee

**Date**: 2026-03-12
**Feature**: Gold Tier Autonomous AI Employee
**Purpose**: Document technical research findings to inform implementation decisions

---

## 1. MCP SDK Integration Patterns

**Status**: Research completed
**Decision**: Use asyncio-native MCP client with connection pooling

### Recommended Approach

**Architecture**: Single MCP client manager with per-server connection pools

**Key Findings**:
- MCP SDK supports asyncio natively
- Connection pooling essential for 4+ concurrent servers
- Health checks should run every 30 seconds
- Reconnection logic with exponential backoff

**Implementation Pattern**:
```python
class MCPConnectionManager:
    def __init__(self):
        self.connections = {}  # server_name -> connection pool
        self.health_checks = {}  # server_name -> last check time

    async def get_connection(self, server_name: str):
        if server_name not in self.connections:
            await self._create_connection_pool(server_name)
        return await self.connections[server_name].acquire()
```

**Alternatives Considered**:
- Direct connections per request: Too slow, no connection reuse
- Single shared connection: Bottleneck for concurrent operations
- **Selected**: Connection pooling with health monitoring

**Implementation Notes**:
- Use `asyncio.create_task()` for concurrent MCP calls
- Implement timeout for all MCP operations (default: 30s)
- Log all connection state changes for debugging

---

## 2. Odoo Community JSON-RPC Integration

**Status**: Research in progress (agent still running)
**Expected completion**: Within next few minutes

**Preliminary findings** (from plan.md):
- Odoo uses XML-RPC for authentication and JSON-RPC for operations
- Authentication returns UID for subsequent calls
- Invoice creation requires: customer_id, line_items, dates
- Financial queries use `account.move` model

---

## 3. Social Media API Integration

**Status**: Research completed
**Decision**: Use official APIs with OAuth2, implement rate limiting per platform

### Facebook Graph API

**Authentication**: OAuth2 with long-lived page access tokens (60 days)

**Key Endpoints**:
- Page insights: `/v18.0/{page_id}/insights`
- Post metrics: `/v18.0/{post_id}?fields=likes,comments,shares`
- Rate limit: 200 calls/hour per user token

**Implementation**:
```python
class FacebookMetrics:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"

    async def get_page_insights(self, page_id, metrics, period='day'):
        # Fetch page-level insights with rate limiting
        pass
```

### Instagram Graph API

**Authentication**: Uses Facebook OAuth2 (Instagram Business accounts linked to Facebook Pages)

**Key Endpoints**:
- Account insights: `/v18.0/{ig_account_id}/insights`
- Media insights: `/v18.0/{media_id}/insights`
- Rate limit: 200 calls/hour (shared with Facebook)

**Metrics Available**:
- Impressions, reach, profile views
- Follower count, engagement
- Media-specific: likes, comments, saves

### Twitter API v2

**Authentication**: OAuth 2.0 with PKCE (Proof Key for Code Exchange)

**Key Endpoints**:
- Tweet metrics: `/2/tweets/{id}?tweet.fields=public_metrics`
- User metrics: `/2/users/{id}?user.fields=public_metrics`
- Rate limit: 300 requests/15 minutes (app auth)

**Token Management**:
- Access tokens expire after 2 hours
- Refresh tokens reusable with `offline.access` scope
- Implement automatic token refresh

### Rate Limiting Strategy

**Recommended Library**: Custom rate limiter with exponential backoff

**Implementation**:
```python
class RateLimiter:
    def __init__(self, max_requests, time_window, platform_name):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = deque()

    def wait_if_needed(self):
        # Block if rate limit would be exceeded
        # Remove old requests outside time window
        # Sleep if necessary
        pass
```

**Platform Limits**:
- Facebook/Instagram: 200 calls/hour
- Twitter: 300 calls/15 minutes

**Alternatives Considered**:
- Third-party aggregators (Hootsuite API): Additional cost, less control
- Web scraping: Violates ToS, unreliable
- **Selected**: Official APIs with custom rate limiting

---

## 4. Risk Classification Algorithm

**Status**: Research completed
**Decision**: Hybrid rule-based system with weighted scoring

### Algorithm Design

**Approach**: Multi-tier classification with 6 factors

**Classification Factors** (weighted 0-100):
1. **Operation Type** (30%): Read vs Write vs Irreversible
2. **Data Sensitivity** (25%): Public vs Business vs Financial vs PII
3. **Reversibility** (20%): Fully reversible vs Rollback available vs Cannot undo
4. **Financial Impact** (15%): $0 vs $1-$1000 vs >$1000
5. **External Visibility** (5%): Internal vs Business vs Public
6. **Approval History** (5%): Pre-approved vs Similar approved vs Never approved

**Risk Levels**:
- **Low**: Score 0-30 (auto-approve)
- **Medium**: Score 31-60 (conditional auto-approve)
- **High**: Score 61-100 (human approval required)

**Override Rules** (automatic HIGH risk):
- Accounting data modification (any write to financial records)
- Financial transaction > $1000
- Irreversible operation without rollback procedure
- First-time skill combination
- Multi-system operations (>2 external systems)

### Implementation

```python
class RiskClassificationEngine:
    def classify_action(self, context: ActionContext) -> RiskScore:
        # Tier 1: Check override rules
        override = self._check_overrides(context)
        if override:
            return RiskScore(risk_level=RiskLevel.HIGH, ...)

        # Tier 2: Calculate weighted scores
        base_score = self._calculate_base_score(context)

        # Tier 3: Apply context modifiers
        total_score = base_score + self._context_modifiers(context)

        # Determine risk level
        return self._classify_score(total_score)
```

**Configuration Format** (YAML):
```yaml
thresholds:
  low_max: 30
  medium_max: 60

weights:
  operation: 30
  sensitivity: 25
  reversibility: 20
  financial: 15
  visibility: 5
  history: 5
```

**Alternatives Considered**:
- ML-based classification: Not deterministic, fails auditability requirement
- Simple rule-based: Too rigid, doesn't handle nuance
- **Selected**: Hybrid weighted scoring with override rules

**Rationale**:
- Deterministic: Same inputs always produce same outputs
- Transparent: Every decision traceable to specific rules
- Configurable: Thresholds adjustable without code changes
- Auditable: Complete reasoning trail for compliance

---

## 5. Audit Logging Infrastructure

**Status**: Research completed
**Decision**: structlog with JSON output and append-only files

### Recommended Library: structlog

**Rationale**:
- Native JSON output for machine parsing
- Context binding (attach data once, use throughout call chain)
- Dual output: JSON for machines, colored console for humans
- Performance: Lazy evaluation, efficient processing
- Testing-friendly: Easy to capture and assert on logs

**Alternatives Considered**:
- `python-json-logger`: Simpler but less flexible
- Standard `logging` + custom formatters: More work, less maintainable
- **Selected**: structlog

### Implementation

```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

class AuditLogger:
    @contextmanager
    def log_action(self, action_type, description, risk_level,
                   approval_method, input_data, **extra_context):
        log = self.logger.bind(
            action_id=self._generate_action_id(),
            action_type=action_type,
            risk_level=risk_level.value,
            ...
        )

        try:
            log.info("action_started")
            yield ActionLogContext(log)
            log.info("action_completed", status="success", ...)
        except Exception as e:
            log.error("action_failed", status="failure", ...)
            raise
```

### Log Format

**JSON format** (machine-parseable):
```json
{
  "event": "action_completed",
  "timestamp": "2026-03-12T14:32:15.123456+00:00",
  "action_id": "act_a1b2c3d4e5f6",
  "action_type": "task.process",
  "risk_level": "medium",
  "approval_method": "auto_approved",
  "input_data": {...},
  "output_data": {...},
  "status": "success",
  "duration_ms": 150.0
}
```

### Rotation and Retention Strategy

**Rotation**: Time-based with compression
- Rotate daily at midnight UTC
- Compress files older than 1 day (gzip)
- Keep 90 days in hot storage

**Retention Policy**:
- Hot storage: 30 days uncompressed
- Warm storage: 60 days compressed
- Cold storage: 7 years in S3/archive
- Deletion: After 7 years (compliance requirement)

**Implementation**:
```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    filename="audit.jsonl",
    when="midnight",
    interval=1,
    backupCount=90,
    encoding="utf-8",
    utc=True
)
```

### Query and Analysis

**Query Interface**:
```python
class AuditLogQuery:
    def query(self, start_date, end_date, action_type,
              risk_level, status, limit):
        # Efficient JSONL querying
        for log_file in self._get_log_files(start_date, end_date):
            for entry in self._read_log_file(log_file):
                if self._matches_filters(entry, ...):
                    yield entry
```

**Common Queries**:
- Failed actions in last 7 days
- High-risk actions in last 30 days
- Actions by specific user
- Actions for specific task

---

## 6. Circuit Breaker Pattern

**Status**: Research completed
**Decision**: aiobreaker library with custom monitoring

### Recommended Library: aiobreaker

**Rationale**:
- Asyncio-native (doesn't block event loop)
- Decorator-based API (clean integration)
- State listeners for monitoring
- Thread-safe

**Alternatives Considered**:
- `pybreaker`: Most popular but NOT asyncio-native (synchronous)
- `circuitbreaker`: Too basic, no asyncio support
- **Selected**: aiobreaker

### Configuration

**Per-server configuration**:
```python
MCP_SERVER_CONFIGS = {
    "odoo": {
        "fail_max": 5,           # Open after 5 consecutive failures
        "timeout_duration": 300,  # 5 minutes before half-open
    },
    "social": {
        "fail_max": 3,           # More sensitive (less critical)
        "timeout_duration": 180,  # 3 minutes
    },
}
```

### Implementation Pattern

```python
from aiobreaker import CircuitBreaker, CircuitBreakerError

# Initialize with monitoring
breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=300,
    name="odoo-mcp"
)

# Register state listeners
def on_state_change(breaker, old_state, new_state):
    logger.warning(f"Circuit breaker: {breaker.name} "
                   f"{old_state.name} -> {new_state.name}")
    # Emit metrics, send alerts

breaker.add_listener(on_state_change)

# Use as decorator
@breaker
async def call_mcp_server():
    # Your async code
    pass
```

### State Transitions

**States**:
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service failing, reject requests immediately (fail fast)
- **HALF_OPEN**: Testing recovery, allow limited requests

**Transitions**:
1. CLOSED → OPEN: After N consecutive failures (default: 5)
2. OPEN → HALF_OPEN: After timeout period (default: 5 minutes)
3. HALF_OPEN → CLOSED: On successful request
4. HALF_OPEN → OPEN: On failure during testing

### Integration with Retry Logic

**Correct layering** (circuit breaker wraps retry):
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@circuit_breaker  # Outer layer
@retry(           # Inner layer
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10)
)
async def call_external_api():
    # Retry attempts 3 times for transient errors
    # Circuit breaker tracks overall success/failure pattern
    pass
```

### Monitoring

**Metrics to track**:
- Circuit breaker state (gauge: 0=closed, 1=open, 2=half_open)
- Failure count per server
- Success count per server
- Time in open state
- State transition events

**Alert levels**:
- **CRITICAL**: Circuit opens (service unavailable)
- **WARNING**: High failure rate (>50%), circuit half-open
- **INFO**: Circuit closes (recovery)

---

## 7. CEO Briefing Templates

**Status**: Research completed
**Decision**: Jinja2 templates with Markdown and HTML output

### Template Structure

**Recommended Structure**:
1. **Executive Summary** (30 seconds read): 3 bullet points with key takeaways
2. **Business Operations**: Task completion metrics, upcoming priorities
3. **Financial Performance**: Revenue, expenses, profit/loss with trends
4. **Marketing Performance**: Social media engagement across platforms
5. **Risk Alerts**: Failed tasks, system errors, anomalies
6. **Recommendations**: 3 actionable items for next week

**Optimal Length**: 2-3 pages (per ADR-003)
**Reading Time**: 5-7 minutes full read, 1-2 minutes for summary

### Markdown Template

```markdown
# CEO Briefing: Week Ending {{WEEK_ENDING_DATE}}

**Generated:** {{GENERATION_TIMESTAMP}}
**Period:** {{WEEK_START_DATE}} to {{WEEK_ENDING_DATE}}

## Executive Summary

• {{KEY_ACHIEVEMENT}}
• {{KEY_CONCERN}}
• {{KEY_METRIC}}

## Financial Performance

| Metric | This Week | Last Week | Change | YTD |
|--------|-----------|-----------|--------|-----|
| Revenue | {{REVENUE}} | {{REVENUE_LAST}} | {{REVENUE_CHANGE}}% | {{REVENUE_YTD}} |
| Expenses | {{EXPENSES}} | {{EXPENSES_LAST}} | {{EXPENSES_CHANGE}}% | {{EXPENSES_YTD}} |
| Net Profit | {{NET_PROFIT}} | {{NET_PROFIT_LAST}} | {{NET_PROFIT_CHANGE}}% | {{NET_PROFIT_YTD}} |

[Additional sections...]
```

### Template Engine: Jinja2

**Rationale**:
- Industry standard for Python
- Powerful template inheritance
- Built-in filters for formatting
- Safe by default (auto-escaping)

**Implementation**:
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ceo_briefing.md.j2')

output = template.render(
    WEEK_ENDING_DATE=week_end,
    REVENUE=format_currency(revenue),
    ...
)
```

### Data Aggregation Approach

**Strategy**: Parallel data collection with graceful degradation

```python
async def aggregate_briefing_data(week_start, week_end):
    # Fetch data from all sources in parallel
    results = await asyncio.gather(
        fetch_financial_data(week_start, week_end),
        fetch_social_metrics(week_start, week_end),
        fetch_task_completion(week_start, week_end),
        return_exceptions=True  # Don't fail if one source fails
    )

    # Handle partial data
    briefing_data = {}
    for result in results:
        if isinstance(result, Exception):
            # Log error, mark section as unavailable
            continue
        briefing_data.update(result)

    return briefing_data
```

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| MCP SDK | Asyncio-native with connection pooling | Performance, concurrent operations |
| Odoo Integration | JSON-RPC with retry logic | Official API, reliable |
| Social Media | Official APIs with rate limiting | Compliance, reliability |
| Risk Classification | Hybrid rule-based weighted scoring | Deterministic, auditable, configurable |
| Audit Logging | structlog with JSON output | Performance, flexibility, machine-parseable |
| Circuit Breaker | aiobreaker | Asyncio-native, monitoring support |
| CEO Briefing | Jinja2 templates (Markdown + HTML) | Industry standard, flexible |

---

## Implementation Priorities

Based on research findings, recommended implementation order:

1. **Phase 1: Foundation** (Tasks T001-T018)
   - Audit logging (structlog)
   - Risk engine (rule-based)
   - Circuit breaker (aiobreaker)
   - Retry logic (tenacity)

2. **Phase 2: MCP Servers** (Tasks T021-T047)
   - Odoo MCP (JSON-RPC)
   - Social MCP (Facebook, Instagram, Twitter)
   - Email MCP (SMTP)
   - Reporting MCP (Jinja2)

3. **Phase 3: Autonomous Loop** (Tasks T050-T062)
   - Ralph Wiggum Loop (Plan → Execute → Reflect → Retry)
   - Task scanner
   - Skill orchestration

4. **Phase 4: Integration** (Tasks T087-T110)
   - CEO briefing generation
   - End-to-end testing
   - Performance optimization

---

## Open Questions

1. **Odoo JSON-RPC**: Awaiting completion of research agent (expected soon)
2. **Token Refresh**: Should we implement automatic OAuth2 token refresh or require manual renewal?
   - **Recommendation**: Implement automatic refresh for Twitter, manual for Facebook/Instagram (60-day tokens)
3. **MCP Server Deployment**: Should MCP servers run as separate processes or embedded in main application?
   - **Recommendation**: Embedded initially for simplicity, separate processes for production scaling

---

**Last Updated**: 2026-03-12
**Research Agents**: 6/7 completed (Odoo JSON-RPC pending)
