"""
Audit Logging Test - Demonstrate Gold Tier audit trail
"""
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("E:/AI_Employee_Vault")
AUDIT_PATH = VAULT_PATH / "Audit_Logs"
AUDIT_PATH.mkdir(exist_ok=True)

def log_audit_event(event_type, action, risk_level, details):
    """Log an audit event in JSON Lines format."""

    timestamp = datetime.now()
    log_file = AUDIT_PATH / f"{timestamp.strftime('%Y-%m-%d')}-audit.jsonl"

    event = {
        "timestamp": timestamp.isoformat(),
        "event_type": event_type,
        "action": action,
        "risk_level": risk_level,
        "details": details,
        "system": "gold_tier_autonomous_employee",
        "version": "1.0.0"
    }

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')

    return event

print("=" * 80)
print("AUDIT LOGGING DEMONSTRATION")
print("=" * 80)
print()

# Log various events
events = [
    {
        "event_type": "task_created",
        "action": "create_task",
        "risk_level": "low",
        "details": {
            "task_id": "test_001",
            "description": "Generate weekly report",
            "domain": "business"
        }
    },
    {
        "event_type": "task_executed",
        "action": "execute_task",
        "risk_level": "low",
        "details": {
            "task_id": "test_001",
            "status": "completed",
            "duration_seconds": 2.5
        }
    },
    {
        "event_type": "briefing_generated",
        "action": "generate_ceo_briefing",
        "risk_level": "low",
        "details": {
            "week_start": "2026-03-16",
            "week_end": "2026-03-22",
            "file_path": "Briefings/Monday_CEO_Briefing_2026-03-16.md"
        }
    },
    {
        "event_type": "high_risk_action",
        "action": "create_invoice",
        "risk_level": "high",
        "details": {
            "task_id": "invoice_001",
            "customer": "ABC Corp",
            "amount": 1500.00,
            "status": "pending_approval"
        }
    },
    {
        "event_type": "approval_required",
        "action": "escalate_to_human",
        "risk_level": "high",
        "details": {
            "task_id": "invoice_001",
            "reason": "Financial transaction requires approval",
            "escalation_path": "Pending_Approval/invoice_001.md"
        }
    }
]

for event_data in events:
    event = log_audit_event(**event_data)
    print(f"[{event['timestamp']}] {event['event_type'].upper()}")
    print(f"  Action: {event['action']}")
    print(f"  Risk: {event['risk_level'].upper()}")
    print(f"  Details: {json.dumps(event['details'], indent=4)}")
    print()

# Show audit log file
log_file = AUDIT_PATH / f"{datetime.now().strftime('%Y-%m-%d')}-audit.jsonl"
print(f"Audit log saved to: {log_file}")
print()

# Read and display log
print("AUDIT LOG CONTENTS:")
print("-" * 80)
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        event = json.loads(line)
        print(f"{event['timestamp']} | {event['event_type']:20s} | {event['risk_level']:6s} | {event['action']}")

print()
print("=" * 80)
print("AUDIT LOGGING TEST COMPLETED")
print("=" * 80)
