# ADR-002: Ralph Wiggum Loop Pattern for Autonomous Execution

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-03-12
- **Feature:** gold-tier-autonomous-employee
- **Context:** The Gold Tier AI Employee must execute complex, multi-step tasks autonomously (e.g., "Generate CEO briefing" requires fetching financial data, social metrics, analyzing trends, and formatting report). We need a pattern for autonomous task execution that can handle failures, learn from mistakes, and retry intelligently.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core execution pattern for all autonomous operations
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Simple retry vs Ralph Wiggum vs Event-driven
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all autonomous task execution
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement the **Ralph Wiggum Loop** pattern for autonomous task execution:

```
Loop:
  1. PLAN: Break task into subtasks, identify dependencies
  2. EXECUTE: Run subtasks, call MCP tools, gather results
  3. REFLECT: Analyze results, identify failures, extract learnings
  4. RETRY: Adjust plan based on reflection, retry failed subtasks

Exit conditions:
  - Task completed successfully
  - Max iterations reached (5)
  - Unrecoverable error detected
  - Token budget exhausted (50K tokens)
```

**Key Components:**

- **Planning Phase**: AI agent analyzes task, breaks into subtasks, identifies which MCP tools to call
- **Execution Phase**: Calls MCP tools, handles responses, aggregates results
- **Reflection Phase**: Evaluates what worked/failed, identifies root causes, proposes adjustments
- **Retry Phase**: Re-plans with learnings, retries failed operations with different approach
- **Guardrails**: Max 5 iterations, 50K token budget, circuit breaker after 10 consecutive failures

**Example Flow:**
```
Task: "Generate CEO briefing for week ending 2026-03-08"

Iteration 1:
  PLAN: [Fetch Odoo data, Fetch social data, Fetch email summary, Generate report]
  EXECUTE: Odoo ✓, Social ✗ (rate limit), Email ✓
  REFLECT: Social API rate limited, need to wait or use cached data
  RETRY: Use cached social data from yesterday

Iteration 2:
  PLAN: [Use cached social data, Generate report]
  EXECUTE: Generate report ✓
  REFLECT: Success, report complete
  EXIT: Task completed
```

## Consequences

### Positive

- **Adaptive Behavior**: System learns from failures and adjusts approach (e.g., switches to cached data when API fails)
- **Multi-Step Reasoning**: Can handle complex tasks requiring multiple API calls and data transformations
- **Transparency**: Reflection phase provides audit trail of decisions and reasoning
- **Error Recovery**: Intelligent retry with context awareness (not blind retries)
- **Graceful Degradation**: Can complete task with partial data when some sources fail
- **Debugging**: Clear log of plan → execute → reflect → retry makes debugging easier
- **Testability**: Each phase can be tested independently

### Negative

- **Token Consumption**: Reflection phase adds 5-10K tokens per iteration (expensive for simple tasks)
- **Latency**: Multi-iteration loops take longer than direct execution (30s vs 5s for complex tasks)
- **Complexity**: More complex than simple retry logic, harder to reason about
- **Prompt Engineering**: Requires careful prompting to prevent infinite loops or poor decisions
- **Unpredictability**: Adaptive behavior means same task might execute differently each time
- **Cost**: Higher Claude API costs due to token consumption

## Alternatives Considered

### Alternative A: Simple Retry Loop

**Description**: Retry failed operations N times with exponential backoff, no planning or reflection.

```
for i in range(5):
  try:
    result = execute_task()
    return result
  except Exception as e:
    if i == 4: raise
    sleep(2 ** i)
```

**Pros**:
- Simple to implement and understand
- Low token consumption (no reflection)
- Fast execution (no planning overhead)
- Predictable behavior

**Cons**:
- **No Learning**: Retries same approach repeatedly, doesn't adapt
- **No Multi-Step**: Can't break complex tasks into subtasks
- **Blind Retries**: Retries even when error is unrecoverable (e.g., 404)
- **No Context**: Doesn't understand why failure occurred

**Why Rejected**: Too simplistic for autonomous AI Employee. Can't handle complex multi-step tasks like "Generate CEO briefing" which requires orchestrating multiple data sources and adapting to failures.

### Alternative B: Event-Driven Workflow

**Description**: Define tasks as state machines with event handlers. Events trigger state transitions.

```
States: [FETCH_ODOO, FETCH_SOCIAL, FETCH_EMAIL, GENERATE_REPORT]
Events: [SUCCESS, FAILURE, TIMEOUT]

On FETCH_ODOO + SUCCESS → FETCH_SOCIAL
On FETCH_SOCIAL + FAILURE → RETRY_SOCIAL or USE_CACHED_SOCIAL
```

**Pros**:
- Explicit state machine (easy to visualize)
- Well-defined error handling per state
- Can be implemented with workflow engines (Temporal, Step Functions)
- Deterministic behavior

**Cons**:
- **Rigid**: Must predefine all states and transitions (not adaptive)
- **No Reasoning**: Can't make intelligent decisions based on context
- **Complex Setup**: Requires workflow engine infrastructure
- **Limited Flexibility**: Adding new task types requires new state machines

**Why Rejected**: Too rigid for autonomous system. We want the AI to reason about tasks dynamically, not follow predefined state machines. The whole point is autonomous decision-making.

### Alternative C: Agent Swarm (Multiple Specialized Agents)

**Description**: Deploy multiple specialized agents (Financial Agent, Social Agent, Reporting Agent). Coordinator agent delegates subtasks.

**Pros**:
- Specialization (each agent expert in domain)
- Parallel execution (agents work simultaneously)
- Fault isolation (agent failure doesn't affect others)

**Cons**:
- **High Complexity**: Managing multiple agents, coordination protocol
- **High Cost**: Multiple Claude API calls running in parallel
- **Communication Overhead**: Agents must communicate results
- **Difficult Debugging**: Distributed agent behavior hard to trace

**Why Rejected**: Over-engineered for current needs. Ralph Wiggum Loop provides sufficient autonomy with single agent. Can revisit if we need true parallel execution.

## References

- Feature Spec: [specs/gold-tier-autonomous-employee/spec.md](../../specs/gold-tier-autonomous-employee/spec.md) (Section 5: Ralph Wiggum Loop)
- Implementation Plan: TBD (run `/sp.plan`)
- Related ADRs:
  - ADR-001: MCP Server Federation (Ralph Wiggum orchestrates across servers)
  - ADR-003: Weekly CEO Briefing Cadence (primary use case for Ralph Wiggum)
- Evaluator Evidence: [history/prompts/gold-tier-autonomous-employee/001-create-gold-tier-specification.spec.prompt.md](../prompts/gold-tier-autonomous-employee/001-create-gold-tier-specification.spec.prompt.md)
- Pattern Reference: Internal docs on autonomous reasoning patterns
