# Quickstart Guide: Gold Tier Autonomous AI Employee

**Feature**: Gold Tier Autonomous AI Employee
**Date**: 2026-03-12
**Audience**: Developers setting up and running the system

## Overview

This guide walks you through setting up the Gold Tier autonomous AI employee system from scratch, including all dependencies, MCP servers, and the autonomous reasoning loop.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Git**: For version control
- **Odoo Community**: Self-hosted instance (Docker or native)
- **Social Media Accounts**: Facebook Page, Instagram Business, Twitter/X with API access
- **Email Account**: SMTP-enabled email account for sending briefings

---

## 1. Environment Setup

### Clone Repository

```bash
cd E:\AI_Employee_Vault
git checkout 1-gold-tier-autonomous-employee
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `mcp-sdk` - Model Context Protocol SDK
- `asyncio` - Async I/O for concurrent operations
- `pydantic` - Data validation
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variable management
- `structlog` - Structured logging
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support

### Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=your_odoo_password

# Facebook Configuration
FB_ACCESS_TOKEN=your_facebook_access_token
FB_PAGE_ID=your_facebook_page_id

# Instagram Configuration
IG_ACCESS_TOKEN=your_instagram_access_token
IG_ACCOUNT_ID=your_instagram_business_account_id

# Twitter Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password
CEO_EMAIL=ceo@yourcompany.com

# Risk Engine Configuration
RISK_HIGH_THRESHOLD=0.7
RISK_MEDIUM_THRESHOLD=0.4
MAX_RETRIES=3
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=300

# Autonomous Loop Configuration
ENABLE_AUTONOMOUS_LOOP=false  # Set to true after testing
LOOP_INTERVAL_SECONDS=60
CEO_BRIEFING_DAY=monday
CEO_BRIEFING_HOUR=8
```

---

## 2. Odoo Setup

### Option A: Docker (Recommended)

```bash
# Pull Odoo Community image
docker pull odoo:19

# Run Odoo with PostgreSQL
docker run -d \
  --name odoo \
  -p 8069:8069 \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  odoo:19
```

### Option B: Native Installation

Follow official Odoo installation guide: https://www.odoo.com/documentation/19.0/administration/install.html

### Configure Odoo

1. Access Odoo at http://localhost:8069
2. Create a new database (name it `odoo_db` to match .env)
3. Install the **Accounting** module
4. Create test data:
   - Add a customer (Contacts → Create)
   - Add a product (Sales → Products → Create)
   - Create a chart of accounts (if not auto-created)

### Test Odoo JSON-RPC Connection

```bash
python -c "
import xmlrpc.client
url = 'http://localhost:8069'
db = 'odoo_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f'Authenticated with UID: {uid}')
"
```

---

## 3. Social Media API Setup

### Facebook & Instagram

1. Go to https://developers.facebook.com/
2. Create a new app (Business type)
3. Add **Facebook Login** and **Instagram Graph API** products
4. Generate a **Page Access Token** with permissions:
   - `pages_read_engagement`
   - `pages_show_list`
   - `instagram_basic`
   - `instagram_manage_insights`
5. Copy the access token to `.env` as `FB_ACCESS_TOKEN` and `IG_ACCESS_TOKEN`

**Note**: Tokens expire. Implement token refresh or use long-lived tokens.

### Twitter/X

1. Go to https://developer.twitter.com/
2. Create a new project and app
3. Generate API keys and access tokens with **Read** permissions
4. Copy credentials to `.env`:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`

---

## 4. MCP Server Configuration

MCP server configurations are stored in `mcp_server/` directory.

### Odoo MCP Config

Edit `mcp_server/odoo_config.yaml`:

```yaml
server_type: odoo
host: http://localhost:8069
database: odoo_db
timeout: 30
retry_attempts: 3
circuit_breaker:
  threshold: 5
  timeout: 300
```

### Social MCP Config

Edit `mcp_server/social_config.yaml`:

```yaml
server_type: social
platforms:
  facebook:
    enabled: true
    rate_limit: 200  # requests per hour
  instagram:
    enabled: true
    rate_limit: 200
  twitter:
    enabled: true
    rate_limit: 300  # requests per 15 minutes
timeout: 30
retry_attempts: 3
```

### Email MCP Config

Edit `mcp_server/email_config.yaml`:

```yaml
server_type: email
smtp:
  use_tls: true
  timeout: 30
templates:
  ceo_briefing: src/templates/ceo_briefing_email.html.j2
```

### Reporting MCP Config

Edit `mcp_server/reporting_config.yaml`:

```yaml
server_type: reporting
templates:
  ceo_briefing: src/templates/ceo_briefing.md.j2
output_directory: Reports/CEO_Briefings/
```

---

## 5. Running the System

### Start MCP Servers (if separate processes)

```bash
# Start Odoo MCP server
python src/mcp_servers/odoo_mcp.py &

# Start Social MCP server
python src/mcp_servers/social_mcp.py &

# Start Email MCP server
python src/mcp_servers/email_mcp.py &

# Start Reporting MCP server
python src/mcp_servers/reporting_mcp.py &
```

**Note**: MCP servers may be embedded in the main application depending on implementation.

### Run Tests

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests
pytest tests/contract/                # Contract tests

# Run with coverage
pytest --cov=src --cov-report=html
```

### Start Autonomous Loop (Manual Mode)

For initial testing, run with autonomous loop **disabled**:

```bash
# In .env, ensure: ENABLE_AUTONOMOUS_LOOP=false
python src/main.py
```

This starts the system in manual mode where you can trigger operations manually.

### Trigger CEO Briefing Manually

```bash
# Create a task file in Inbox
cat > Inbox/generate-briefing.md <<EOF
---
domain: business
priority: 1
---

Generate CEO briefing for last week
EOF

# The task scanner will detect it and process
```

### Enable Autonomous Loop (Production Mode)

After testing, enable autonomous operation:

1. Edit `.env`: Set `ENABLE_AUTONOMOUS_LOOP=true`
2. Restart the system: `python src/main.py`
3. The autonomous loop will now:
   - Monitor folders continuously
   - Generate CEO briefings every Monday at 8 AM
   - Execute tasks automatically based on risk classification
   - Retry failed operations
   - Escalate high-risk actions to `/Pending_Approval`

---

## 6. Using the Kill Switch

To immediately halt the autonomous loop:

```bash
# Create the kill switch file
touch /STOP

# Or on Windows
type nul > STOP
```

The autonomous loop checks for this file before each action and will gracefully shut down if detected.

To re-enable:

```bash
# Remove the kill switch file
rm /STOP

# Restart the system
python src/main.py
```

---

## 7. Testing the System

### Test 1: CEO Briefing Generation

```bash
# Trigger briefing manually
python -c "
from src.skills.reporting_skills import generate_ceo_briefing
from datetime import date, timedelta

# Generate briefing for last week
today = date.today()
week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
week_end = week_start + timedelta(days=6)  # Last Sunday

briefing = generate_ceo_briefing(week_start, week_end)
print(f'Briefing generated: {briefing.file_path}')
"
```

**Expected Result**: Briefing file created in `Reports/CEO_Briefings/YYYY-MM-DD-briefing.md`

### Test 2: Invoice Creation (with Approval)

```bash
# Create invoice task
cat > Inbox/create-invoice.md <<EOF
---
domain: accounting
priority: 1
---

Create invoice for Customer ABC
- Product: Consulting Services
- Quantity: 10 hours
- Unit Price: $150
EOF
```

**Expected Result**:
1. Task moves to `/Pending_Approval` (high-risk operation)
2. Review the invoice details
3. Move to `/Approved` to execute
4. Invoice created in Odoo
5. Task moves to `/Done` with execution summary

### Test 3: Social Media Metrics Collection

```bash
# Create social metrics task
cat > Inbox/social-metrics.md <<EOF
---
domain: marketing
priority: 2
---

Fetch social media metrics for last week
EOF
```

**Expected Result**:
1. Task auto-executes (low-risk operation)
2. Metrics fetched from Facebook, Instagram, Twitter
3. Summary generated
4. Task moves to `/Done`

### Test 4: Multi-Step Task with Ralph Wiggum Loop

```bash
# Create complex task
cat > Inbox/quarterly-report.md <<EOF
---
domain: business
priority: 1
---

Generate Q1 financial report and email to board members
EOF
```

**Expected Result**:
1. Ralph Wiggum Loop decomposes task into steps:
   - Fetch Q1 financial data from Odoo
   - Generate P&L summary
   - Format report
   - Send email via Email MCP
2. Each step executes in sequence
3. If a step fails, retry with exponential backoff
4. Task completes or escalates if max retries exceeded

### Test 5: Error Recovery and Circuit Breaker

```bash
# Simulate Odoo downtime
docker stop odoo

# Create invoice task (will fail)
cat > Inbox/test-invoice.md <<EOF
---
domain: accounting
priority: 1
---

Create test invoice
EOF
```

**Expected Result**:
1. Odoo MCP call fails
2. Retry logic attempts 3 times
3. Circuit breaker opens after 5 consecutive failures
4. Subsequent requests fail fast
5. Error logged to `Audit_Logs/`
6. High-severity alert sent via email

```bash
# Restart Odoo
docker start odoo

# Circuit breaker will attempt half-open after timeout (5 min)
# Or manually reset by restarting the system
```

---

## 8. Monitoring and Logs

### Audit Logs

All actions are logged to `Audit_Logs/` in JSON Lines format:

```bash
# View recent audit logs
tail -f Audit_Logs/$(date +%Y-%m-%d)-audit.jsonl

# Query logs by risk level
grep '"risk_level":"high"' Audit_Logs/*.jsonl

# Count actions by type
jq -r '.action_type' Audit_Logs/*.jsonl | sort | uniq -c
```

### System Health Check

```bash
# Check MCP server status
curl http://localhost:8072/reporting/data-sources/status

# Check circuit breaker states
python -c "
from src.circuit_breaker import get_all_circuit_states
states = get_all_circuit_states()
for server, state in states.items():
    print(f'{server}: {state}')
"
```

### CEO Briefing History

```bash
# List all generated briefings
ls -lh Reports/CEO_Briefings/

# View latest briefing
cat Reports/CEO_Briefings/$(ls -t Reports/CEO_Briefings/ | head -1)
```

---

## 9. Troubleshooting

### Issue: Odoo Authentication Fails

**Symptoms**: `401 Unauthorized` errors in logs

**Solution**:
1. Verify credentials in `.env`
2. Test connection manually (see section 2)
3. Check Odoo is running: `curl http://localhost:8069`

### Issue: Social Media API Rate Limit

**Symptoms**: `429 Too Many Requests` errors

**Solution**:
1. Check rate limit headers in logs
2. Adjust `LOOP_INTERVAL_SECONDS` in `.env` to reduce frequency
3. Implement token rotation if multiple tokens available

### Issue: CEO Briefing Missing Data

**Symptoms**: Briefing shows "Data unavailable" for some sections

**Solution**:
1. Check MCP server status: `curl http://localhost:8072/reporting/data-sources/status`
2. Review circuit breaker states
3. Check audit logs for errors during data collection
4. Verify API credentials are valid

### Issue: Autonomous Loop Not Running

**Symptoms**: Tasks stay in `/Inbox`, no automatic processing

**Solution**:
1. Check `.env`: Ensure `ENABLE_AUTONOMOUS_LOOP=true`
2. Check for kill switch: `ls /STOP` (should not exist)
3. Review logs for startup errors
4. Verify Python process is running: `ps aux | grep main.py`

### Issue: High Memory Usage

**Symptoms**: System slows down over time

**Solution**:
1. Check audit log size: `du -sh Audit_Logs/`
2. Implement log rotation (keep last 90 days)
3. Review concurrent task limit in `main.py`
4. Monitor MCP connection pooling

---

## 10. Development Workflow

### Adding a New Skill

1. Create skill file in `src/skills/`:

```python
# src/skills/my_new_skill.py
from src.skills.base_skill import BaseSkill

class MyNewSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="my_new_skill",
            risk_level="medium",
            requires_approval=False
        )

    async def execute(self, params):
        # Skill logic here
        self.log_action("Executing my new skill")
        result = await self.do_something(params)
        return result
```

2. Register skill in `src/skills/__init__.py`
3. Add tests in `tests/unit/test_my_new_skill.py`
4. Update documentation

### Running in Development Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with auto-reload
python -m watchdog src/ -p '*.py' -c 'python src/main.py'
```

### Creating a New MCP Server

1. Define contract in `specs/1-gold-tier-autonomous-employee/contracts/`
2. Implement server in `src/mcp_servers/`
3. Add configuration in `mcp_server/`
4. Add contract tests in `tests/contract/`
5. Update `data-model.md` if new entities are introduced

---

## 11. Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/ai-employee.service`:

```ini
[Unit]
Description=Gold Tier Autonomous AI Employee
After=network.target

[Service]
Type=simple
User=aiemployee
WorkingDirectory=/opt/ai-employee
Environment="PATH=/opt/ai-employee/venv/bin"
ExecStart=/opt/ai-employee/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
sudo systemctl status ai-employee
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY mcp_server/ ./mcp_server/
COPY .env .

CMD ["python", "src/main.py"]
```

Build and run:

```bash
docker build -t ai-employee:latest .
docker run -d --name ai-employee \
  -v $(pwd)/Audit_Logs:/app/Audit_Logs \
  -v $(pwd)/Reports:/app/Reports \
  ai-employee:latest
```

---

## 12. Security Considerations

- **Credentials**: Never commit `.env` to version control
- **API Tokens**: Rotate tokens regularly
- **Audit Logs**: Protect with appropriate file permissions (600)
- **Kill Switch**: Ensure `/STOP` file is accessible to operators
- **Approval Workflow**: Review high-risk actions before approving
- **Network**: Run MCP servers on localhost or secure network
- **Backups**: Backup audit logs and CEO briefings regularly

---

## 13. Next Steps

After completing this quickstart:

1. Review generated CEO briefing for accuracy
2. Test invoice creation workflow with real Odoo data
3. Configure social media API credentials
4. Set up email delivery for CEO briefings
5. Enable autonomous loop in production
6. Monitor audit logs for errors
7. Implement log rotation and archival
8. Set up monitoring dashboard (optional)
9. Train team on approval workflow
10. Document custom skills and workflows

---

## Support

- **Documentation**: See `specs/1-gold-tier-autonomous-employee/`
- **Issues**: Check audit logs first, then review troubleshooting section
- **Constitution**: Review `.specify/memory/constitution.md` for system constraints
- **ADRs**: See `history/adr/` for architectural decisions

---

**Last Updated**: 2026-03-12
