# ADR-001: MCP Server Federation Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-03-12
- **Feature:** gold-tier-autonomous-employee
- **Context:** The Gold Tier autonomous AI Employee needs to integrate with multiple external systems (Odoo ERP, social media platforms, email servers) and provide reporting capabilities. We need to decide how to structure the integration layer between the AI agent and these external systems.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines entire integration architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Monolithic vs Federation vs Direct
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all external integrations
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement a **federated MCP server architecture** consisting of 4 independent MCP servers:

- **Odoo MCP Server**: Handles all Odoo ERP operations (invoices, financial data, P&L reports)
- **Social MCP Server**: Manages Facebook, Instagram, and Twitter/X integrations
- **Email MCP Server**: Handles email sending and inbox management
- **Reporting MCP Server**: Aggregates data from other servers to generate CEO briefings

Each server:
- Runs as an independent process (Docker container)
- Exposes its own set of MCP tools
- Maintains its own connection pool and state
- Can be deployed, scaled, and restarted independently
- Implements its own error handling and retry logic

The AI agent connects to all 4 servers simultaneously and orchestrates cross-domain operations by calling tools across servers.

## Consequences

### Positive

- **Fault Isolation**: Failure in one domain (e.g., social media API down) doesn't cascade to other domains (Odoo, email still work)
- **Independent Scaling**: Can scale Odoo server independently if financial operations increase without affecting social media server
- **Separation of Concerns**: Each server has clear boundaries and responsibilities, reducing complexity
- **Maintainability**: Domain experts can own and maintain specific servers without understanding entire system
- **Testability**: Each server can be tested in isolation with mocked dependencies
- **Deployment Flexibility**: Can update/restart one server without affecting others (zero-downtime deployments)
- **Security Boundaries**: Can apply different security policies per server (e.g., stricter controls on financial server)
- **Development Velocity**: Teams can work on different servers in parallel without conflicts

### Negative

- **Operational Complexity**: 4 servers to deploy, monitor, and maintain instead of 1
- **Network Overhead**: Cross-domain operations require multiple network calls between agent and servers
- **Distributed State**: No shared state between servers, must coordinate through agent
- **Infrastructure Cost**: 4 containers vs 1 (though minimal with modern container orchestration)
- **Debugging Complexity**: Distributed tracing required to follow requests across servers
- **Configuration Management**: 4 sets of environment variables, API keys, and configurations to manage

## Alternatives Considered

### Alternative A: Monolithic MCP Server

**Description**: Single MCP server handling all integrations (Odoo, social media, email, reporting) in one process.

**Pros**:
- Simpler deployment (1 container)
- Shared state and connection pooling
- Lower network overhead
- Easier debugging (single process)
- Simpler configuration management

**Cons**:
- **Failure Cascade**: Bug in social media integration could crash entire server, taking down Odoo and email
- **Tight Coupling**: Changes to one integration risk breaking others
- **Scaling Limitations**: Can't scale individual domains independently
- **Large Codebase**: Single repository becomes complex and hard to navigate
- **Testing Difficulty**: Integration tests require all external systems to be available

**Why Rejected**: The risk of cascading failures and inability to scale domains independently outweighs the operational simplicity. A bug in social media code shouldn't prevent invoice creation.

### Alternative B: Direct API Integration (No MCP Layer)

**Description**: AI agent calls external APIs directly (Odoo JSON-RPC, Facebook Graph API, etc.) without MCP abstraction layer.

**Pros**:
- No middleware layer (fewer moving parts)
- Direct control over API calls
- Lower latency (no MCP protocol overhead)
- Simpler architecture diagram

**Cons**:
- **No Standardization**: Each API has different authentication, error handling, retry logic
- **Agent Complexity**: Agent must understand 10+ different API contracts
- **No Caching**: Can't implement shared caching layer for expensive operations
- **Difficult Testing**: Must mock each external API individually
- **No Circuit Breaking**: No centralized place to implement circuit breakers and rate limiting
- **Poor Observability**: Distributed tracing and logging harder to implement consistently

**Why Rejected**: The MCP layer provides critical standardization, error handling, and observability that would otherwise need to be reimplemented for each API. The abstraction is worth the overhead.

### Alternative C: Hybrid Approach (2 Servers: Core + Reporting)

**Description**: Split into 2 servers: Core MCP (Odoo + Social + Email) and Reporting MCP.

**Pros**:
- Fewer servers than full federation (2 vs 4)
- Reporting isolated (can be resource-intensive)
- Simpler than full federation

**Cons**:
- **Partial Fault Isolation**: Social media failure still affects Odoo and email
- **Uneven Scaling**: Core server handles 3 domains with different load patterns
- **Unclear Boundaries**: What belongs in "Core" vs "Reporting"?

**Why Rejected**: Doesn't solve the core problem of fault isolation between unrelated domains. If we're going to federate, go all the way.

## References

- Feature Spec: [specs/gold-tier-autonomous-employee/spec.md](../../specs/gold-tier-autonomous-employee/spec.md)
- Implementation Plan: TBD (run `/sp.plan`)
- Related ADRs:
  - ADR-002: Ralph Wiggum Loop Pattern (orchestration across servers)
  - ADR-004: Odoo JSON-RPC Integration (specific to Odoo server)
- Evaluator Evidence: [history/prompts/gold-tier-autonomous-employee/001-create-gold-tier-specification.spec.prompt.md](../prompts/gold-tier-autonomous-employee/001-create-gold-tier-specification.spec.prompt.md)
