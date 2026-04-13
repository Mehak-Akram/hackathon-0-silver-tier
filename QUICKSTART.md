# Gold Tier Autonomous Employee - Quick Start Guide

> **⚠️ System Status**: This is a Gold Tier implementation with email monitoring, social media integration, Odoo CRM, and automated reporting. Many features require proper API credentials and configuration. Test in development mode before production use.

## 🎉 Congratulations! Your Autonomous Employee is Ready

You've successfully built a fully autonomous AI employee that can:
- Monitor tasks automatically
- Create customers in Odoo CRM
- Create leads and opportunities
- Assess risk before taking action
- Log all activities for audit

---

## 🚀 How to Start

### Method 1: Windows Batch File (Easiest)
```
Double-click: start_autonomous_loop.bat
```

### Method 2: Command Line
```bash
python orchestrator/autonomous_loop.py
```

---

## 📝 How to Use

### 1. Create a Task File

Drop a JSON file in the `Inbox/` folder:

**Example: Create Customer**
```json
{
  "type": "odoo",
  "content": "Create customer Jane Doe with email jane@example.com",
  "customer_name": "Jane Doe",
  "customer_email": "jane@example.com",
  "customer_phone": "+1234567890"
}
```

**Example: Create Lead**
```json
{
  "type": "odoo",
  "content": "Create lead for Product Demo Request",
  "lead_title": "Product Demo Request",
  "customer_email": "demo@example.com",
  "description": "Customer interested in product demo"
}
```

### 2. Watch It Process

The autonomous loop will:
1. **Scan Inbox/** every 60 seconds
2. **Classify** the task (email, social, odoo, general)
3. **Assess risk** (low, medium, high)
4. **Route** to appropriate folder:
   - Low/Medium risk → `Needs_Action/`
   - High risk → `Pending_Approval/`
5. **Execute** tasks from `Needs_Action/`
6. **Move** completed tasks to `Done/`

### 3. Check Results

- **Odoo Dashboard**: http://localhost:8069
- **Audit Logs**: `Audit_Logs/` folder
- **Completed Tasks**: `Done/` folder

---

## 📂 Folder Structure

```
Inbox/              ← Drop new tasks here
Needs_Action/       ← Tasks ready to execute
Pending_Approval/   ← High-risk tasks waiting for approval
Done/               ← Completed tasks
Rejected/           ← Rejected tasks
Audit_Logs/         ← All activity logs
```

---

## ⚙️ Configuration

Edit `.env` file:

```bash
# Enable/disable autonomous mode
ENABLE_AUTONOMOUS_LOOP=true

# How often to check for new tasks (seconds)
LOOP_INTERVAL_SECONDS=60

# Odoo connection
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=your-email@example.com
ODOO_PASSWORD=your-secure-password
```

---

## 🛡️ Safety Features

### Risk Assessment
- **Low Risk**: Auto-executed (logging, reading data)
- **Medium Risk**: Auto-executed with audit (creating customers, sending emails)
- **High Risk**: Requires approval (financial transactions, deletions)

### Kill Switch
To emergency stop all operations:
```python
from src.kill_switch_simple import KillSwitch
kill_switch = KillSwitch()
kill_switch.activate("Emergency stop reason")
```

### Audit Trail
Every action is logged to `Audit_Logs/` with:
- Timestamp
- Action type
- Risk level
- Result
- Details

---

## 🧪 Testing

Run the test suite:
```bash
python test_autonomous_loop.py
```

This will:
- Create sample tasks
- Process them through the system
- Verify Odoo integration works
- Show you the complete workflow

---

## 📊 What Happens Next

### Automatic Processing Flow

```
1. Task arrives in Inbox/
   ↓
2. Task Processor scans and classifies
   ↓
3. Risk Engine assesses safety
   ↓
4. Task routed to Needs_Action/ or Pending_Approval/
   ↓
5. Decision Engine creates execution plan
   ↓
6. Actions executed (Odoo, email, social media)
   ↓
7. Results logged to Audit_Logs/
   ↓
8. Task moved to Done/
```

---

## 🎯 Real-World Examples

### Example 1: Customer Inquiry from Website
1. Website form submission → Creates JSON in Inbox/
2. System creates customer in Odoo
3. System creates lead/opportunity
4. Sales team sees it in Odoo CRM dashboard

### Example 2: Social Media Mention
1. Social media monitoring detects mention
2. Creates task in Inbox/
3. System creates lead in Odoo
4. Optionally sends auto-response

### Example 3: Email Request
1. Email arrives with customer request
2. Parsed into task JSON
3. System creates customer + lead
4. Sends confirmation email

---

## 🔧 Troubleshooting

### Loop Not Starting
- Check: `ENABLE_AUTONOMOUS_LOOP=true` in .env
- Check: Odoo is running (`docker ps`)
- Check: No kill switch active

### Tasks Not Processing
- Check: Files are in `Inbox/` folder
- Check: Files are valid JSON
- Check: Audit logs for errors

### Odoo Connection Failed
- Check: Odoo running at http://localhost:8069
- Check: Credentials in .env are correct
- Test: `python test_odoo_connection.py`

---

## 📈 Next Steps (Optional Enhancements)

### Phase 2: Advanced Features
1. ✅ **Email Integration** - Process incoming emails automatically (COMPLETED)
   - IMAP monitoring for new emails
   - Auto-response generation based on inquiry type
   - Customer and lead creation from email inquiries
2. ✅ **Social Media Integration** - Monitor and respond to social media (COMPLETED)
   - Facebook page monitoring and posting
   - Twitter/X monitoring and posting
   - Instagram monitoring and posting
   - Automatic lead creation from mentions
3. ✅ **CEO Briefing System** - Weekly automated reports (COMPLETED)
   - Automated metrics collection
   - Professional HTML/text/JSON reports
   - Week-over-week comparisons
   - Email delivery to executives
   - Scheduled weekly generation
4. **Advanced Risk Rules** - Custom risk assessment logic
5. **Approval Workflows** - Web UI for approving high-risk tasks

### Phase 3: Production Deployment ✅ COMPLETED
1. ✅ **Windows Service** - Run as background service
2. ✅ **Health Monitoring** - HTTP dashboard and metrics
3. ✅ **Alerting System** - Email notifications
4. ✅ **Log Management** - Automatic rotation

---

## ✅ Success Checklist

- [x] Odoo 19 installed and running
- [x] Autonomous loop tested and working
- [x] Sample tasks processed successfully
- [x] Audit logging functional
- [x] Risk assessment working
- [x] Odoo integration verified
- [x] Email auto-response integration complete
- [x] Social media monitoring integration complete
- [x] Production deployment ready
- [x] Health monitoring operational
- [x] CEO briefing system complete

**You're ready to go! 🚀**

Drop a task in `Inbox/` and watch your autonomous employee work!

---

## 📚 Additional Documentation

- **DEPLOYMENT.md** - Production deployment guide (Windows service, monitoring)
- **INTEGRATION_GUIDE.md** - Email and social media setup
- **CEO_BRIEFING_GUIDE.md** - Executive reporting system
- **SYSTEM_STATUS.md** - Complete system overview
- **CLAUDE.md** - Project instructions and guidelines
- **Audit_Logs/** - All system activity logs
