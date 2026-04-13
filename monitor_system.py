
"""
System Monitor - Real-time monitoring of Gold Tier AI Employee
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import json
from datetime import datetime
from src.kill_switch_simple import KillSwitch


def monitor_system():
    """Monitor system status and display real-time information."""
    print("\n" + "="*70)
    print(" GOLD TIER AUTONOMOUS AI EMPLOYEE - SYSTEM MONITOR")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check kill switch
    print("\n[SAFETY SYSTEMS]")
    kill_switch = KillSwitch()
    if kill_switch.is_active():
        print("  [WARN] Kill switch: ACTIVE - System halted")
    else:
        print("  [OK] Kill switch: INACTIVE - System operational")

    # Check folders
    print("\n[TASK FOLDERS]")
    folders = {
        "Inbox": Path("Inbox"),
        "Needs_Action": Path("Needs_Action"),
        "Pending_Approval": Path("Pending_Approval"),
        "Approved": Path("Approved"),
        "Done": Path("Done"),
        "Rejected": Path("Rejected")
    }

    for name, folder in folders.items():
        if folder.exists():
            count = len(list(folder.glob("*.md")))
            print(f"  {name:20s}: {count:3d} tasks")
        else:
            print(f"  {name:20s}:   - (not created)")

    # Check briefings
    print("\n[BRIEFINGS]")
    briefings_path = Path("Briefings")
    if briefings_path.exists():
        briefings = list(briefings_path.glob("*.md"))
        print(f"  Total briefings: {len(briefings)}")
        if briefings:
            latest = max(briefings, key=lambda p: p.stat().st_mtime)
            print(f"  Latest: {latest.name}")
    else:
        print("  No briefings folder")

    # Check audit logs
    print("\n[AUDIT LOGS]")
    audit_path = Path("Audit_Logs")
    if audit_path.exists():
        logs = list(audit_path.glob("*.jsonl"))
        print(f"  Total log files: {len(logs)}")

        # Count today's events
        today = datetime.now().strftime("%Y-%m-%d")
        today_log = audit_path / f"{today}-audit.jsonl"

        if today_log.exists():
            with open(today_log, 'r') as f:
                events = [json.loads(line) for line in f if line.strip()]
            print(f"  Today's events: {len(events)}")

            # Count by type
            event_types = {}
            for event in events:
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1

            print("  Event breakdown:")
            for event_type, count in sorted(event_types.items()):
                print(f"    - {event_type}: {count}")
        else:
            print("  No events today")
    else:
        print("  No audit logs folder")

    # System configuration
    print("\n[CONFIGURATION]")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("ENABLE_AUTONOMOUS_LOOP"):
                    print(f"  {line.strip()}")
                elif line.startswith("LOOP_INTERVAL_SECONDS"):
                    print(f"  {line.strip()}")
                elif line.startswith("CEO_BRIEFING_DAY"):
                    print(f"  {line.strip()}")

    print("\n" + "="*70)
    print(" SYSTEM STATUS: OPERATIONAL")
    print("="*70)


if __name__ == "__main__":
    try:
        monitor_system()
    except Exception as e:
        print(f"\n[ERROR] Monitoring failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
