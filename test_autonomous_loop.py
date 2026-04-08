"""
Test Autonomous Loop
Verifies the autonomous task processing system works end-to-end
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from orchestrator.task_processor import TaskProcessor
from orchestrator.decision_engine import DecisionEngine
from orchestrator.autonomous_loop import AutonomousLoop


def create_sample_tasks():
    """Create sample tasks for testing"""
    inbox = Path('./Inbox')
    inbox.mkdir(parents=True, exist_ok=True)

    # Sample 1: Odoo customer creation
    task1 = {
        "type": "odoo",
        "classified_type": "odoo",
        "content": "Create customer John Smith with email john@example.com",
        "customer_name": "John Smith",
        "customer_email": "john@example.com",
        "customer_phone": "+1234567890",
        "timestamp": datetime.now().isoformat()
    }

    # Sample 2: Odoo lead creation
    task2 = {
        "type": "odoo",
        "classified_type": "odoo",
        "content": "Create lead for Product Demo Request",
        "lead_title": "Product Demo Request",
        "customer_email": "demo@example.com",
        "description": "Customer interested in product demo via website form",
        "timestamp": datetime.now().isoformat()
    }

    # Sample 3: General task
    task3 = {
        "type": "general",
        "content": "Log this general task for review",
        "timestamp": datetime.now().isoformat()
    }

    # Write tasks
    (inbox / 'task1_create_customer.json').write_text(json.dumps(task1, indent=2))
    (inbox / 'task2_create_lead.json').write_text(json.dumps(task2, indent=2))
    (inbox / 'task3_general.json').write_text(json.dumps(task3, indent=2))

    print("[OK] Created 3 sample tasks in Inbox/")


def test_task_processor():
    """Test task processor"""
    print("\n" + "="*60)
    print("TEST 1: Task Processor")
    print("="*60)

    processor = TaskProcessor()

    # Scan inbox
    tasks = processor.scan_inbox()
    print(f"[OK] Found {len(tasks)} tasks in Inbox")

    if len(tasks) == 0:
        print("[INFO] No tasks to process - creating samples")
        create_sample_tasks()
        tasks = processor.scan_inbox()

    # Process tasks
    results = processor.process_all_tasks()
    print(f"[OK] Processed {len(results)} tasks")

    for result in results:
        if result.get('success'):
            print(f"  [OK] {result['task']['file_name']} -> {result['destination']}")
        else:
            print(f"  [FAIL] {result.get('file', 'unknown')} - {result.get('error')}")

    return len([r for r in results if r.get('success')]) > 0


def test_decision_engine():
    """Test decision engine"""
    print("\n" + "="*60)
    print("TEST 2: Decision Engine")
    print("="*60)

    engine = DecisionEngine()

    # Test Odoo action
    test_task = {
        "classified_type": "odoo",
        "content": "create customer Test User",
        "customer_name": "Test User",
        "customer_email": "test@example.com"
    }

    plan = engine.analyze_task(test_task)
    print(f"[OK] Created execution plan with {len(plan['actions'])} actions")

    result = engine.execute_plan(plan)
    print(f"[OK] Execution result: {result.get('success')}")

    return result.get('success', False)


def test_single_iteration():
    """Test single iteration of autonomous loop"""
    print("\n" + "="*60)
    print("TEST 3: Single Loop Iteration")
    print("="*60)

    loop = AutonomousLoop()

    # Run one iteration
    stats = loop.run_iteration()

    print(f"[OK] Iteration completed:")
    print(f"  • Inbox processed: {stats['inbox_processed']}")
    print(f"  • Needs_Action processed: {stats['needs_action_processed']}")
    print(f"  • Errors: {stats['errors']}")
    print(f"  • Duration: {stats['duration_seconds']:.2f}s")

    return stats['errors'] == 0


def main():
    """Run all tests"""
    print("="*60)
    print("AUTONOMOUS LOOP TEST SUITE")
    print("="*60)

    # Ensure sample tasks exist
    create_sample_tasks()

    # Run tests
    test1_passed = test_task_processor()
    test2_passed = test_decision_engine()
    test3_passed = test_single_iteration()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Task Processor:    {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"Decision Engine:   {'[PASS]' if test2_passed else '[FAIL]'}")
    print(f"Loop Iteration:    {'[PASS]' if test3_passed else '[FAIL]'}")

    all_passed = test1_passed and test2_passed and test3_passed

    if all_passed:
        print("\n[OK] ALL TESTS PASSED")
        print("\nNext steps:")
        print("1. Enable autonomous mode: Set ENABLE_AUTONOMOUS_LOOP=true in .env")
        print("2. Run: python orchestrator/autonomous_loop.py")
        print("3. Drop tasks in Inbox/ folder")
        print("4. Watch them get processed automatically!")
    else:
        print("\n[FAIL] SOME TESTS FAILED")
        print("Check the errors above and fix issues before running autonomous mode")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
