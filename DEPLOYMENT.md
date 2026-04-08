# Production Deployment Guide

Complete guide for deploying Gold Tier Autonomous Employee as a production Windows service.

---

## Overview

This guide covers:
- Windows service installation
- Health monitoring and alerting
- Log rotation and management
- Production configuration
- Troubleshooting

---

## Prerequisites

### System Requirements
- Windows 10/11 or Windows Server 2016+
- Python 3.8 or higher
- Administrator privileges
- 4GB RAM minimum (8GB recommended)
- 10GB disk space

### Software Requirements
- Docker Desktop (for Odoo)
- NSSM (Non-Sucking Service Manager)
- Git (optional, for updates)

---

## Step 1: Download NSSM

NSSM is required to run the autonomous loop as a Windows service.

1. Download NSSM from: https://nssm.cc/download
2. Extract the archive
3. Copy `nssm.exe` (64-bit version) to: `E:\AI_Employee_Vault\tools\nssm.exe`

**Directory structure:**
```
E:\AI_Employee_Vault\
├── tools\
│   └── nssm.exe          <- Place NSSM here
├── deployment\
│   ├── service_manager.py
│   ├── health_monitor.py
│   └── alert_manager.py
└── install_service.bat
```

---

## Step 2: Configure Environment

Edit `.env` file with production settings:

```bash
# ============================================================
# CORE SETTINGS
# ============================================================
ENABLE_AUTONOMOUS_LOOP=true
LOOP_INTERVAL_SECONDS=60

# ============================================================
# ODOO CONFIGURATION
# ============================================================
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your-secure-password

# ============================================================
# EMAIL CONFIGURATION (Optional)
# ============================================================
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
EMAIL_FROM_NAME=AI Employee

# ============================================================
# SOCIAL MEDIA MONITORING (Optional)
# ============================================================
FACEBOOK_MONITORING_ENABLED=false
FACEBOOK_PAGE_ID=
FACEBOOK_ACCESS_TOKEN=

TWITTER_MONITORING_ENABLED=false
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

INSTAGRAM_MONITORING_ENABLED=false
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# ============================================================
# HEALTH MONITORING
# ============================================================
HEALTH_CHECK_PORT=8080

# ============================================================
# ALERTING
# ============================================================
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_TO=admin@example.com
ALERT_ERROR_RATE_THRESHOLD=10.0
ALERT_CPU_THRESHOLD=90.0
ALERT_MEMORY_THRESHOLD=90.0
ALERT_NO_ITERATION_SECONDS=300
ALERT_COOLDOWN_MINUTES=30

# ============================================================
# LOG MANAGEMENT
# ============================================================
LOG_MAX_AGE_DAYS=30
LOG_COMPRESS_AGE_DAYS=7
LOG_MAX_SIZE_MB=100
```

---

## Step 3: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Odoo (if not already running)
docker-compose up -d
```

---

## Step 4: Install Windows Service

**Run as Administrator:**

```bash
install_service.bat
```

This will:
1. Install the service named "GoldTierEmployee"
2. Configure automatic startup on boot
3. Set restart behavior on failure
4. Create service log directory

**Expected output:**
```
[SUCCESS] Service 'GoldTierEmployee' installed successfully!

Next steps:
1. Start service: net start GoldTierEmployee
2. Check status: sc query GoldTierEmployee
3. View logs: service_logs\service_stdout.log
```

---

## Step 5: Start the Service

```bash
# Start service
net start GoldTierEmployee

# Or use the batch script
start_service.bat
```

**Verify service is running:**
```bash
sc query GoldTierEmployee
```

Expected status: `STATE: 4 RUNNING`

---

## Step 6: Verify Health Monitoring

Open your browser and navigate to:

**Dashboard:** http://localhost:8080/

You should see:
- System status (healthy/degraded/unhealthy)
- Uptime
- Iteration count
- Task statistics
- CPU and memory usage

**Health Check API:** http://localhost:8080/health

Returns JSON with detailed health information.

**Metrics API:** http://localhost:8080/metrics

Returns Prometheus-style metrics for monitoring tools.

---

## Step 7: Configure Log Rotation

**Schedule automatic log rotation (runs daily at 2 AM):**

Run as Administrator:
```bash
schedule_log_rotation.bat
```

**Manual log rotation:**
```bash
python deployment\log_rotator.py rotate
```

**View log statistics:**
```bash
python deployment\log_rotator.py stats
```

---

## Service Management

### Start Service
```bash
net start GoldTierEmployee
# or
start_service.bat
```

### Stop Service
```bash
net stop GoldTierEmployee
# or
stop_service.bat
```

### Restart Service
```bash
restart_service.bat
```

### Check Status
```bash
sc query GoldTierEmployee
```

### View Service Configuration
```bash
sc qc GoldTierEmployee
```

### Uninstall Service
```bash
# Run as Administrator
uninstall_service.bat
```

---

## Monitoring and Alerting

### Health Dashboard

Access the web dashboard at: http://localhost:8080/

Features:
- Real-time system status
- Task processing metrics
- Resource usage (CPU, memory, disk)
- Auto-refresh every 10 seconds

### Email Alerts

Configure in `.env`:
```bash
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_TO=admin@example.com
```

Alerts are sent for:
- System unhealthy status
- High error rate (>10%)
- High CPU usage (>90%)
- High memory usage (>90%)
- No iterations for 5+ minutes

**Alert cooldown:** 30 minutes (configurable)

### Health Check Endpoints

**HTTP 200 = Healthy**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-08T12:00:00",
  "uptime_seconds": 3600,
  "iterations": {
    "total": 60,
    "error_count": 0
  },
  "tasks": {
    "total_processed": 45,
    "total_executed": 40
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8
  }
}
```

---

## Log Management

### Log Locations

**Audit Logs:**
- Location: `Audit_Logs/`
- Format: `audit_log_YYYYMMDD.json`
- Contains: All system events with timestamps

**Service Logs:**
- Location: `service_logs/`
- Files:
  - `service_stdout.log` - Standard output
  - `service_stderr.log` - Error output

### Log Rotation

**Automatic (Scheduled):**
- Runs daily at 2:00 AM
- Compresses logs older than 7 days
- Deletes logs older than 30 days

**Manual:**
```bash
python deployment\log_rotator.py rotate
```

**View Statistics:**
```bash
python deployment\log_rotator.py stats
```

### Log Retention Policy

- **Active logs:** Uncompressed, current day
- **Recent logs (1-7 days):** Uncompressed
- **Old logs (7-30 days):** Compressed (.gz)
- **Very old logs (>30 days):** Deleted

---

## Troubleshooting

### Service Won't Start

**Check service logs:**
```bash
type service_logs\service_stderr.log
```

**Common issues:**
1. **Python not found**
   - Verify Python is in PATH
   - Check service configuration: `sc qc GoldTierEmployee`

2. **Port already in use (8080)**
   - Change `HEALTH_CHECK_PORT` in .env
   - Restart service

3. **Odoo not running**
   - Start Odoo: `docker-compose up -d`
   - Verify: http://localhost:8069

4. **Missing dependencies**
   - Reinstall: `pip install -r requirements.txt`

### Service Crashes Repeatedly

**Check error logs:**
```bash
type service_logs\service_stderr.log
```

**Check audit logs:**
```bash
type Audit_Logs\audit_log_YYYYMMDD.json
```

**Common causes:**
- Database connection issues
- Email authentication failures
- Insufficient permissions
- Disk space full

### Health Check Shows "Unhealthy"

**Check dashboard:** http://localhost:8080/

**Possible issues:**
- No iterations running (check kill switch)
- High error rate (check audit logs)
- Resource exhaustion (check Task Manager)

**Restart service:**
```bash
restart_service.bat
```

### Email Alerts Not Working

**Verify configuration:**
```bash
# Check .env file
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_TO=admin@example.com
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**Test email manually:**
```bash
python deployment\alert_manager.py
```

**Common issues:**
- Gmail App Password not configured
- SMTP blocked by firewall
- Invalid email credentials

### High CPU/Memory Usage

**Check dashboard:** http://localhost:8080/

**Reduce load:**
1. Increase loop interval:
   ```bash
   LOOP_INTERVAL_SECONDS=120  # 2 minutes instead of 1
   ```

2. Disable unused monitors:
   ```bash
   FACEBOOK_MONITORING_ENABLED=false
   TWITTER_MONITORING_ENABLED=false
   ```

3. Restart service:
   ```bash
   restart_service.bat
   ```

---

## Performance Tuning

### Optimize Loop Interval

**Default:** 60 seconds

**Light load (few tasks):**
```bash
LOOP_INTERVAL_SECONDS=120  # Check every 2 minutes
```

**Heavy load (many tasks):**
```bash
LOOP_INTERVAL_SECONDS=30   # Check every 30 seconds
```

### Optimize Email Checking

Edit `orchestrator/email_monitor.py`:
```python
def check_new_emails(self, folder: str = 'INBOX', limit: int = 10):
    # Reduce limit for faster checks
    # Default: 10, Reduce to: 5
```

### Optimize Database Queries

Ensure Odoo has proper indexes:
```sql
-- Run in PostgreSQL
CREATE INDEX idx_partner_email ON res_partner(email);
CREATE INDEX idx_lead_create_date ON crm_lead(create_date);
```

---

## Backup and Recovery

### Backup Strategy

**What to backup:**
1. `.env` file (configuration)
2. `Audit_Logs/` directory
3. `Done/` directory (completed tasks)
4. Odoo database (PostgreSQL)

**Backup script (example):**
```bash
@echo off
set BACKUP_DIR=C:\Backups\GoldTier\%date:~-4,4%%date:~-10,2%%date:~-7,2%

mkdir %BACKUP_DIR%

REM Backup configuration
copy .env %BACKUP_DIR%\

REM Backup logs
xcopy /E /I Audit_Logs %BACKUP_DIR%\Audit_Logs

REM Backup completed tasks
xcopy /E /I Done %BACKUP_DIR%\Done

REM Backup Odoo database
docker exec odoo-postgres pg_dump -U odoo odoo > %BACKUP_DIR%\odoo_backup.sql

echo Backup completed: %BACKUP_DIR%
```

### Recovery

**Restore configuration:**
```bash
copy C:\Backups\GoldTier\YYYYMMDD\.env .
```

**Restore Odoo database:**
```bash
docker exec -i odoo-postgres psql -U odoo odoo < C:\Backups\GoldTier\YYYYMMDD\odoo_backup.sql
```

---

## Security Best Practices

### 1. Secure Credentials

- Use App Passwords for Gmail (not main password)
- Store `.env` file securely (not in version control)
- Rotate passwords regularly
- Use strong passwords (16+ characters)

### 2. Network Security

- Restrict health check port (8080) to localhost
- Use firewall rules to block external access
- Consider VPN for remote monitoring

### 3. Service Account

- Run service as dedicated user (not Administrator)
- Grant minimum required permissions
- Audit service account activity

### 4. Audit Logging

- Review audit logs regularly
- Monitor for suspicious activity
- Set up log forwarding to SIEM (optional)

---

## Scaling

### Multiple Workers

Run multiple instances on different machines:

1. **Machine 1:** Email monitoring
2. **Machine 2:** Social media monitoring
3. **Machine 3:** Task execution

Configure each with different responsibilities.

### Load Balancing

Use a task queue (Redis) for distributed processing:

```bash
pip install redis
```

Configure in `.env`:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Database Scaling

For high volume:
1. Use PostgreSQL replication
2. Add read replicas for Odoo
3. Optimize database indexes

---

## Monitoring Integration

### Prometheus

Scrape metrics endpoint:
```yaml
scrape_configs:
  - job_name: 'goldtier'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### Grafana

Create dashboard with:
- Uptime graph
- Task throughput
- Error rate
- Resource usage

### Nagios/Zabbix

Monitor health check endpoint:
```bash
check_http -H localhost -p 8080 -u /health
```

---

## Maintenance

### Weekly Tasks

- Review audit logs for errors
- Check disk space usage
- Verify backup completion
- Review alert emails

### Monthly Tasks

- Update dependencies: `pip install -r requirements.txt --upgrade`
- Review and optimize performance
- Test disaster recovery
- Rotate service account passwords

### Quarterly Tasks

- Security audit
- Performance review
- Capacity planning
- Update documentation

---

## Support

### Logs to Check

1. **Service logs:** `service_logs/service_stderr.log`
2. **Audit logs:** `Audit_Logs/audit_log_YYYYMMDD.json`
3. **Health dashboard:** http://localhost:8080/

### Diagnostic Commands

```bash
# Service status
sc query GoldTierEmployee

# View service config
sc qc GoldTierEmployee

# Check Python version
python --version

# Check dependencies
pip list

# Test Odoo connection
python test_odoo_connection.py

# View log statistics
python deployment\log_rotator.py stats
```

---

## Production Checklist

Before going live:

- [ ] NSSM installed in `tools/` directory
- [ ] `.env` configured with production settings
- [ ] Odoo running and accessible
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Service installed (`install_service.bat`)
- [ ] Service started and running
- [ ] Health dashboard accessible (http://localhost:8080/)
- [ ] Email alerts configured and tested
- [ ] Log rotation scheduled
- [ ] Backup strategy implemented
- [ ] Firewall rules configured
- [ ] Documentation reviewed
- [ ] Team trained on operations

---

## Quick Reference

### Service Commands
```bash
net start GoldTierEmployee      # Start
net stop GoldTierEmployee       # Stop
sc query GoldTierEmployee       # Status
```

### Health Check
```bash
http://localhost:8080/          # Dashboard
http://localhost:8080/health    # API
http://localhost:8080/metrics   # Metrics
```

### Log Management
```bash
python deployment\log_rotator.py rotate    # Rotate logs
python deployment\log_rotator.py stats     # View stats
```

### Troubleshooting
```bash
type service_logs\service_stderr.log       # View errors
type Audit_Logs\audit_log_YYYYMMDD.json   # View audit log
```

---

## Next Steps

After successful deployment:

1. Monitor system for 24 hours
2. Review audit logs daily for first week
3. Tune performance based on actual load
4. Document any custom configurations
5. Train team on monitoring and troubleshooting

**System Status:** 🟢 Ready for Production
