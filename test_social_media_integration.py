"""
Test Social Media Integration
Tests the social media monitoring and response workflow
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from orchestrator.social_media_monitor import SocialMediaMonitor
from orchestrator.decision_engine import DecisionEngine
from src.audit_logger_simple import AuditLogger


def test_social_media_monitoring():
    """Test social media monitoring"""
    print("="*60)
    print("TEST 1: Social Media Monitoring")
    print("="*60)

    monitor = SocialMediaMonitor()

    print("\n[INFO] Checking all platforms...")
    count = monitor.check_all_platforms()

    print(f"\n[OK] Checked social media platforms")
    print(f"Tasks created: {count}")

    return True


def test_mention_classification():
    """Test mention classification"""
    print("\n" + "="*60)
    print("TEST 2: Mention Classification")
    print("="*60)

    monitor = SocialMediaMonitor()

    test_mentions = [
        {
            'message': 'What is your pricing for the enterprise plan?',
            'expected': 'customer_inquiry'
        },
        {
            'message': 'I love your product! Amazing work!',
            'expected': 'positive_engagement'
        },
        {
            'message': 'Interested in a demo of your service',
            'expected': 'sales_opportunity'
        },
        {
            'message': 'Just checking out your page',
            'expected': 'general_mention'
        }
    ]

    all_passed = True

    for test in test_mentions:
        mention = {'message': test['message']}
        result = monitor.classify_mention(mention)

        status = "[OK]" if result == test['expected'] else "[FAIL]"
        print(f"{status} '{test['message'][:40]}...' -> {result}")

        if result != test['expected']:
            all_passed = False

    return all_passed


def test_social_media_task_planning():
    """Test social media task planning"""
    print("\n" + "="*60)
    print("TEST 3: Social Media Task Planning")
    print("="*60)

    engine = DecisionEngine()

    # Create social media mention task
    task = {
        'type': 'social_media_mention',
        'classified_type': 'social_media',
        'platform': 'facebook',
        'content': 'Social media mention from customer on facebook',
        'mention_id': 'fb_test_123',
        'mention_type': 'customer_inquiry',
        'from_user': 'Test Customer',
        'from_user_id': 'fb_user_test',
        'message': 'Can you tell me more about your pricing?',
        'post_id': 'fb_post_test',
        'requires_response': True
    }

    # Analyze task
    plan = engine.analyze_task(task)

    print(f"\n[OK] Created execution plan")
    print(f"Task type: {plan['task_type']}")
    print(f"Number of actions: {len(plan['actions'])}")
    print(f"Risk level: {plan['estimated_risk']}")

    if len(plan['actions']) > 0:
        print("\nPlanned actions:")
        for i, action in enumerate(plan['actions'], 1):
            print(f"  {i}. {action['type']}: {action.get('action', action.get('tool', 'N/A'))}")

    return True


def test_create_sample_social_task():
    """Create a sample social media task file for testing"""
    print("\n" + "="*60)
    print("TEST 4: Create Sample Social Media Task")
    print("="*60)

    inbox_path = Path('./Inbox')
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Create sample task
    task = {
        'type': 'social_media_mention',
        'classified_type': 'social_media',
        'platform': 'facebook',
        'content': 'Social media mention from sample customer on facebook',
        'mention_id': 'fb_sample_123',
        'mention_type': 'customer_inquiry',
        'from_user': 'Sample Customer',
        'from_user_id': 'fb_user_sample',
        'message': 'Hi! I saw your post and I am interested in learning more about your services.',
        'post_id': 'fb_post_sample',
        'timestamp': datetime.now().isoformat(),
        'requires_response': True
    }

    # Write task file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"sample_social_mention_{timestamp}.json"
    task_path = inbox_path / filename

    task_path.write_text(json.dumps(task, indent=2))

    print(f"\n[OK] Created sample task: {filename}")
    print(f"Location: {task_path}")
    print("\n[INFO] This task will be processed by the autonomous loop")
    print("[INFO] It will create a lead in Odoo for follow-up")

    return True


def test_platform_configuration():
    """Test platform configuration"""
    print("\n" + "="*60)
    print("TEST 5: Platform Configuration")
    print("="*60)

    monitor = SocialMediaMonitor()

    print("\nPlatform Status:")
    for platform, config in monitor.platforms.items():
        status = "[ENABLED]" if config['enabled'] else "[DISABLED]"
        print(f"  {status} {platform.capitalize()}")

    print("\n[INFO] Enable platforms in .env:")
    print("  FACEBOOK_MONITORING_ENABLED=true")
    print("  TWITTER_MONITORING_ENABLED=true")
    print("  INSTAGRAM_MONITORING_ENABLED=true")

    return True


def main():
    """Run all tests"""
    print("="*60)
    print("SOCIAL MEDIA INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        ("Social Media Monitoring", test_social_media_monitoring),
        ("Mention Classification", test_mention_classification),
        ("Social Media Task Planning", test_social_media_task_planning),
        ("Create Sample Task", test_create_sample_social_task),
        ("Platform Configuration", test_platform_configuration)
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
        print("1. Configure social media credentials in .env")
        print("2. Enable monitoring: FACEBOOK_MONITORING_ENABLED=true")
        print("3. Start autonomous loop: python orchestrator/autonomous_loop.py")
        print("4. System will automatically monitor social media and create tasks")
    else:
        print("\n[WARNING] Some tests failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
