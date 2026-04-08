"""
Email Monitor
Monitors incoming emails and creates tasks for the autonomous loop
"""

import os
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger


class EmailMonitor:
    """
    Monitors incoming emails and creates tasks for autonomous processing
    """

    def __init__(self):
        """Initialize email monitor"""
        self.imap_host = os.getenv('IMAP_HOST', 'imap.gmail.com')
        self.imap_port = int(os.getenv('IMAP_PORT', '993'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')

        self.inbox_path = Path('./Inbox')
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        self.audit_logger = AuditLogger()
        self.processed_emails_file = Path('./Audit_Logs/processed_emails.json')

        # Load processed email IDs
        self.processed_emails = self._load_processed_emails()

    def _load_processed_emails(self) -> set:
        """Load set of already processed email IDs"""
        if self.processed_emails_file.exists():
            try:
                data = json.loads(self.processed_emails_file.read_text())
                return set(data.get('processed_ids', []))
            except:
                return set()
        return set()

    def _save_processed_email(self, email_id: str):
        """Save email ID as processed"""
        self.processed_emails.add(email_id)

        self.processed_emails_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_emails_file.write_text(json.dumps({
            'processed_ids': list(self.processed_emails),
            'last_updated': datetime.now().isoformat()
        }, indent=2))

    def connect(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Connect to email server

        Returns:
            IMAP connection or None if failed
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_address, self.email_password)
            return mail
        except Exception as e:
            self.audit_logger.log_event(
                event_type='email_connection_error',
                details={'error': str(e)},
                severity='error'
            )
            return None

    def decode_email_subject(self, subject: str) -> str:
        """Decode email subject"""
        try:
            decoded_parts = decode_header(subject)
            decoded_subject = ''

            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_subject += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_subject += part

            return decoded_subject
        except:
            return subject

    def parse_email(self, msg) -> Dict[str, Any]:
        """
        Parse email message

        Args:
            msg: Email message object

        Returns:
            Parsed email dictionary
        """
        # Get subject
        subject = self.decode_email_subject(msg.get('Subject', ''))

        # Get sender
        from_header = msg.get('From', '')

        # Get body
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())

        return {
            'subject': subject,
            'from': from_header,
            'body': body,
            'date': msg.get('Date', ''),
            'message_id': msg.get('Message-ID', '')
        }

    def classify_email(self, email_data: Dict[str, Any]) -> str:
        """
        Classify email type

        Args:
            email_data: Parsed email data

        Returns:
            Email classification
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()

        # Customer inquiry keywords
        inquiry_keywords = [
            'inquiry', 'question', 'interested', 'demo', 'pricing',
            'quote', 'information', 'help', 'support', 'contact'
        ]

        # Check if it's a customer inquiry
        if any(keyword in subject or keyword in body for keyword in inquiry_keywords):
            return 'customer_inquiry'

        # Check for order/purchase
        if any(word in subject or word in body for word in ['order', 'purchase', 'buy']):
            return 'sales_inquiry'

        # Default
        return 'general'

    def create_task_from_email(self, email_data: Dict[str, Any]) -> Path:
        """
        Create task file from email

        Args:
            email_data: Parsed email data

        Returns:
            Path to created task file
        """
        email_type = self.classify_email(email_data)

        # Extract sender email
        from_header = email_data.get('from', '')
        sender_email = from_header.split('<')[-1].strip('>') if '<' in from_header else from_header

        # Create task
        task = {
            'type': 'email_inquiry',
            'classified_type': 'odoo',
            'content': f"Customer inquiry from {sender_email}",
            'email_subject': email_data.get('subject'),
            'email_body': email_data.get('body'),
            'email_from': from_header,
            'sender_email': sender_email,
            'customer_email': sender_email,
            'inquiry_type': email_type,
            'timestamp': datetime.now().isoformat(),
            'requires_response': True
        }

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"email_inquiry_{timestamp}.json"
        task_path = self.inbox_path / filename

        # Write task
        task_path.write_text(json.dumps(task, indent=2))

        self.audit_logger.log_event(
            event_type='email_task_created',
            details={
                'file': filename,
                'from': sender_email,
                'subject': email_data.get('subject')
            },
            severity='info'
        )

        return task_path

    def check_new_emails(self, folder: str = 'INBOX', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Check for new unread emails

        Args:
            folder: Email folder to check
            limit: Maximum number of emails to process

        Returns:
            List of new email data
        """
        mail = self.connect()
        if not mail:
            return []

        new_emails = []

        try:
            # Select folder
            mail.select(folder)

            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')

            if status != 'OK':
                return []

            email_ids = messages[0].split()

            # Process recent emails (limit)
            for email_id in email_ids[-limit:]:
                email_id_str = email_id.decode()

                # Skip if already processed
                if email_id_str in self.processed_emails:
                    continue

                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                if status != 'OK':
                    continue

                # Parse email
                msg = email.message_from_bytes(msg_data[0][1])
                email_data = self.parse_email(msg)
                email_data['email_id'] = email_id_str

                new_emails.append(email_data)

                # Mark as processed
                self._save_processed_email(email_id_str)

            mail.close()
            mail.logout()

        except Exception as e:
            self.audit_logger.log_event(
                event_type='email_check_error',
                details={'error': str(e)},
                severity='error'
            )

        return new_emails

    def process_new_emails(self) -> int:
        """
        Check for new emails and create tasks

        Returns:
            Number of tasks created
        """
        new_emails = self.check_new_emails()

        tasks_created = 0
        for email_data in new_emails:
            try:
                self.create_task_from_email(email_data)
                tasks_created += 1
            except Exception as e:
                self.audit_logger.log_event(
                    event_type='email_task_creation_error',
                    details={
                        'email_from': email_data.get('from'),
                        'error': str(e)
                    },
                    severity='error'
                )

        if tasks_created > 0:
            print(f"[Email Monitor] Created {tasks_created} tasks from new emails")

        return tasks_created


def main():
    """Test email monitor"""
    print("="*60)
    print("EMAIL MONITOR TEST")
    print("="*60)

    monitor = EmailMonitor()

    print("\nChecking for new emails...")
    count = monitor.process_new_emails()

    print(f"\n[OK] Processed {count} new emails")
    print("\nTasks created in Inbox/ folder")


if __name__ == "__main__":
    main()
