"""
Kill Switch Safety Test
Tests emergency stop functionality.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import time
from datetime import datetime
from src.kill_switch_simple import KillSwitch


def test_kill_switch_safety():
    """Test kill switch safety mechanisms."""
    print("\n" + "="*70)
    print(" KILL SWITCH SAFETY TEST")
    print("="*70)

    kill_switch = KillSwitch()

    # Test 1: Initial state
    print("\n[TEST 1] Initial State Check")
    if kill_switch.is_active():
        print("  [WARN] Kill switch already active - deactivating for test")
        kill_switch.deactivate()

    print("  [OK] Kill switch is INACTIVE")
    print("  [OK] System can run normally")

    # Test 2: Activation
    print("\n[TEST 2] Emergency Activation")
    kill_switch.activate(reason="Safety test - emergency stop")
    print("  [OK] Kill switch ACTIVATED")

    if kill_switch.is_active():
        print("  [OK] Status verified: ACTIVE")
        print("  [OK] System would halt all operations")
    else:
        print("  [FAIL] Kill switch activation failed!")
        return False

    # Test 3: Check file exists
    print("\n[TEST 3] File-Based Detection")
    stop_file = Path("STOP")
    if stop_file.exists():
        print(f"  [OK] STOP file exists: {stop_file}")
        with open(stop_file, 'r') as f:
            content = f.read()
        print(f"  [OK] File content:\n{content}")
    else:
        print("  [FAIL] STOP file not found!")
        return False

    # Test 4: Simulated operation check
    print("\n[TEST 4] Simulated Operation Check")
    print("  Attempting to run operation with kill switch active...")

    try:
        kill_switch.check_and_raise()
        print("  [FAIL] Operation should have been blocked!")
        return False
    except RuntimeError as e:
        print(f"  [OK] Operation blocked: {e}")

    # Test 5: Deactivation
    print("\n[TEST 5] Deactivation")
    kill_switch.deactivate()
    print("  [OK] Kill switch DEACTIVATED")

    if not kill_switch.is_active():
        print("  [OK] Status verified: INACTIVE")
        print("  [OK] System can resume operations")
    else:
        print("  [FAIL] Kill switch deactivation failed!")
        return False

    # Test 6: Verify file removed
    print("\n[TEST 6] File Cleanup Verification")
    if not stop_file.exists():
        print("  [OK] STOP file removed")
    else:
        print("  [FAIL] STOP file still exists!")
        return False

    # Test 7: Multiple activations
    print("\n[TEST 7] Multiple Activation/Deactivation Cycles")
    for i in range(3):
        kill_switch.activate(reason=f"Test cycle {i+1}")
        if not kill_switch.is_active():
            print(f"  [FAIL] Cycle {i+1} activation failed")
            return False

        kill_switch.deactivate()
        if kill_switch.is_active():
            print(f"  [FAIL] Cycle {i+1} deactivation failed")
            return False

    print("  [OK] All 3 cycles completed successfully")

    # Summary
    print("\n" + "="*70)
    print(" KILL SWITCH SAFETY TEST: PASSED")
    print("="*70)
    print("\nVerified Capabilities:")
    print("  [OK] Emergency activation")
    print("  [OK] File-based detection")
    print("  [OK] Operation blocking")
    print("  [OK] Safe deactivation")
    print("  [OK] File cleanup")
    print("  [OK] Multiple cycles")
    print("\nSafety Status: OPERATIONAL")

    return True


if __name__ == "__main__":
    try:
        success = test_kill_switch_safety()
        if success:
            print("\n[SUCCESS] Kill switch safety test completed")
            sys.exit(0)
        else:
            print("\n[FAIL] Kill switch safety test failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
