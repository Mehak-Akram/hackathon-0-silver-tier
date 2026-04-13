# CEO Briefing System Guide

Automated weekly executive reports for business intelligence and system monitoring.

> **⚠️ Data Accuracy Note**: The CEO Briefing System aggregates data from audit logs, task files, and Odoo. The accuracy of metrics depends on the completeness and correctness of data in these sources. Verify metrics against source systems for critical business decisions.

---

## Overview

The CEO Briefing System automatically generates comprehensive weekly reports that include:
- Task processing statistics
- Customer and lead metrics from Odoo
- Email and social media engagement
- System health and performance
- Week-over-week comparisons
- Highlights and notable events

Reports are generated in HTML, text, and JSON formats and can be automatically emailed to executives.

---

## Features

### Automated Metrics Collection
- Aggregates data from audit logs, Odoo CRM, and task files
- Tracks system performance and uptime
- Monitors email and social media activity
- Identifies errors and issues

### Professional Reports
- **HTML Report** - Beautiful, responsive web format with charts and tables
- **Text Report** - Plain text for email clients
- **JSON Data** - Raw data for further analysis

### Week-over-Week Comparison
- Compares current week to previous week
- Shows percentage changes for key metrics
- Highlights significant improvements or concerns

### Flexible Delivery
- Manual generation via CLI
- Automated weekly email delivery
- Scheduled execution (every Monday at 9 AM)

---

## Quick Start

### 1. Generate Your First Briefing

```bash
# Generate briefing for current week
python reporting/ceo_briefing_cli.py generate

# Open in browser
python reporting/ceo_briefing_cli.py generate --open
```

Briefings are saved to: `Briefings/ceo_briefing_YYYYMMDD.html`

### 2. View Current Metrics

```bash
# Show metrics for last 7 days
python reporting/ceo_briefing_cli.py metrics

# Show metrics for last 30 days
python reporting/ceo_briefing_cli.py metrics --days 30
```

### 3. Configure Email Delivery

Edit `.env`:
```bash
CEO_BRIEFING_EMAIL_ENABLED=true
CEO_BRIEFING_RECIPIENTS=ceo@example.com,cfo@example.com
```

Send briefing:
```bash
python reporting/ceo_briefing_cli.py send
```

### 4. Schedule Automatic Delivery

Run as Administrator:
```bash
schedule_ceo_briefing.bat
```

This creates a Windows scheduled task that runs every Monday at 9:00 AM.

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Enable email delivery
CEO_BRIEFING_EMAIL_ENABLED=true

# Email recipients (comma-separated)
CEO_BRIEFING_RECIPIENTS=ceo@example.com,cfo@example.com,board@example.com

# Email credentials (same as system email)
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

---

## CLI Commands

### Generate Briefing

```bash
# Current week
python reporting/ceo_briefing_cli.py generate

# Specific date (end of period)
python reporting/ceo_briefing_cli.py generate --date 2026-04-08

# Generate and open in browser
python reporting/ceo_briefing_cli.py generate --open
```

### Send Briefing

```bash
# Generate and email current week
python reporting/ceo_briefing_cli.py send

# Send for specific date
python reporting/ceo_briefing_cli.py send --date 2026-04-08
```

### View Metrics

```bash
# Last 7 days
python reporting/ceo_briefing_cli.py metrics

# Last 30 days
python reporting/ceo_briefing_cli.py metrics --days 30

# Last 90 days
python reporting/ceo_briefing_cli.py metrics --days 90
```

### List Briefings

```bash
# Show all generated briefings
python reporting/ceo_briefing_cli.py list
```

---

## Report Contents

### Executive Summary
High-level overview of the week's activities and key metrics.

### Key Performance Indicators
- **Tasks Executed** - Total tasks completed
- **New Customers** - Customers created in Odoo
- **New Leads** - Sales opportunities created
- **System Uptime** - Hours of operation

All KPIs include week-over-week comparison with percentage change.

### Email Operations
- Emails received and processed
- Auto-responses sent
- Response rate percentage

### Social Media Engagement
- Mentions detected across platforms
- Leads generated from social media
- Breakdown by platform (Facebook, Twitter, Instagram)

### System Health
- Total iterations completed
- Errors and warnings
- Critical issues
- System performance metrics

### Highlights & Notable Events
Automatically generated insights:
- Significant improvements (>20% increase)
- Areas of concern (error rate increases)
- Perfect performance achievements
- Critical issues requiring attention

---

## Scheduling

### Windows Scheduled Task

**Install:**
```bash
# Run as Administrator
schedule_ceo_briefing.bat
```

**Default Schedule:**
- Every Monday at 9:00 AM
- Runs as SYSTEM user
- Logs to audit logs

**Manage Task:**
```bash
# View task details
schtasks /query /tn GoldTierCEOBriefing

# Run immediately
schtasks /run /tn GoldTierCEOBriefing

# Delete task
schtasks /delete /tn GoldTierCEOBriefing /f
```

### Custom Schedule

To change the schedule, edit the task:
```bash
# Change to Friday at 5 PM
schtasks /change /tn GoldTierCEOBriefing /st 17:00 /d FRI
```

---

## Report Formats

### HTML Report

Professional web-based report with:
- Responsive design
- Color-coded metrics
- Interactive tables
- Week-over-week indicators (▲ ▼)
- Highlights section
- Auto-refresh capability

**Location:** `Briefings/ceo_briefing_YYYYMMDD.html`

### Text Report

Plain text version for:
- Email body
- Terminal viewing
- Archival purposes

**Location:** `Briefings/ceo_briefing_YYYYMMDD.txt`

### JSON Data

Raw metrics data for:
- Custom analysis
- Integration with BI tools
- Programmatic access

**Location:** `Briefings/ceo_briefing_YYYYMMDD.json`

---

## Metrics Explained

### System Metrics
- **Total Iterations** - Number of autonomous loop cycles
- **Uptime Hours** - Estimated operational time
- **Average Iteration Time** - Performance indicator

### Task Metrics
- **Total Processed** - Tasks classified and routed
- **Total Executed** - Tasks successfully completed
- **Success Rate** - Percentage of successful executions
- **By Type** - Breakdown by task category

### Odoo Metrics
- **Customers Created** - New contacts added to CRM
- **Leads Created** - New sales opportunities
- **Opportunities Value** - Total pipeline value (if available)

### Email Metrics
- **Emails Received** - Incoming emails processed
- **Auto-Responses Sent** - Automated replies sent
- **Response Rate** - Percentage of emails responded to

### Social Media Metrics
- **Mentions Detected** - Social media interactions found
- **By Platform** - Breakdown by Facebook/Twitter/Instagram
- **Leads Generated** - Opportunities from social mentions

### Error Metrics
- **Total Errors** - All error events
- **Critical Errors** - Severe issues requiring immediate attention
- **Warnings** - Non-critical issues
- **By Type** - Categorized error breakdown

---

## Customization

### Custom Metrics

Add custom metrics by editing `reporting/metrics_aggregator.py`:

```python
def _get_custom_metrics(self, start_date, end_date):
    """Add your custom metrics here"""
    metrics = {
        'custom_metric': 0
    }
    # Your logic here
    return metrics
```

### Custom Report Sections

Modify report templates in `reporting/ceo_briefing_generator.py`:

```python
def _generate_custom_section(self, metrics):
    """Add custom report section"""
    html = '<h2>Custom Section</h2>'
    # Your HTML here
    return html
```

### Custom Email Template

Edit email formatting in `reporting/ceo_briefing_email_sender.py`.

---

## Troubleshooting

### No Data in Report

**Issue:** Report shows zeros for all metrics

**Solutions:**
1. Ensure autonomous loop has been running
2. Check that tasks have been processed (check `Done/` folder)
3. Verify audit logs exist in `Audit_Logs/`
4. Run system for at least a few hours to generate data

### Email Not Sending

**Issue:** Briefing generates but email fails

**Solutions:**
1. Check `CEO_BRIEFING_EMAIL_ENABLED=true` in .env
2. Verify `CEO_BRIEFING_RECIPIENTS` is set
3. Confirm email credentials are correct
4. Test with: `python reporting/ceo_briefing_cli.py send`
5. Check audit logs for error details

### Scheduled Task Not Running

**Issue:** Briefing not generated on Monday

**Solutions:**
1. Verify task exists: `schtasks /query /tn GoldTierCEOBriefing`
2. Check task is enabled
3. Run manually: `schtasks /run /tn GoldTierCEOBriefing`
4. Check Windows Event Viewer for task scheduler errors
5. Verify Python path is correct in task

### Incorrect Metrics

**Issue:** Metrics don't match expected values

**Solutions:**
1. Check date range - briefing covers 7 days ending on generation date
2. Verify audit log format hasn't changed
3. Ensure task files are in correct format
4. Check Odoo connection is working
5. Review `Briefings/*.json` for raw data

---

## Best Practices

### Regular Review
- Review briefings weekly with leadership team
- Track trends over multiple weeks
- Set goals based on metrics

### Data Quality
- Ensure autonomous loop runs consistently
- Monitor for gaps in data collection
- Validate metrics against other sources

### Distribution
- Send to relevant stakeholders only
- Consider different reports for different audiences
- Archive briefings for historical analysis

### Action Items
- Use highlights section to identify priorities
- Address critical errors immediately
- Celebrate improvements with team

---

## Integration

### Business Intelligence Tools

Export JSON data to:
- Power BI
- Tableau
- Google Data Studio
- Excel

### Slack/Teams Integration

Add webhook to send briefing notifications:
```python
# In ceo_briefing_email_sender.py
def send_slack_notification(briefing):
    # Your Slack webhook code
    pass
```

### Dashboard Integration

Embed metrics in existing dashboards using JSON API.

---

## Examples

### Weekly Executive Meeting

Generate briefing before Monday meeting:
```bash
python reporting/ceo_briefing_cli.py generate --open
```

### Monthly Board Report

Generate 30-day metrics:
```bash
python reporting/ceo_briefing_cli.py metrics --days 30 > monthly_report.txt
```

### Quarterly Review

Generate briefings for each week of quarter and compare trends.

---

## Files and Directories

```
reporting/
├── metrics_aggregator.py          # Data collection
├── ceo_briefing_generator.py      # Report generation
├── ceo_briefing_email_sender.py   # Email delivery
├── scheduled_briefing.py          # Automated execution
└── ceo_briefing_cli.py            # Command-line interface

Briefings/
├── ceo_briefing_20260409.html     # HTML report
├── ceo_briefing_20260409.txt      # Text report
└── ceo_briefing_20260409.json     # JSON data

schedule_ceo_briefing.bat          # Windows scheduler setup
```

---

## Support

### Logs

Check audit logs for briefing generation:
```bash
type Audit_Logs\audit_log_YYYYMMDD.json | findstr ceo_briefing
```

### Manual Execution

Test briefing generation:
```bash
python reporting/scheduled_briefing.py
```

### Debugging

Enable verbose output:
```python
# In metrics_aggregator.py
print(f"Debug: Found {len(events)} events")
```

---

## Roadmap

Future enhancements:
- [ ] PDF export
- [ ] Custom date ranges
- [ ] Comparative analysis (multiple weeks)
- [ ] Predictive analytics
- [ ] Mobile-friendly reports
- [ ] Real-time dashboard
- [ ] Multi-language support

---

## Summary

The CEO Briefing System provides automated, comprehensive weekly reports that give executives visibility into:
- Business operations (customers, leads, tasks)
- System performance and health
- Email and social media engagement
- Trends and changes over time

**Get Started:**
```bash
python reporting/ceo_briefing_cli.py generate --open
```

**Schedule Weekly Delivery:**
```bash
schedule_ceo_briefing.bat
```

**Configure Recipients:**
```bash
# In .env
CEO_BRIEFING_EMAIL_ENABLED=true
CEO_BRIEFING_RECIPIENTS=ceo@example.com
```

For questions or issues, check the audit logs or run commands with verbose output.
