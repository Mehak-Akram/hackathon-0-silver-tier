"""
Autonomous Loop (Ralph Wiggum Pattern)
Continuously monitors and processes tasks autonomously
"""

import os
import time
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from orchestrator.task_processor import TaskProcessor
from orchestrator.decision_engine import DecisionEngine
from orchestrator.email_monitor import EmailMonitor
from orchestrator.social_media_monitor import SocialMediaMonitor
from src.audit_logger_simple import AuditLogger
from src.kill_switch_simple import KillSwitch

# Import health monitoring (optional)
try:
    from deployment.health_monitor import HealthMonitor, HealthCheckServer
    from deployment.alert_manager import AlertManager
    HEALTH_MONITOR_AVAILABLE = True
except ImportError:
    HEALTH_MONITOR_AVAILABLE = False


class AutonomousLoop:
    """
    Main autonomous loop that monitors and executes tasks

    Named after Ralph Wiggum's famous quote: "I'm helping!"
    This loop continuously helps by processing tasks autonomously.
    """

    def __init__(self):
        """Initialize autonomous loop"""
        self.enabled = os.getenv('ENABLE_AUTONOMOUS_LOOP', 'false').lower() == 'true'
        self.loop_interval = int(os.getenv('LOOP_INTERVAL_SECONDS', '60'))
        self.running = False

        # Initialize components
        self.task_processor = TaskProcessor()
        self.decision_engine = DecisionEngine()
        self.audit_logger = AuditLogger()
        self.kill_switch = KillSwitch()

        # Initialize email monitor (optional - only if credentials configured)
        try:
            self.email_monitor = EmailMonitor()
        except Exception as e:
            self.audit_logger.log_event(
                event_type='email_monitor_init_error',
                details={'error': str(e)},
                severity='warning'
            )
            self.email_monitor = None

        # Initialize social media monitor (optional - only if credentials configured)
        try:
            self.social_media_monitor = SocialMediaMonitor()
        except Exception as e:
            self.audit_logger.log_event(
                event_type='social_media_monitor_init_error',
                details={'error': str(e)},
                severity='warning'
            )
            self.social_media_monitor = None

        # Initialize health monitor (optional)
        self.health_monitor = None
        self.health_server = None
        self.alert_manager = None
        if HEALTH_MONITOR_AVAILABLE:
            try:
                health_port = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
                self.health_monitor = HealthMonitor()
                self.health_server = HealthCheckServer(self.health_monitor, port=health_port)
                self.alert_manager = AlertManager()
            except Exception as e:
                self.audit_logger.log_event(
                    event_type='health_monitor_init_error',
                    details={'error': str(e)},
                    severity='warning'
                )

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.audit_logger.log_event(
            event_type='autonomous_loop_initialized',
            details={
                'enabled': self.enabled,
                'interval_seconds': self.loop_interval,
                'email_monitor_enabled': self.email_monitor is not None,
                'social_media_monitor_enabled': self.social_media_monitor is not None,
                'health_monitor_enabled': self.health_monitor is not None
            },
            severity='info'
        )

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n[SIGNAL] Received signal {signum}, shutting down gracefully...")
        self.stop()

    def check_kill_switch(self) -> bool:
        """
        Check if kill switch is activated

        Returns:
            True if system should continue, False if killed
        """
        if self.kill_switch.is_active():
            self.audit_logger.log_event(
                event_type='kill_switch_active',
                details={'message': 'Autonomous loop stopped by kill switch'},
                severity='critical'
            )
            return False
        return True

    def process_needs_action_folder(self) -> int:
        """
        Process tasks from Needs_Action folder

        Returns:
            Number of tasks processed
        """
        needs_action_path = Path('./Needs_Action')
        done_path = Path('./Done')
        done_path.mkdir(parents=True, exist_ok=True)

        tasks = list(needs_action_path.glob('*.json')) + \
                list(needs_action_path.glob('*.txt')) + \
                list(needs_action_path.glob('*.md'))

        processed_count = 0

        for task_path in tasks:
            try:
                # Read task
                task = self.task_processor.read_task(task_path)
                if not task:
                    continue

                # Analyze and create execution plan
                plan = self.decision_engine.analyze_task(task)

                # Execute plan
                result = self.decision_engine.execute_plan(plan)

                # Move to Done if successful
                if result.get('success'):
                    done_file = done_path / task_path.name

                    # Handle name conflicts
                    counter = 1
                    while done_file.exists():
                        stem = task_path.stem
                        suffix = task_path.suffix
                        done_file = done_path / f"{stem}_{counter}{suffix}"
                        counter += 1

                    task_path.rename(done_file)
                    processed_count += 1

                    self.audit_logger.log_event(
                        event_type='task_executed',
                        details={
                            'file': task_path.name,
                            'result': result,
                            'moved_to': str(done_file)
                        },
                        severity='info'
                    )
                else:
                    self.audit_logger.log_event(
                        event_type='task_execution_failed',
                        details={
                            'file': task_path.name,
                            'result': result
                        },
                        severity='warning'
                    )

            except Exception as e:
                self.audit_logger.log_event(
                    event_type='task_processing_error',
                    details={
                        'file': str(task_path),
                        'error': str(e)
                    },
                    severity='error'
                )

        return processed_count

    def run_iteration(self) -> dict:
        """
        Run a single iteration of the loop

        Returns:
            Iteration statistics
        """
        iteration_start = datetime.now()

        stats = {
            'timestamp': iteration_start.isoformat(),
            'emails_checked': 0,
            'social_mentions_checked': 0,
            'inbox_processed': 0,
            'needs_action_processed': 0,
            'errors': 0
        }

        try:
            # Step 1: Check for new emails (if email monitor is enabled)
            if self.email_monitor:
                try:
                    emails_count = self.email_monitor.process_new_emails()
                    stats['emails_checked'] = emails_count
                except Exception as e:
                    self.audit_logger.log_event(
                        event_type='email_check_error',
                        details={'error': str(e)},
                        severity='warning'
                    )

            # Step 2: Check for social media mentions (if social media monitor is enabled)
            if self.social_media_monitor:
                try:
                    mentions_count = self.social_media_monitor.check_all_platforms()
                    stats['social_mentions_checked'] = mentions_count
                except Exception as e:
                    self.audit_logger.log_event(
                        event_type='social_media_check_error',
                        details={'error': str(e)},
                        severity='warning'
                    )

            # Step 3: Process new tasks from Inbox
            inbox_results = self.task_processor.process_all_tasks()
            stats['inbox_processed'] = len([r for r in inbox_results if r.get('success')])
            stats['errors'] += len([r for r in inbox_results if not r.get('success')])

            # Step 4: Execute tasks from Needs_Action
            stats['needs_action_processed'] = self.process_needs_action_folder()

        except Exception as e:
            self.audit_logger.log_event(
                event_type='iteration_error',
                details={'error': str(e)},
                severity='error'
            )
            stats['errors'] += 1

        iteration_duration = (datetime.now() - iteration_start).total_seconds()
        stats['duration_seconds'] = iteration_duration

        # Update health monitor if available
        if self.health_monitor:
            self.health_monitor.update_iteration(stats)

        return stats

    def start(self):
        """Start the autonomous loop"""
        if not self.enabled:
            print("[INFO] Autonomous loop is DISABLED")
            print("[INFO] Set ENABLE_AUTONOMOUS_LOOP=true in .env to enable")
            return

        if not self.check_kill_switch():
            print("[CRITICAL] Kill switch is ACTIVE - cannot start")
            return

        self.running = True

        print("="*60)
        print("AUTONOMOUS LOOP STARTED (Ralph Wiggum Mode)")
        print("="*60)
        print(f"Interval: {self.loop_interval} seconds")
        print(f"Monitoring: Inbox/ and Needs_Action/")
        print(f"Press Ctrl+C to stop gracefully")
        print("="*60)

        # Start health check server if available
        if self.health_server:
            try:
                self.health_server.start()
            except Exception as e:
                print(f"[WARNING] Failed to start health server: {e}")

        self.audit_logger.log_event(
            event_type='autonomous_loop_started',
            details={'interval': self.loop_interval},
            severity='info'
        )

        iteration_count = 0

        while self.running:
            try:
                # Check kill switch
                if not self.check_kill_switch():
                    print("\n[CRITICAL] Kill switch activated - stopping loop")
                    break

                iteration_count += 1
                print(f"\n[Iteration {iteration_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Run iteration
                stats = self.run_iteration()

                # Print stats
                if stats['emails_checked'] > 0:
                    print(f"  [Email] Created {stats['emails_checked']} tasks from new emails")

                if stats['social_mentions_checked'] > 0:
                    print(f"  [Social] Created {stats['social_mentions_checked']} tasks from mentions")

                if stats['inbox_processed'] > 0 or stats['needs_action_processed'] > 0:
                    print(f"  [Inbox] Processed {stats['inbox_processed']} tasks")
                    print(f"  [Action] Executed {stats['needs_action_processed']} tasks")
                else:
                    print(f"  [Status] No new tasks")

                if stats['errors'] > 0:
                    print(f"  [Warning] {stats['errors']} errors occurred")

                # Periodic health check and alerting (every 10 iterations)
                if self.health_monitor and self.alert_manager and iteration_count % 10 == 0:
                    try:
                        health_status = self.health_monitor.get_health_status()
                        self.alert_manager.check_health_and_alert(health_status)
                    except Exception as e:
                        print(f"  [Warning] Health check failed: {e}")

                # Sleep until next iteration
                print(f"  [Status] Sleeping for {self.loop_interval} seconds...")
                time.sleep(self.loop_interval)

            except KeyboardInterrupt:
                print("\n[INFO] Keyboard interrupt received")
                break
            except Exception as e:
                print(f"\n[ERROR] Unexpected error: {e}")
                self.audit_logger.log_event(
                    event_type='loop_error',
                    details={'error': str(e)},
                    severity='error'
                )
                # Continue running despite errors
                time.sleep(self.loop_interval)

        self.stop()

    def stop(self):
        """Stop the autonomous loop"""
        if not self.running:
            return

        self.running = False

        print("\n" + "="*60)
        print("AUTONOMOUS LOOP STOPPED")
        print("="*60)

        # Stop health check server if running
        if self.health_server:
            try:
                self.health_server.stop()
            except Exception as e:
                print(f"[WARNING] Error stopping health server: {e}")

        self.audit_logger.log_event(
            event_type='autonomous_loop_stopped',
            details={'timestamp': datetime.now().isoformat()},
            severity='info'
        )


def main():
    """Main entry point"""
    loop = AutonomousLoop()

    try:
        loop.start()
    except Exception as e:
        print(f"\n[FATAL] Autonomous loop crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
