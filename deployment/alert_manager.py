"""
Alerting System
Sends notifications when system issues are detected
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger


class AlertManager:
    """
    Manages system alerts and notifications
    """

    def __init__(self):
        """Initialize alert manager"""
        self.audit_logger = AuditLogger()

        # Email configuration
        self.alert_email_enabled = os.getenv('ALERT_EMAIL_ENABLED', 'false').lower() == 'true'
        self.alert_email_to = os.getenv('ALERT_EMAIL_TO', '')
        self.alert_email_from = os.getenv('EMAIL_ADDRESS', '')
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_password = os.getenv('EMAIL_PASSWORD', '')

        # Alert thresholds
        self.error_rate_threshold = float(os.getenv('ALERT_ERROR_RATE_THRESHOLD', '10.0'))
        self.cpu_threshold = float(os.getenv('ALERT_CPU_THRESHOLD', '90.0'))
        self.memory_threshold = float(os.getenv('ALERT_MEMORY_THRESHOLD', '90.0'))
        self.no_iteration_threshold = int(os.getenv('ALERT_NO_ITERATION_SECONDS', '300'))

        # Alert cooldown (don't spam alerts)
        self.alert_cooldown = timedelta(minutes=int(os.getenv('ALERT_COOLDOWN_MINUTES', '30')))
        self.last_alerts = {}

    def check_health_and_alert(self, health_status: Dict[str, Any]):
        """
        Check health status and send alerts if needed

        Args:
            health_status: Health status from HealthMonitor
        """
        alerts = []

        # Check overall status
        if health_status['status'] == 'unhealthy':
            alerts.append({
                'severity': 'critical',
                'title': 'System Unhealthy',
                'message': f"Issues detected: {', '.join(health_status['issues'])}"
            })
        elif health_status['status'] == 'degraded':
            alerts.append({
                'severity': 'warning',
                'title': 'System Degraded',
                'message': f"Issues detected: {', '.join(health_status['issues'])}"
            })

        # Check error rate
        iterations = health_status['iterations']['total']
        errors = health_status['iterations']['error_count']
        if iterations > 0:
            error_rate = (errors / iterations) * 100
            if error_rate > self.error_rate_threshold:
                alerts.append({
                    'severity': 'warning',
                    'title': 'High Error Rate',
                    'message': f"Error rate: {error_rate:.1f}% (threshold: {self.error_rate_threshold}%)"
                })

        # Check CPU usage
        cpu_percent = health_status['system'].get('cpu_percent', 0)
        if cpu_percent > self.cpu_threshold:
            alerts.append({
                'severity': 'warning',
                'title': 'High CPU Usage',
                'message': f"CPU usage: {cpu_percent:.1f}% (threshold: {self.cpu_threshold}%)"
            })

        # Check memory usage
        memory_percent = health_status['system'].get('memory_percent', 0)
        if memory_percent > self.memory_threshold:
            alerts.append({
                'severity': 'warning',
                'title': 'High Memory Usage',
                'message': f"Memory usage: {memory_percent:.1f}% (threshold: {self.memory_threshold}%)"
            })

        # Send alerts
        for alert in alerts:
            self.send_alert(alert, health_status)

    def send_alert(self, alert: Dict[str, Any], health_status: Dict[str, Any]):
        """
        Send an alert notification

        Args:
            alert: Alert details
            health_status: Full health status for context
        """
        alert_key = f"{alert['severity']}_{alert['title']}"

        # Check cooldown
        if alert_key in self.last_alerts:
            time_since_last = datetime.now() - self.last_alerts[alert_key]
            if time_since_last < self.alert_cooldown:
                return  # Skip - in cooldown period

        # Update last alert time
        self.last_alerts[alert_key] = datetime.now()

        # Log alert
        self.audit_logger.log_event(
            event_type='alert_triggered',
            details={
                'severity': alert['severity'],
                'title': alert['title'],
                'message': alert['message']
            },
            severity=alert['severity']
        )

        # Send email if enabled
        if self.alert_email_enabled and self.alert_email_to:
            self.send_email_alert(alert, health_status)

        # Print to console
        severity_prefix = {
            'critical': '[CRITICAL]',
            'warning': '[WARNING]',
            'info': '[INFO]'
        }.get(alert['severity'], '[ALERT]')

        print(f"\n{severity_prefix} {alert['title']}: {alert['message']}")

    def send_email_alert(self, alert: Dict[str, Any], health_status: Dict[str, Any]):
        """
        Send email alert

        Args:
            alert: Alert details
            health_status: Full health status for context
        """
        if not self.alert_email_from or not self.smtp_password:
            return

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[Gold Tier Employee] {alert['title']}"
            msg['From'] = self.alert_email_from
            msg['To'] = self.alert_email_to

            # Create email body
            text_body = self._create_text_alert_body(alert, health_status)
            html_body = self._create_html_alert_body(alert, health_status)

            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.alert_email_from, self.smtp_password)
                server.send_message(msg)

            print(f"[Alert] Email sent to {self.alert_email_to}")

        except Exception as e:
            self.audit_logger.log_event(
                event_type='alert_email_failed',
                details={'error': str(e)},
                severity='error'
            )

    def _create_text_alert_body(self, alert: Dict[str, Any], health_status: Dict[str, Any]) -> str:
        """Create plain text alert email body"""
        return f"""
Gold Tier Autonomous Employee Alert

Severity: {alert['severity'].upper()}
Title: {alert['title']}
Message: {alert['message']}

System Status:
- Overall Status: {health_status['status']}
- Uptime: {health_status['uptime_formatted']}
- Total Iterations: {health_status['iterations']['total']}
- Error Count: {health_status['iterations']['error_count']}
- Tasks Processed: {health_status['tasks']['total_processed']}
- CPU Usage: {health_status['system'].get('cpu_percent', 0):.1f}%
- Memory Usage: {health_status['system'].get('memory_percent', 0):.1f}%

Timestamp: {health_status['timestamp']}

This is an automated alert from your Gold Tier Autonomous Employee system.
"""

    def _create_html_alert_body(self, alert: Dict[str, Any], health_status: Dict[str, Any]) -> str:
        """Create HTML alert email body"""
        severity_color = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }.get(alert['severity'], '#6c757d')

        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .alert-box {{
            background: {severity_color};
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .alert-title {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; }}
        .alert-message {{ font-size: 16px; }}
        .status-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .status-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .status-table td:first-child {{ font-weight: bold; width: 40%; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Gold Tier Autonomous Employee Alert</h2>

        <div class="alert-box">
            <div class="alert-title">{alert['title']}</div>
            <div class="alert-message">{alert['message']}</div>
        </div>

        <h3>System Status</h3>
        <table class="status-table">
            <tr>
                <td>Overall Status</td>
                <td>{health_status['status'].upper()}</td>
            </tr>
            <tr>
                <td>Uptime</td>
                <td>{health_status['uptime_formatted']}</td>
            </tr>
            <tr>
                <td>Total Iterations</td>
                <td>{health_status['iterations']['total']}</td>
            </tr>
            <tr>
                <td>Error Count</td>
                <td>{health_status['iterations']['error_count']}</td>
            </tr>
            <tr>
                <td>Tasks Processed</td>
                <td>{health_status['tasks']['total_processed']}</td>
            </tr>
            <tr>
                <td>CPU Usage</td>
                <td>{health_status['system'].get('cpu_percent', 0):.1f}%</td>
            </tr>
            <tr>
                <td>Memory Usage</td>
                <td>{health_status['system'].get('memory_percent', 0):.1f}%</td>
            </tr>
        </table>

        <div class="footer">
            <p>Timestamp: {health_status['timestamp']}</p>
            <p>This is an automated alert from your Gold Tier Autonomous Employee system.</p>
        </div>
    </div>
</body>
</html>
"""


if __name__ == "__main__":
    # Test alert manager
    alert_manager = AlertManager()

    # Simulate health status
    health_status = {
        'status': 'degraded',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': 3600,
        'uptime_formatted': '1h 0m 0s',
        'iterations': {
            'total': 60,
            'error_count': 8
        },
        'tasks': {
            'total_processed': 45,
            'total_executed': 40
        },
        'system': {
            'cpu_percent': 85.5,
            'memory_percent': 72.3
        },
        'issues': ['High error rate: 13.3%']
    }

    print("Testing alert system...")
    alert_manager.check_health_and_alert(health_status)
    print("\nAlert test complete. Check console output and email (if configured).")
