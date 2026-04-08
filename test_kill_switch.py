"""
Kill Switch Test - Demonstrate emergency stop mechanism
"""
import time
from pathlib import Path

VAULT_PATH = Path("E:/AI_Employee_Vault")
KILL_SWITCH_FILE = VAULT_PATH / "STOP"

def check_kill_switch():
    """Check if kill switch is activated."""
    return KILL_SWITCH_FILE.exists()

def simulate_autonomous_loop():
    """Simulate the autonomous loop with kill switch monitoring."""

    print("=" * 80)
    print("KILL SWITCH TEST - AUTONOMOUS LOOP SIMULATION")
    print("=" * 80)
    print()

    print("Starting autonomous loop...")
    print("The system will check for STOP file before each operation")
    print()

    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        iteration += 1

        # CHECK KILL SWITCH BEFORE EACH OPERATION
        if check_kill_switch():
            print()
            print("!" * 80)
            print("KILL SWITCH ACTIVATED - STOP FILE DETECTED")
            print("!" * 80)
            print()
            print("System is shutting down gracefully...")
            print("  - Completing current operation")
            print("  - Saving state")
            print("  - Closing connections")
            print("  - System halted")
            print()
            print("To restart: Remove STOP file and restart the system")
            return "STOPPED_BY_KILL_SWITCH"

        # Simulate work
        print(f"[Iteration {iteration}] Autonomous loop running...")
        print(f"  - Checking for new tasks")
        print(f"  - Monitoring scheduled operations")
        print(f"  - System healthy")

        if iteration == 3:
            print()
            print(">>> SIMULATING KILL SWITCH ACTIVATION <<<")
            print(">>> Creating STOP file... <<<")
            print()
            KILL_SWITCH_FILE.touch()

        time.sleep(0.5)

    print()
    print("Autonomous loop completed normally")
    return "COMPLETED"

# Run simulation
result = simulate_autonomous_loop()

print()
print("=" * 80)
print(f"KILL SWITCH TEST RESULT: {result}")
print("=" * 80)
print()

# Clean up
if KILL_SWITCH_FILE.exists():
    print("Cleaning up: Removing STOP file")
    KILL_SWITCH_FILE.unlink()
    print("[OK] STOP file removed - system ready to restart")
else:
    print("No STOP file found - system ready to run")

print()
