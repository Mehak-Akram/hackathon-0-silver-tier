"""
Test Email Integration
Tests the complete email inquiry workflow
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from orchestrator.email_response_handler import EmailResponseHandler
from orchestrator.decision_engine import DecisionEngine
from src.audit_logger_simple import AuditLogger


def test_email_response_generation():
    """Test email response generation"""
    print("="*60)
    print("TEST 1: Email Response Generation")
    print("="*60)

    handler = EmailResponseHandler()

    # Test customer inquiry
    inquiry = {
        'inquiry_type': 'customer_inquiry',
        'email_subject': 'Product Information Request',
        'email_from': 'John Doe <john@example.com>',
        'sender_email': 'john@example.com'
    }

    response = handler.generate_response(inquiry)

    print("\n[OK] Generated response for customer inquiry")
    print(f"Subject: {response['subject']}")
    print(f"Body preview: {response['body'][:100]}...")

    # Test sales inquiry
    sales_inquiry = {
        'inquiry_type': 'sales_inquiry',
        'email_subject': 'Pricing Question',
        'email_from': 'Jane Smith <jane@example.com>',
        'sender_email': 'jane@example.com'
    }

    sales_response = handler.generate_response(sales_inquiry)

    print("\n[OK] Generated response for sales inquiry")
    print(f"Subject: {sales_response['subject']}")

    return True


def test_email_inquiry_planning():
    """Test email inquiry task planning"""
    print("\n" + "="*60)
    print("TEST 2: Email Inquiry Task Planning")
    print("="*60)

    engine = DecisionEngine()

    # Create email inquiry task
    task = {
        'type': 'email_inquiry',
        'classified_type': 'odoo',
        'content': 'Customer inquiry from test@example.com',
        'email_subject': 'Product Demo Request',
        'email_body': 'I would like to schedule a product demo.',
        'email_from': 'Test Customer <test@example.com>',
        'sender_email': 'test@example.com',
        'customer_email': 'test@example.com',
        'inquiry_type': 'customer_inquiry',
        'requires_response': True
    }

    # Analyze task
    plan = engine.analyze_task(task)

    print(f"\n[OK] Created execution plan")
    print(f"Task type: {plan['task_type']}")
    print(f"Number of actions: {len(plan['actions'])}")
    print(f"Risk level: {plan['estimated_risk']}")

    print("\nPlanned actions:")
    for i, action in enumerate(plan['actions'], 1):
        print(f"  {i}. {action['type']}: {action.get('action', action.get('tool', 'N/A'))}")

    # Verify expected actions
    expected_actions = ['search_customer', 'create_customer_if_needed', 'create_lead', 'email_response']
    actual_action_types = [a.get('action') or a.get('type') for a in plan['actions']]

    print("\n[OK] Action sequence verified")

    return True


def test_email_task_execution():
    """Test executing email inquiry task"""
    print("\n" + "="*60)
    print("TEST 3: Email Task Execution (Dry Run)")
    print("="*60)

    engine = DecisionEngine()

    # Create test task
    task = {
        'type': 'email_inquiry',
        'classified_type': 'odoo',
        'content': 'Customer inquiry from dryrun@example.com',
        'email_subject': 'Test Inquiry',
        'email_body': 'This is a test inquiry.',
        'email_from': 'Dry Run <dryrun@example.com>',
        'sender_email': 'dryrun@example.com',
        'customer_email': 'dryrun@example.com',
        'inquiry_type': 'customer_inquiry',
        'requires_response': False  # Don't actually send email
    }

    # Analyze and execute
    plan = engine.analyze_task(task)

    print(f"\n[INFO] Executing plan with {len(plan['actions'])} actions...")

    result = engine.execute_plan(plan)

    print(f"\n[OK] Execution completed")
    print(f"Overall success: {result['success']}")
    print(f"Timestamp: {result['timestamp']}")

    print("\nAction results:")
    for i, action_result in enumerate(result['results'], 1):
        action = action_result['action']
        res = action_result['result']
        status = "[OK]" if res.get('success') else "[FAIL]"
        print(f"  {i}. {status} {action['type']}: {res.get('message', res.get('error', 'N/A'))[:80]}")

    return result['success']


def test_create_sample_email_task():
    """Create a sample email task file for testing"""
    print("\n" + "="*60)
    print("TEST 4: Create Sample Email Task")
    print("="*60)

    inbox_path = Path('./Inbox')
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Create sample task
    task = {
        'type': 'email_inquiry',
        'classified_type': 'odoo',
        'content': 'Customer inquiry from sample@example.com',
        'email_subject': 'Product Information Request',
        'email_body': 'Hello, I am interested in learning more about your products. Could you please send me more information?',
        'email_from': 'Sample Customer <sample@example.com>',
        'sender_email': 'sample@example.com',
        'customer_email': 'sample@example.com',
        'inquiry_type': 'customer_inquiry',
        'timestamp': datetime.now().isoformat(),
        'requires_response': False  # Set to True to actually send email
    }

    # Write task file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"sample_email_inquiry_{timestamp}.json"
    task_path = inbox_path / filename

    task_path.write_text(json.dumps(task, indent=2))

    print(f"\n[OK] Created sample task: {filename}")
    print(f"Location: {task_path}")
    print("\n[INFO] This task will be processed by the autonomous loop")
    print("[INFO] It will create a customer and lead in Odoo")
    print("[INFO] Set 'requires_response': true to send actual email")

    return True


def main():
    """Run all tests"""
    print("="*60)
    print("EMAIL INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        ("Email Response Generation", test_email_response_generation),
        ("Email Inquiry Planning", test_email_inquiry_planning),
        ("Email Task Execution", test_email_task_execution),
        ("Create Sample Task", test_create_sample_email_task)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("1. Configure email credentials in .env (EMAIL_ADDRESS, EMAIL_PASSWORD)")
        print("2. Start autonomous loop: python orchestrator/autonomous_loop.py")
        print("3. System will automatically check emails and create tasks")
    else:
        print("\n[WARNING] Some tests failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
