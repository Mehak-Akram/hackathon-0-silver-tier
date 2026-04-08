"""
Email Response Handler
Generates and sends intelligent auto-responses to customer inquiries
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger


class EmailResponseHandler:
    """
    Handles automatic email responses to customer inquiries
    """

    def __init__(self):
        """Initialize email response handler"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.from_name = os.getenv('EMAIL_FROM_NAME', 'AI Employee')

        self.audit_logger = AuditLogger()

    def generate_response(self, inquiry_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate intelligent response based on inquiry type

        Args:
            inquiry_data: Customer inquiry data

        Returns:
            Dictionary with subject and body
        """
        inquiry_type = inquiry_data.get('inquiry_type', 'general')
        customer_name = self._extract_name(inquiry_data.get('email_from', ''))

        # Response templates
        if inquiry_type == 'customer_inquiry':
            subject = f"Re: {inquiry_data.get('email_subject', 'Your Inquiry')}"
            body = f"""Dear {customer_name},

Thank you for reaching out to us! We've received your inquiry and our team has been notified.

We've created a record in our system and one of our representatives will get back to you within 24 hours.

In the meantime, if you have any urgent questions, please don't hesitate to reply to this email.

Best regards,
{self.from_name}

---
This is an automated response. A human team member will follow up shortly.
"""

        elif inquiry_type == 'sales_inquiry':
            subject = f"Re: {inquiry_data.get('email_subject', 'Your Sales Inquiry')}"
            body = f"""Dear {customer_name},

Thank you for your interest in our products/services!

We've received your inquiry and have created a sales opportunity in our system. Our sales team has been notified and will reach out to you within 24 hours to discuss your needs.

We're excited to help you find the perfect solution!

Best regards,
{self.from_name}

---
This is an automated response. Our sales team will contact you shortly.
"""

        else:
            subject = f"Re: {inquiry_data.get('email_subject', 'Your Message')}"
            body = f"""Dear {customer_name},

Thank you for contacting us! We've received your message and our team will review it shortly.

We aim to respond to all inquiries within 24-48 hours.

Best regards,
{self.from_name}

---
This is an automated response.
"""

        return {
            'subject': subject,
            'body': body
        }

    def _extract_name(self, from_header: str) -> str:
        """Extract name from email header"""
        if '<' in from_header:
            name = from_header.split('<')[0].strip().strip('"')
            if name:
                return name

        # Use email address
        email = from_header.split('<')[-1].strip('>')
        return email.split('@')[0].capitalize()

    def send_response(
        self,
        to_email: str,
        subject: str,
        body: str,
        in_reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email response

        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            in_reply_to: Message ID to reply to

        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
                msg['References'] = in_reply_to

            # Attach body
            msg.attach(MIMEText(body, 'plain'))

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            self.audit_logger.log_event(
                event_type='email_response_sent',
                details={
                    'to': to_email,
                    'subject': subject
                },
                severity='info'
            )

            return True

        except Exception as e:
            self.audit_logger.log_event(
                event_type='email_send_error',
                details={
                    'to': to_email,
                    'error': str(e)
                },
                severity='error'
            )
            return False

    def handle_inquiry(self, inquiry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle customer inquiry - generate and send response

        Args:
            inquiry_data: Customer inquiry data

        Returns:
            Result dictionary
        """
        # Generate response
        response = self.generate_response(inquiry_data)

        # Send response
        to_email = inquiry_data.get('sender_email') or inquiry_data.get('customer_email')

        if not to_email:
            return {
                'success': False,
                'error': 'No recipient email found'
            }

        success = self.send_response(
            to_email=to_email,
            subject=response['subject'],
            body=response['body'],
            in_reply_to=inquiry_data.get('message_id')
        )

        return {
            'success': success,
            'to': to_email,
            'subject': response['subject'],
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Test email response handler"""
    print("="*60)
    print("EMAIL RESPONSE HANDLER TEST")
    print("="*60)

    handler = EmailResponseHandler()

    # Test inquiry
    test_inquiry = {
        'inquiry_type': 'customer_inquiry',
        'email_subject': 'Product Information Request',
        'email_from': 'John Doe <john@example.com>',
        'sender_email': 'john@example.com',
        'email_body': 'I would like to know more about your products.'
    }

    print("\nGenerating response...")
    response = handler.generate_response(test_inquiry)

    print(f"\n[OK] Generated response:")
    print(f"Subject: {response['subject']}")
    print(f"\nBody:\n{response['body']}")

    print("\n[INFO] To actually send, call handler.handle_inquiry(inquiry_data)")


if __name__ == "__main__":
    main()
