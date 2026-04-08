# Integration Guide - Email & Social Media

## Overview

Your Gold Tier Autonomous Employee now includes:
- **Email Auto-Response** - Monitors incoming emails and responds automatically
- **Social Media Monitoring** - Tracks mentions on Facebook, Twitter, and Instagram

---

## Email Integration

### Features
- IMAP monitoring for new emails
- Automatic customer and lead creation in Odoo
- Intelligent auto-response based on inquiry type
- Duplicate detection (won't process same email twice)

### Configuration

Add to your `.env` file:

```bash
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
EMAIL_FROM_NAME=AI Employee
```

### Gmail Setup

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password
3. Use the App Password as `EMAIL_PASSWORD` in .env

### How It Works

1. **Email arrives** → System checks IMAP inbox every 60 seconds
2. **Email parsed** → Extracts sender, subject, body
3. **Task created** → Creates JSON task in `Inbox/` folder
4. **Customer created** → Searches for existing customer, creates if new
5. **Lead created** → Creates opportunity in Odoo CRM
6. **Auto-response sent** → Sends confirmation email to customer

### Response Templates

**Customer Inquiry:**
```
Dear [Name],

Thank you for reaching out to us! We've received your inquiry 
and our team has been notified.

We've created a record in our system and one of our representatives 
will get back to you within 24 hours.

Best regards,
AI Employee
```

**Sales Inquiry:**
```
Dear [Name],

Thank you for your interest in our products/services!

We've received your inquiry and have created a sales opportunity 
in our system. Our sales team has been notified and will reach 
out to you within 24 hours.

Best regards,
AI Employee
```

### Testing

```bash
# Test email response generation
python orchestrator/email_response_handler.py

# Test email monitoring
python orchestrator/email_monitor.py

# Test full integration
python test_email_integration.py
```

---

## Social Media Integration

### Features
- Facebook page monitoring (mentions, comments)
- Twitter/X monitoring (mentions, replies)
- Instagram monitoring (comments, mentions)
- Automatic lead creation for inquiries
- Mention classification (inquiry, sales, positive, general)

### Configuration

Add to your `.env` file:

```bash
# Facebook
FACEBOOK_MONITORING_ENABLED=true
FACEBOOK_PAGE_ID=your-page-id
FACEBOOK_ACCESS_TOKEN=your-access-token

# Twitter/X
TWITTER_MONITORING_ENABLED=true
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret

# Instagram
INSTAGRAM_MONITORING_ENABLED=true
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-account-id
```

### How It Works

1. **Mention detected** → System checks platforms every 60 seconds
2. **Mention classified** → Determines type (inquiry, sales, positive, general)
3. **Task created** → Creates JSON task in `Inbox/` folder
4. **Lead created** → For inquiries/sales opportunities, creates lead in Odoo
5. **Logged** → All mentions logged to audit trail

### Mention Classification

- **Customer Inquiry** → Contains: question, how, what, price, help, support
- **Sales Opportunity** → Contains: interested, demo, trial, quote
- **Positive Engagement** → Contains: love, great, awesome, amazing
- **General Mention** → Everything else

### Platform Setup

#### Facebook
1. Create Facebook App at https://developers.facebook.com
2. Add "Pages" permission
3. Generate Page Access Token
4. Get Page ID from Page Settings

#### Twitter/X
1. Create Twitter App at https://developer.twitter.com
2. Enable OAuth 2.0
3. Generate Bearer Token and API credentials
4. Set up read/write permissions

#### Instagram
1. Convert to Business Account
2. Connect to Facebook Page
3. Use Facebook Graph API
4. Get Business Account ID

### Testing

```bash
# Test social media monitoring
python orchestrator/social_media_monitor.py

# Test full integration
python test_social_media_integration.py
```

---

## Autonomous Loop Integration

Both email and social media monitoring are integrated into the main autonomous loop.

### Workflow

```
Every 60 seconds:
1. Check for new emails → Create tasks
2. Check social media → Create tasks
3. Process Inbox/ → Classify and route
4. Execute Needs_Action/ → Run tasks
5. Move to Done/ → Archive completed
```

### Starting the Loop

```bash
# Windows
start_autonomous_loop.bat

# Command line
python orchestrator/autonomous_loop.py
```

### Monitoring

Watch the console output:
```
[Iteration 1] 2026-04-08 03:45:00
  [Email] Created 2 tasks from new emails
  [Social] Created 1 tasks from mentions
  [Inbox] Processed 3 tasks
  [Action] Executed 3 tasks
  [Status] Sleeping for 60 seconds...
```

### Logs

All activity is logged to:
- `Audit_Logs/audit_log_YYYYMMDD.json` - All events
- `Audit_Logs/processed_emails.json` - Processed email IDs
- `Audit_Logs/processed_mentions.json` - Processed mention IDs

---

## Task Flow Examples

### Email Inquiry Flow

```
1. Email arrives: "I need pricing information"
   ↓
2. email_monitor.py creates: Inbox/email_inquiry_20260408_120000.json
   ↓
3. task_processor.py classifies as: odoo (email_inquiry)
   ↓
4. decision_engine.py plans:
   - Search for customer
   - Create customer if needed
   - Create lead
   - Send auto-response
   ↓
5. Actions executed → Customer + Lead in Odoo, Email sent
   ↓
6. Task moved to: Done/email_inquiry_20260408_120000.json
```

### Social Media Mention Flow

```
1. Facebook comment: "Can you help with pricing?"
   ↓
2. social_media_monitor.py creates: Inbox/social_mention_facebook_20260408_120000.json
   ↓
3. task_processor.py classifies as: social_media (mention)
   ↓
4. decision_engine.py plans:
   - Create lead in Odoo
   ↓
5. Lead created → Sales team can follow up
   ↓
6. Task moved to: Done/social_mention_facebook_20260408_120000.json
```

---

## Troubleshooting

### Email Not Working

**Issue:** No emails being processed

**Solutions:**
- Check: `EMAIL_ADDRESS` and `EMAIL_PASSWORD` in .env
- Check: Gmail App Password (not regular password)
- Check: IMAP enabled in Gmail settings
- Test: `python orchestrator/email_monitor.py`
- Check logs: `Audit_Logs/audit_log_*.json`

### Social Media Not Working

**Issue:** No mentions being detected

**Solutions:**
- Check: Platform enabled in .env (`*_MONITORING_ENABLED=true`)
- Check: API credentials configured
- Check: API rate limits not exceeded
- Test: `python orchestrator/social_media_monitor.py`
- Note: Simulated data in development mode

### Auto-Response Not Sending

**Issue:** Emails received but no response sent

**Solutions:**
- Check: `requires_response: true` in task
- Check: SMTP credentials in .env
- Check: `EMAIL_PASSWORD` is App Password
- Test: `python orchestrator/email_response_handler.py`

---

## Production Deployment

### Security Best Practices

1. **Never commit .env file** - Add to .gitignore
2. **Use App Passwords** - Not your main account password
3. **Rotate credentials** - Change passwords regularly
4. **Monitor logs** - Check for suspicious activity
5. **Rate limiting** - Already built into MCP server

### Performance Optimization

1. **Adjust loop interval** - Change `LOOP_INTERVAL_SECONDS` in .env
2. **Limit email fetch** - Modify `limit` parameter in email_monitor.py
3. **Database indexing** - Ensure Odoo has proper indexes
4. **Log rotation** - Implement log cleanup for old audit logs

### Scaling

1. **Multiple workers** - Run multiple autonomous loops
2. **Queue system** - Add Redis/RabbitMQ for task queue
3. **Load balancing** - Distribute across multiple servers
4. **Database replication** - Scale Odoo database

---

## Next Steps

### Immediate
- Configure email credentials
- Test email integration
- Configure social media credentials (optional)
- Start autonomous loop

### Optional Enhancements
- CEO briefing system (weekly reports)
- Advanced risk rules (custom logic)
- Approval workflows (web UI)
- Multi-language support
- Custom response templates
- Sentiment analysis
- Priority routing

---

## Support

For issues or questions:
1. Check logs in `Audit_Logs/`
2. Run test suites
3. Review this guide
4. Check QUICKSTART.md

**System Status:**
- ✅ Email integration complete
- ✅ Social media integration complete
- ✅ Autonomous loop operational
- ✅ Odoo integration working
- ✅ All tests passing
