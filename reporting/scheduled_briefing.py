"""
CEO Briefing Scheduler
Automated weekly briefing generation and delivery
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from reporting.ceo_briefing_email_sender import CEOBriefingEmailSender
from src.audit_logger_simple import AuditLogger


def generate_and_send_briefing():
    """Generate and send weekly CEO briefing"""
    print("="*60)
    print("CEO WEEKLY BRIEFING - AUTOMATED GENERATION")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    audit_logger = AuditLogger()
    sender = CEOBriefingEmailSender()

    try:
        # Generate and send briefing
        result = sender.send_weekly_briefing()

        if result['success']:
            print()
            print("="*60)
            print("SUCCESS")
            print("="*60)
            print(f"Message: {result['message']}")
            print(f"Recipients: {', '.join(result['recipients'])}")
            print()
            print("Briefing files:")
            print(f"  HTML: {result['briefing']['html_path']}")
            print(f"  Text: {result['briefing']['text_path']}")
            print(f"  JSON: {result['briefing']['json_path']}")
            print()

            audit_logger.log_event(
                event_type='ceo_briefing_scheduled_success',
                details=result,
                severity='info'
            )

            return 0

        else:
            print()
            print("="*60)
            print("FAILED")
            print("="*60)
            print(f"Message: {result['message']}")
            if 'note' in result:
                print(f"Note: {result['note']}")
            print()

            audit_logger.log_event(
                event_type='ceo_briefing_scheduled_failed',
                details=result,
                severity='warning'
            )

            return 1

    except Exception as e:
        print()
        print("="*60)
        print("ERROR")
        print("="*60)
        print(f"Exception: {e}")
        print()

        import traceback
        traceback.print_exc()

        audit_logger.log_event(
            event_type='ceo_briefing_scheduled_error',
            details={'error': str(e)},
            severity='error'
        )

        return 1


if __name__ == "__main__":
    exit_code = generate_and_send_briefing()
    sys.exit(exit_code)
