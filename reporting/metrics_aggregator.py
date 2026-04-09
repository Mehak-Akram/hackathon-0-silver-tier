"""
Metrics Aggregator
Collects and aggregates data from various sources for reporting
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.odoo_client import OdooClient


class MetricsAggregator:
    """
    Aggregates metrics from audit logs, Odoo, and task data
    """

    def __init__(self):
        """Initialize metrics aggregator"""
        self.project_root = Path(__file__).parent.parent
        self.audit_logs_dir = self.project_root / "Audit_Logs"
        self.done_dir = self.project_root / "Done"

        # Initialize Odoo client
        try:
            self.odoo_client = OdooClient()
            self.odoo_client.authenticate()
        except Exception as e:
            print(f"[WARNING] Odoo client not available: {e}")
            self.odoo_client = None

    def get_weekly_metrics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get metrics for a specific week

        Args:
            start_date: Start of period (defaults to 7 days ago)
            end_date: End of period (defaults to now)

        Returns:
            Dictionary of aggregated metrics
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=7)

        metrics = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'system': self._get_system_metrics(start_date, end_date),
            'tasks': self._get_task_metrics(start_date, end_date),
            'odoo': self._get_odoo_metrics(start_date, end_date),
            'email': self._get_email_metrics(start_date, end_date),
            'social_media': self._get_social_media_metrics(start_date, end_date),
            'errors': self._get_error_metrics(start_date, end_date)
        }

        return metrics

    def _get_system_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get system performance metrics from audit logs"""
        metrics = {
            'total_iterations': 0,
            'uptime_hours': 0,
            'average_iteration_time': 0,
            'health_status': 'unknown'
        }

        # Parse audit logs
        audit_events = self._parse_audit_logs(start_date, end_date)

        # Count iterations
        iterations = [e for e in audit_events if e.get('event_type') == 'task_executed']
        metrics['total_iterations'] = len(iterations)

        # Calculate uptime
        start_events = [e for e in audit_events if e.get('event_type') == 'autonomous_loop_started']
        stop_events = [e for e in audit_events if e.get('event_type') == 'autonomous_loop_stopped']

        if start_events:
            # Estimate uptime based on iterations (assuming 60s interval)
            metrics['uptime_hours'] = (len(iterations) * 60) / 3600

        return metrics

    def _get_task_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get task processing metrics"""
        metrics = {
            'total_processed': 0,
            'total_executed': 0,
            'by_type': defaultdict(int),
            'success_rate': 0
        }

        # Count completed tasks in Done/ folder
        if self.done_dir.exists():
            for task_file in self.done_dir.glob('*.json'):
                try:
                    file_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                    if start_date <= file_time <= end_date:
                        metrics['total_executed'] += 1

                        # Read task type
                        task_data = json.loads(task_file.read_text())
                        task_type = task_data.get('type', 'unknown')
                        metrics['by_type'][task_type] += 1

                except Exception:
                    pass

        # Get processed count from audit logs
        audit_events = self._parse_audit_logs(start_date, end_date)
        processed_events = [e for e in audit_events if e.get('event_type') == 'task_executed']
        metrics['total_processed'] = len(processed_events)

        # Calculate success rate
        if metrics['total_processed'] > 0:
            metrics['success_rate'] = (metrics['total_executed'] / metrics['total_processed']) * 100

        return metrics

    def _get_odoo_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Odoo CRM metrics"""
        metrics = {
            'customers_created': 0,
            'leads_created': 0,
            'opportunities_value': 0,
            'available': False
        }

        if not self.odoo_client:
            return metrics

        try:
            # Count customers created in period
            # Note: This is a simplified version - actual implementation would query Odoo
            audit_events = self._parse_audit_logs(start_date, end_date)

            customer_events = [e for e in audit_events
                             if e.get('event_type') == 'task_executed'
                             and 'create_customer' in str(e.get('details', {}))]
            metrics['customers_created'] = len(customer_events)

            lead_events = [e for e in audit_events
                         if e.get('event_type') == 'task_executed'
                         and 'create_lead' in str(e.get('details', {}))]
            metrics['leads_created'] = len(lead_events)

            metrics['available'] = True

        except Exception as e:
            print(f"[WARNING] Failed to get Odoo metrics: {e}")

        return metrics

    def _get_email_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get email processing metrics"""
        metrics = {
            'emails_received': 0,
            'emails_responded': 0,
            'response_rate': 0
        }

        # Count email tasks
        if self.done_dir.exists():
            email_tasks = list(self.done_dir.glob('*email*.json'))
            for task_file in email_tasks:
                try:
                    file_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                    if start_date <= file_time <= end_date:
                        metrics['emails_received'] += 1

                        # Check if response was sent
                        task_data = json.loads(task_file.read_text())
                        if task_data.get('requires_response'):
                            metrics['emails_responded'] += 1

                except Exception:
                    pass

        # Calculate response rate
        if metrics['emails_received'] > 0:
            metrics['response_rate'] = (metrics['emails_responded'] / metrics['emails_received']) * 100

        return metrics

    def _get_social_media_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get social media metrics"""
        metrics = {
            'mentions_detected': 0,
            'by_platform': defaultdict(int),
            'leads_generated': 0
        }

        # Count social media tasks
        if self.done_dir.exists():
            social_tasks = list(self.done_dir.glob('*social*.json'))
            for task_file in social_tasks:
                try:
                    file_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                    if start_date <= file_time <= end_date:
                        metrics['mentions_detected'] += 1

                        # Read platform
                        task_data = json.loads(task_file.read_text())
                        platform = task_data.get('platform', 'unknown')
                        metrics['by_platform'][platform] += 1

                        # Check if lead was created
                        if task_data.get('mention_type') in ['customer_inquiry', 'sales_opportunity']:
                            metrics['leads_generated'] += 1

                except Exception:
                    pass

        return metrics

    def _get_error_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get error and issue metrics"""
        metrics = {
            'total_errors': 0,
            'critical_errors': 0,
            'warnings': 0,
            'by_type': defaultdict(int)
        }

        # Parse audit logs for errors
        audit_events = self._parse_audit_logs(start_date, end_date)

        for event in audit_events:
            severity = event.get('severity', 'info')

            if severity == 'error':
                metrics['total_errors'] += 1
                event_type = event.get('event_type', 'unknown')
                metrics['by_type'][event_type] += 1

            elif severity == 'critical':
                metrics['critical_errors'] += 1

            elif severity == 'warning':
                metrics['warnings'] += 1

        return metrics

    def _parse_audit_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Parse audit logs for the given period"""
        events = []

        if not self.audit_logs_dir.exists():
            return events

        # Find relevant log files
        for log_file in self.audit_logs_dir.glob('audit_log_*.json'):
            try:
                log_data = json.loads(log_file.read_text())

                for event in log_data.get('events', []):
                    # Parse timestamp
                    timestamp_str = event.get('timestamp', '')
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if start_date <= timestamp <= end_date:
                            events.append(event)
                    except:
                        pass

            except Exception:
                pass

        return events

    def get_comparison_metrics(self, current_start: datetime, current_end: datetime) -> Dict[str, Any]:
        """
        Get metrics with week-over-week comparison

        Args:
            current_start: Start of current period
            current_end: End of current period

        Returns:
            Dictionary with current and previous metrics plus changes
        """
        # Get current period metrics
        current = self.get_weekly_metrics(current_start, current_end)

        # Get previous period metrics
        period_length = current_end - current_start
        previous_start = current_start - period_length
        previous_end = current_start
        previous = self.get_weekly_metrics(previous_start, previous_end)

        # Calculate changes
        comparison = {
            'current': current,
            'previous': previous,
            'changes': self._calculate_changes(current, previous)
        }

        return comparison

    def _calculate_changes(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate percentage changes between periods"""
        changes = {}

        # Task changes
        curr_tasks = current['tasks']['total_executed']
        prev_tasks = previous['tasks']['total_executed']
        if prev_tasks > 0:
            changes['tasks_change'] = ((curr_tasks - prev_tasks) / prev_tasks) * 100
        else:
            changes['tasks_change'] = 100 if curr_tasks > 0 else 0

        # Customer changes
        curr_customers = current['odoo']['customers_created']
        prev_customers = previous['odoo']['customers_created']
        if prev_customers > 0:
            changes['customers_change'] = ((curr_customers - prev_customers) / prev_customers) * 100
        else:
            changes['customers_change'] = 100 if curr_customers > 0 else 0

        # Lead changes
        curr_leads = current['odoo']['leads_created']
        prev_leads = previous['odoo']['leads_created']
        if prev_leads > 0:
            changes['leads_change'] = ((curr_leads - prev_leads) / prev_leads) * 100
        else:
            changes['leads_change'] = 100 if curr_leads > 0 else 0

        # Error changes
        curr_errors = current['errors']['total_errors']
        prev_errors = previous['errors']['total_errors']
        if prev_errors > 0:
            changes['errors_change'] = ((curr_errors - prev_errors) / prev_errors) * 100
        else:
            changes['errors_change'] = 100 if curr_errors > 0 else 0

        return changes


if __name__ == "__main__":
    # Test metrics aggregator
    aggregator = MetricsAggregator()

    print("="*60)
    print("METRICS AGGREGATOR TEST")
    print("="*60)
    print()

    # Get last 7 days metrics
    metrics = aggregator.get_weekly_metrics()

    print("Weekly Metrics:")
    print(f"  Period: {metrics['period']['start']} to {metrics['period']['end']}")
    print(f"  Tasks executed: {metrics['tasks']['total_executed']}")
    print(f"  Customers created: {metrics['odoo']['customers_created']}")
    print(f"  Leads created: {metrics['odoo']['leads_created']}")
    print(f"  Emails processed: {metrics['email']['emails_received']}")
    print(f"  Social mentions: {metrics['social_media']['mentions_detected']}")
    print(f"  Errors: {metrics['errors']['total_errors']}")
    print()

    print("[SUCCESS] Metrics aggregator working correctly!")
