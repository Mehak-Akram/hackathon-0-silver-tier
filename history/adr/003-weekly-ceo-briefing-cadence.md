# ADR-003: Weekly CEO Briefing Cadence with Daily Critical Alerts

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-03-12
- **Feature:** gold-tier-autonomous-employee
- **Context:** The Gold Tier AI Employee must provide executive briefings summarizing business operations, financial performance, and marketing metrics. We need to decide the frequency and delivery mechanism for these briefings to balance information completeness with executive attention bandwidth.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines core product value proposition
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Daily vs Weekly vs Real-time
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects reporting, alerting, and user experience
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement a **weekly CEO briefing cadence with daily critical alerts**:

**Weekly Briefing (Every Monday 9:00 AM local time):**
- Comprehensive report covering previous week (Monday-Sunday)
- Sections: Business Summary, Financial Summary, Marketing Performance, Risk Alerts
- Delivered via email with PDF attachment
- Generated automatically by Reporting MCP Server
- Includes week-over-week comparisons and trend analysis
- Estimated length: 2-3 pages

**Daily Critical Alerts (Real-time, as they occur):**
- Triggered only for high/critical severity issues
- Examples: Revenue drop >20%, authentication failures, system downtime >5min
- Delivered via email + Slack (if configured)
- Includes recommended action and escalation path
- Max 3 alerts per day (to prevent alert fatigue)

**Briefing Content Structure:**
```markdown
# CEO Briefing: Week Ending YYYY-MM-DD

## Executive Summary (3 bullet points)
- Key achievement
- Key concern
- Key metric

## Business Operations
- Tasks completed: X
- Tasks in progress: Y
- Blockers: Z

## Financial Performance
- Revenue: $X (±Y% vs last week)
- Expenses: $X (±Y% vs last week)
- Net Profit: $X (±Y% vs last week)
- Top 3 revenue sources
- Top 3 expense categories

## Marketing Performance
- Total Engagement: X (±Y% vs last week)
- Follower Growth: X (±Y% vs last week)
- Top Performing Content (3 posts)
- Platform Breakdown (Facebook, Instagram, Twitter)

## Risk Alerts
- [Severity] [Category] [Description] [Recommended Action]

## Recommendations
- 3 actionable recommendations for next week
```

## Consequences

### Positive

- **Prevents Information Overload**: Weekly cadence gives executives time to digest and act on information
- **Trend Analysis**: Week-over-week data reveals patterns that daily snapshots miss
- **Actionable Insights**: Time to aggregate data allows for deeper analysis and better recommendations
- **Predictable Rhythm**: Executives know when to expect briefing, can schedule review time
- **Critical Issues Not Missed**: Daily alerts ensure urgent matters get immediate attention
- **Reduced Noise**: Only critical alerts interrupt daily workflow
- **Cost Efficient**: 52 briefings/year vs 365 (lower Claude API costs)
- **Aligns with Business Cycles**: Weekly aligns with typical sprint/review cycles

### Negative

- **Delayed Awareness**: Non-critical issues might not be noticed for up to 7 days
- **Stale Data**: By Monday, Sunday's data is already 1 day old
- **Alert Threshold Tuning**: Defining "critical" requires iteration and may miss important issues initially
- **Weekly Variance**: Some weeks have more/less activity (holidays, campaigns) making comparisons noisy
- **No Mid-Week Adjustments**: Can't course-correct until next week's briefing

## Alternatives Considered

### Alternative A: Daily CEO Briefing

**Description**: Generate and send briefing every morning at 9:00 AM with previous day's data.

**Pros**:
- Fresh data (< 24 hours old)
- Faster response to issues
- Daily rhythm matches operational cadence
- Can spot trends earlier

**Cons**:
- **Information Overload**: 365 briefings/year is too much for executives
- **Noisy Data**: Daily variance is high, hard to distinguish signal from noise
- **Incomplete Picture**: Single day doesn't show trends
- **Higher Cost**: 7x more Claude API calls ($350/month vs $50/month)
- **Alert Fatigue**: Executives will start ignoring daily emails

**Why Rejected**: Daily briefings create information overload and don't provide enough context for decision-making. Executives need trends, not daily snapshots.

### Alternative B: Real-Time Dashboard (No Scheduled Briefings)

**Description**: Provide live dashboard with real-time metrics. Executives check when they want.

**Pros**:
- Always up-to-date data
- Self-service (executives control when to check)
- No email clutter
- Can drill down into specific metrics

**Cons**:
- **Requires Active Checking**: Executives must remember to check dashboard
- **No Proactive Alerts**: System doesn't notify of issues
- **No Analysis**: Raw metrics without interpretation or recommendations
- **Context Switching**: Executives must leave workflow to check dashboard
- **No Historical Context**: Harder to see trends without prepared reports

**Why Rejected**: Passive dashboard doesn't provide proactive value. The AI Employee should surface insights, not wait to be queried.

### Alternative C: Bi-Weekly Briefing

**Description**: Send briefing every 2 weeks (26 briefings/year).

**Pros**:
- Even less frequent than weekly (less noise)
- Lower cost (26 briefings vs 52)
- More time for trend analysis

**Cons**:
- **Too Infrequent**: 2 weeks is too long to wait for business insights
- **Delayed Action**: Issues might compound before being noticed
- **Misses Weekly Cycles**: Many businesses operate on weekly cycles (sales, marketing)

**Why Rejected**: 2 weeks is too long for actionable business intelligence. Weekly strikes the right balance.

### Alternative D: Weekly Briefing + Daily Digest (All Issues)

**Description**: Weekly comprehensive briefing + daily email with all issues (not just critical).

**Pros**:
- Daily awareness of all issues
- Weekly deep dive for trends

**Cons**:
- **Alert Fatigue**: Daily emails with non-critical issues will be ignored
- **Redundancy**: Issues appear in both daily digest and weekly briefing
- **Higher Cost**: Daily generation + weekly briefing

**Why Rejected**: Daily digest of non-critical issues creates noise. Better to only alert on critical issues and save everything else for weekly briefing.

## References

- Feature Spec: [specs/gold-tier-autonomous-employee/spec.md](../../specs/gold-tier-autonomous-employee/spec.md) (Section 6: Weekly CEO Briefing)
- Implementation Plan: TBD (run `/sp.plan`)
- Related ADRs:
  - ADR-001: MCP Server Federation (Reporting MCP generates briefings)
  - ADR-002: Ralph Wiggum Loop (Used to orchestrate briefing generation)
- Evaluator Evidence: [history/prompts/gold-tier-autonomous-employee/001-create-gold-tier-specification.spec.prompt.md](../prompts/gold-tier-autonomous-employee/001-create-gold-tier-specification.spec.prompt.md)
- Research: Executive attention studies, information overload research
