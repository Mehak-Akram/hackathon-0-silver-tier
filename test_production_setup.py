"""
Production Setup Test Suite
Validates all components are working correctly
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent))

def print_header(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def print_test(name):
    print(f"\n[TEST] {name}...", end=" ")

def print_pass():
    print("✓ PASS")

def print_fail(reason):
    print(f"✗ FAIL: {reason}")

def print_skip(reason):
    print(f"⊘ SKIP: {reason}")

class ProductionTester:
    """Tests production configuration"""

    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'tests': []
        }

    def test_odoo_connection(self):
        """Test Odoo CRM connection"""
        print_test("Odoo Connection")

        url = os.getenv('ODOO_URL')
        db = os.getenv('ODOO_DB')
        username = os.getenv('ODOO_USERNAME')
        password = os.getenv('ODOO_PASSWORD')

        if not all([url, db, username, password]):
            print_skip("Odoo credentials not configured")
            self.results['skipped'] += 1
            return False

        try:
            from src.odoo_client import OdooClient
            client = OdooClient()
            client.authenticate()
            print_pass()
            print(f"      Connected to: {url}")
            print(f"      Database: {db}")
            print(f"      User ID: {client.uid}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_odoo_create_customer(self):
        """Test creating customer in Odoo"""
        print_test("Odoo Create Customer")

        try:
            from src.odoo_client import OdooClient
            client = OdooClient()
            client.authenticate()

            # Create test customer
            customer_id = client.create_customer(
                name=f"Test Customer {datetime.now().strftime('%Y%m%d%H%M%S')}",
                email=f"test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                phone="555-0100"
            )

            print_pass()
            print(f"      Customer ID: {customer_id}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_odoo_create_lead(self):
        """Test creating lead in Odoo"""
        print_test("Odoo Create Lead")

        try:
            from src.odoo_client import OdooClient
            client = OdooClient()
            client.authenticate()

            # Create test lead
            lead_id = client.create_lead(
                name=f"Test Lead {datetime.now().strftime('%Y%m%d%H%M%S')}",
                contact_name="Test Contact",
                email=f"lead{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                phone="555-0200",
                description="Test lead created by production test suite"
            )

            print_pass()
            print(f"      Lead ID: {lead_id}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_email_imap(self):
        """Test IMAP email connection"""
        print_test("Email IMAP Connection")

        email = os.getenv('EMAIL_ADDRESS')
        password = os.getenv('EMAIL_PASSWORD')

        if not email or not password:
            print_skip("Email credentials not configured")
            self.results['skipped'] += 1
            return False

        try:
            import imaplib
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email, password)
            status, messages = mail.select('INBOX')
            mail.logout()

            print_pass()
            print(f"      Email: {email}")
            print(f"      Inbox messages: {messages[0].decode()}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            print(f"      Hint: Use Gmail App Password, not regular password")
            self.results['failed'] += 1
            return False

    def test_email_smtp(self):
        """Test SMTP email connection"""
        print_test("Email SMTP Connection")

        email = os.getenv('EMAIL_ADDRESS')
        password = os.getenv('EMAIL_PASSWORD')

        if not email or not password:
            print_skip("Email credentials not configured")
            self.results['skipped'] += 1
            return False

        try:
            import smtplib
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()

            print_pass()
            print(f"      Email: {email}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            print(f"      Hint: Use Gmail App Password, not regular password")
            self.results['failed'] += 1
            return False

    def test_health_monitor(self):
        """Test health monitoring system"""
        print_test("Health Monitor")

        try:
            from deployment.health_monitor import HealthMonitor
            monitor = HealthMonitor()

            # Simulate activity
            monitor.update_iteration({
                'inbox_processed': 5,
                'needs_action_processed': 3,
                'emails_checked': 2,
                'social_mentions_checked': 1,
                'errors': 0
            })

            health = monitor.get_health_status()

            print_pass()
            print(f"      Status: {health['status']}")
            print(f"      Uptime: {health['uptime_formatted']}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_metrics_aggregation(self):
        """Test metrics aggregation"""
        print_test("Metrics Aggregation")

        try:
            from reporting.metrics_aggregator import MetricsAggregator
            aggregator = MetricsAggregator()

            metrics = aggregator.get_weekly_metrics()

            print_pass()
            print(f"      Tasks executed: {metrics['tasks']['total_executed']}")
            print(f"      Customers created: {metrics['odoo']['customers_created']}")
            print(f"      Emails processed: {metrics['email']['emails_received']}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_ceo_briefing_generation(self):
        """Test CEO briefing generation"""
        print_test("CEO Briefing Generation")

        try:
            from reporting.ceo_briefing_generator import CEOBriefingGenerator
            generator = CEOBriefingGenerator()

            result = generator.generate_weekly_briefing()

            print_pass()
            print(f"      HTML: {result['html_path']}")
            print(f"      Text: {result['text_path']}")
            print(f"      JSON: {result['json_path']}")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_audit_logging(self):
        """Test audit logging"""
        print_test("Audit Logging")

        try:
            from src.audit_logger_simple import AuditLogger
            logger = AuditLogger()

            logger.log_event(
                event_type='production_test',
                details={'test': 'audit_logging'},
                severity='info'
            )

            print_pass()
            print(f"      Log directory: Audit_Logs/")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def test_task_processing(self):
        """Test task processing"""
        print_test("Task Processing")

        try:
            # Create test task
            inbox_path = Path('./Inbox')
            inbox_path.mkdir(parents=True, exist_ok=True)

            task = {
                'type': 'test',
                'classified_type': 'general',
                'content': 'Production test task',
                'timestamp': datetime.now().isoformat()
            }

            task_file = inbox_path / f"test_task_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            task_file.write_text(json.dumps(task, indent=2))

            print_pass()
            print(f"      Test task created: {task_file.name}")
            print(f"      Will be processed by autonomous loop")
            self.results['passed'] += 1
            return True
        except Exception as e:
            print_fail(str(e))
            self.results['failed'] += 1
            return False

    def run_all_tests(self):
        """Run all production tests"""
        print_header("PRODUCTION SETUP TEST SUITE")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Core tests
        print("\n" + "-"*60)
        print("CORE SYSTEM TESTS")
        print("-"*60)
        self.test_audit_logging()
        self.test_health_monitor()
        self.test_metrics_aggregation()

        # Odoo tests
        print("\n" + "-"*60)
        print("ODOO CRM TESTS")
        print("-"*60)
        self.test_odoo_connection()
        if self.results['tests'] and self.results['tests'][-1]:
            self.test_odoo_create_customer()
            self.test_odoo_create_lead()

        # Email tests
        print("\n" + "-"*60)
        print("EMAIL INTEGRATION TESTS")
        print("-"*60)
        self.test_email_imap()
        self.test_email_smtp()

        # Reporting tests
        print("\n" + "-"*60)
        print("REPORTING TESTS")
        print("-"*60)
        self.test_ceo_briefing_generation()

        # Task processing
        print("\n" + "-"*60)
        print("TASK PROCESSING TESTS")
        print("-"*60)
        self.test_task_processing()

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Passed:  {self.results['passed']}")
        print(f"Failed:  {self.results['failed']}")
        print(f"Skipped: {self.results['skipped']}")
        print(f"Total:   {self.results['passed'] + self.results['failed'] + self.results['skipped']}")

        if self.results['failed'] == 0:
            print("\n✓ ALL TESTS PASSED!")
            print("\nYour system is ready for production!")
            print("\nNext steps:")
            print("  1. Start autonomous loop: start_autonomous_loop.bat")
            print("  2. Access dashboard: http://localhost:8080/")
            print("  3. Send test email to verify end-to-end workflow")
        else:
            print("\n✗ SOME TESTS FAILED")
            print("\nPlease fix the failed tests before deploying to production.")
            print("Common issues:")
            print("  - Email: Use Gmail App Password, not regular password")
            print("  - Odoo: Verify credentials and database name")
            print("  - Network: Check firewall and internet connection")

        print("\n" + "="*60)


def main():
    """Main entry point"""
    tester = ProductionTester()
    tester.run_all_tests()

    # Return exit code
    sys.exit(0 if tester.results['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
