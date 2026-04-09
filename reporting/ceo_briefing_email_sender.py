"""
CEO Briefing Email Sender
Sends weekly briefings via email
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from reporting.ceo_briefing_generator import CEOBriefingGenerator
from src.audit_logger_simple import AuditLogger


class CEOBriefingEmailSender:
    """
    Sends CEO briefings via email
    """

    def __init__(self):
        """Initialize email sender"""
        self.audit_logger = AuditLogger()

        # Email configuration
        self.enabled = os.getenv('CEO_BRIEFING_EMAIL_ENABLED', 'false').lower() == 'true'
        self.recipients = os.getenv('CEO_BRIEFING_RECIPIENTS', '').split(',')
        self.recipients = [r.strip() for r in self.recipients if r.strip()]

        self.from_email = os.getenv('EMAIL_ADDRESS', '')
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_password = os.getenv('EMAIL_PASSWORD', '')

        self.briefing_generator = CEOBriefingGenerator()

    def send_weekly_briefing(self, end_date: datetime = None) -> Dict[str, Any]:
        """
        Generate and send weekly briefing

        Args:
            end_date: End of reporting period (defaults to now)

        Returns:
            Result dictionary
        """
        if not self.enabled:
            return {
                'success': False,
                'message': 'CEO briefing email is disabled',
                'note': 'Set CEO_BRIEFING_EMAIL_ENABLED=true in .env to enable'
            }

        if not self.recipients:
            return {
                'success': False,
                'message': 'No recipients configured',
                'note': 'Set CEO_BRIEFING_RECIPIENTS in .env'
            }

        if not self.from_email or not self.smtp_password:
            return {
                'success': False,
                'message': 'Email credentials not configured',
                'note': 'Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env'
            }

        try:
            # Generate briefing
            print("[1/3] Generating briefing...")
            briefing = self.briefing_generator.generate_weekly_briefing(end_date)

            # Send email
            print("[2/3] Sending email...")
            self._send_email(briefing)

            # Log success
            print("[3/3] Logging...")
            self.audit_logger.log_event(
                event_type='ceo_briefing_sent',
                details={
                    'recipients': self.recipients,
                    'period': briefing['period'],
                    'html_path': briefing['html_path']
                },
                severity='info'
            )

            return {
                'success': True,
                'message': f"Briefing sent to {len(self.recipients)} recipient(s)",
                'recipients': self.recipients,
                'briefing': briefing
            }

        except Exception as e:
            self.audit_logger.log_event(
                event_type='ceo_briefing_send_failed',
                details={'error': str(e)},
                severity='error'
            )

            return {
                'success': False,
                'message': f"Failed to send briefing: {e}"
            }

    def _send_email(self, briefing: Dict[str, Any]):
        """
        Send email with briefing

        Args:
            briefing: Briefing data with file paths
        """
        # Read HTML content
        html_path = Path(briefing['html_path'])
        html_content = html_path.read_text(encoding='utf-8')

        # Read text content
        text_path = Path(briefing['text_path'])
        text_content = text_path.read_text(encoding='utf-8')

        # Format period for subject
        start_date = datetime.fromisoformat(briefing['period']['start'])
        end_date = datetime.fromisoformat(briefing['period']['end'])
        period_str = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"CEO Weekly Briefing - {period_str}"
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.recipients)

        # Attach text and HTML versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Attach JSON data file
        json_path = Path(briefing['json_path'])
        with open(json_path, 'rb') as f:
            attachment = MIMEBase('application', 'json')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename={json_path.name}'
            )
            msg.attach(attachment)

        # Send email
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.from_email, self.smtp_password)
            server.send_message(msg)

        print(f"[SUCCESS] Email sent to: {', '.join(self.recipients)}")


if __name__ == "__main__":
    # Test email sender
    sender = CEOBriefingEmailSender()

    print("="*60)
    print("CEO BRIEFING EMAIL SENDER TEST")
    print("="*60)
    print()

    if not sender.enabled:
        print("[INFO] CEO briefing email is disabled")
        print("[INFO] Set CEO_BRIEFING_EMAIL_ENABLED=true in .env to enable")
        print()
        print("Testing briefing generation only...")
        print()

        # Generate briefing without sending
        briefing = sender.briefing_generator.generate_weekly_briefing()
        print(f"[SUCCESS] Briefing generated: {briefing['html_path']}")
    else:
        # Send briefing
        result = sender.send_weekly_briefing()

        if result['success']:
            print(f"[SUCCESS] {result['message']}")
            print(f"Recipients: {', '.join(result['recipients'])}")
        else:
            print(f"[ERROR] {result['message']}")
            if 'note' in result:
                print(f"Note: {result['note']}")
