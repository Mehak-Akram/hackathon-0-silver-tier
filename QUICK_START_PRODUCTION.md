# Quick Start Guide - Production Deployment

**System:** Gold Tier Autonomous Employee  
**Version:** 1.0  
**Status:** Development/Testing ⚠️

> **⚠️ Important**: This system is in active development. The "production ready" claims in this document reflect the intended deployment state, not necessarily current verified production usage. Test thoroughly in your environment before relying on it for critical operations.

---

## 🚀 5-Minute Quick Start

### Step 1: Verify Configuration (1 minute)

Your system is already configured with:
- ✅ Odoo CRM credentials
- ✅ Gmail email (IMAP + SMTP)
- ✅ Facebook social media monitoring
- ✅ Alert system enabled
- ✅ CEO briefing enabled (Monday 8 AM)

**No additional configuration needed!**

### Step 2: Run Tests (2 minutes)

```bash
# Test all components
test_production_setup.bat
```

Expected output: All tests pass ✓

### Step 3: Start the System (1 minute)

```bash
# Start in development mode (recommended for first run)
start_autonomous_loop.bat
```

You should see:
```
============================================================
AUTONOMOUS LOOP STARTED (Ralph Wiggum Mode)
============================================================
Interval: 60 seconds
Monitoring: Inbox/ and Needs_Action/
Press Ctrl+C to stop gracefully
============================================================
```

### Step 4: Open Dashboard (30 seconds)

Open your browser: **http://localhost:8080/**

You'll see:
- System status (healthy/degraded/unhealthy)
- Tasks processed
- Uptime
- CPU and memory usage
- Real-time metrics

### Step 5: Send Test Email (30 seconds)

Send an email to your configured monitoring address (set in .env as EMAIL_ADDRESS)

Subject: `Product Information Request`  
Body: `Hi, I'm interested in your products. Can you provide more information?`

Wait 60 seconds, then check:
1. ✅ Task created in Inbox/ folder
2. ✅ Customer created in Odoo
3. ✅ Lead created in Odoo
4. ✅ Auto-response sent to your email
5. ✅ Task moved to Done/ folder

---

## 📊 What Happens Automatically

### Every 60 Seconds
- Checks for new emails
- Checks for social media mentions (Facebook)
- Processes tasks in Inbox/
- Executes tasks in Needs_Action/
- Updates health dashboard
- Logs all activity

### Every Monday at 8:00 AM
- Generates weekly CEO briefing
- Aggregates metrics from past 7 days
- Sends HTML email report to configured recipients (see .env)

### When Issues Occur
- Sends email alerts to configured admin email (see .env)
- Logs errors in Audit_Logs/
- Retries failed operations
- Escalates critical issues

---

## 🎯 Key Features Working

> **⚠️ Note**: The features listed below have been implemented and tested in development. Actual production performance may vary based on your configuration and environment.

### 1. Email Auto-Response ✅
- Monitors: Configured email address (see .env)
- Creates tasks from incoming emails
- Sends intelligent auto-responses
- Creates customers and leads in Odoo

### 2. Odoo CRM Integration ✅
- Creates customers automatically
- Creates leads from inquiries
- Tracks all interactions
- Web interface: http://localhost:8069

### 3. Social Media Monitoring ✅
- Facebook: Active
- Twitter: Not configured (optional)
- Instagram: Not configured (optional)

### 4. Health Monitoring ✅
- Dashboard: http://localhost:8080/
- Real-time metrics
- System health status
- Auto-refresh every 10 seconds

### 5. Alert System ✅
- Email alerts for errors
- CPU/memory warnings
- System health notifications
- Sent to: Configured admin email

### 6. CEO Briefing ✅
- Weekly reports (Monday 8 AM)
- Metrics aggregation
- HTML and text formats
- Sent to: Configured recipients

---

## 📁 Important Folders

```
E:\AI_Employee_Vault\
├── Inbox/              ← New tasks appear here
├── Needs_Action/       ← Tasks waiting for execution
├── Done/               ← Completed tasks
├── Pending_Approval/   ← High-risk tasks requiring approval
├── Audit_Logs/         ← All system activity logs
├── Briefings/          ← CEO briefing reports
└── service_logs/       ← Windows service logs (if installed)
```

---

## 🔧 Common Operations

### View System Status
```bash
# Open dashboard
start http://localhost:8080/
```

### Stop the System
```bash
# Press Ctrl+C in the console window
# Or use kill switch:
echo "Emergency stop" > STOP
```

### Restart the System
```bash
# Stop (Ctrl+C), then:
start_autonomous_loop.bat
```

### Generate CEO Briefing Manually
```bash
python reporting/ceo_briefing_cli.py generate
```

### View Audit Logs
```bash
# Open latest log file
notepad Audit_Logs\audit_log_20260410.json
```

### Check Odoo CRM
```bash
# Open in browser
start http://localhost:8069
# Login: your-configured-username / your-password
```

---

## 🚨 Emergency Procedures

### System Not Responding
1. Check if process is running
2. Check Audit_Logs/ for errors
3. Restart: `start_autonomous_loop.bat`

### Too Many Errors
1. Activate kill switch: `echo "Stop" > STOP`
2. Review audit logs
3. Fix configuration in .env
4. Remove kill switch: `del STOP`
5. Restart system

### Email Not Working
1. Verify Gmail App Password is correct
2. Check .env file: EMAIL_PASSWORD
3. Test manually: `python orchestrator/email_monitor.py`

### Odoo Not Working
1. Check if Odoo is running: http://localhost:8069
2. Verify credentials in .env
3. Test connection: `python debug_odoo_client.py`

---

## 📈 Monitoring Checklist

### Daily (5 minutes)
- [ ] Check dashboard: http://localhost:8080/
- [ ] Review error count (should be 0 or low)
- [ ] Check email for alerts
- [ ] Verify tasks are being processed

### Weekly (10 minutes)
- [ ] Review Monday CEO briefing email
- [ ] Check Odoo for new customers/leads
- [ ] Review Done/ folder for completed tasks
- [ ] Check system uptime

### Monthly (30 minutes)
- [ ] Review audit logs for patterns
- [ ] Check disk space (Audit_Logs/ folder)
- [ ] Verify email auto-responses are appropriate
- [ ] Review Odoo data quality

---

## 🎓 Advanced: Install as Windows Service

For 24/7 production operation:

### Prerequisites
1. Download NSSM: https://nssm.cc/download
2. Extract to: `E:\AI_Employee_Vault\tools\nssm.exe`

### Installation
```bash
# Run as Administrator
install_service.bat
```

### Service Management
```bash
# Start service
net start GoldTierEmployee

# Stop service
net stop GoldTierEmployee

# Check status
sc query GoldTierEmployee

# View logs
type service_logs\service_stdout.log
```

### Benefits
- ✅ Auto-starts on system boot
- ✅ Auto-restarts on failure
- ✅ Runs in background
- ✅ Production-grade reliability

---

## 📞 Support

### Documentation
- Full audit report: `GOLD_TIER_AUDIT_REPORT.md`
- Fixes applied: `FIXES_APPLIED.md`
- Production checklist: `PRODUCTION_DEPLOYMENT_CHECKLIST.md`

### Logs
- Audit logs: `Audit_Logs/`
- Service logs: `service_logs/`
- Health dashboard: http://localhost:8080/

### Configuration
- Main config: `.env`
- Odoo config: `odoo-config/`

---

## ✅ System Status

**Status:** OPERATIONAL ✅  
**Uptime Target:** 99%  
**Error Rate Target:** <5%  
**Response Time:** <5 minutes  

**Your system is ready for production use!**

---

**Last Updated:** 2026-04-10  
**Version:** 1.0  
**Support:** Check audit logs and documentation
