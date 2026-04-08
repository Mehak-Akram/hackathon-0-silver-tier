"""
Windows Service Wrapper for Autonomous Loop
Uses NSSM (Non-Sucking Service Manager) for service installation
"""

import os
import sys
import subprocess
from pathlib import Path


class ServiceManager:
    """Manages Windows service installation and configuration"""

    def __init__(self):
        self.service_name = "GoldTierEmployee"
        self.service_display_name = "Gold Tier Autonomous Employee"
        self.service_description = "Autonomous business automation system with email and social media integration"

        self.project_root = Path(__file__).parent.parent
        self.python_exe = sys.executable
        self.script_path = self.project_root / "orchestrator" / "autonomous_loop.py"
        self.nssm_path = self.project_root / "tools" / "nssm.exe"

    def check_nssm(self) -> bool:
        """Check if NSSM is available"""
        if self.nssm_path.exists():
            return True

        print(f"[ERROR] NSSM not found at: {self.nssm_path}")
        print("\nDownload NSSM from: https://nssm.cc/download")
        print(f"Extract nssm.exe to: {self.project_root / 'tools'}")
        return False

    def install_service(self) -> bool:
        """Install the service"""
        if not self.check_nssm():
            return False

        print(f"Installing service: {self.service_name}")
        print(f"Python: {self.python_exe}")
        print(f"Script: {self.script_path}")

        try:
            # Install service
            subprocess.run([
                str(self.nssm_path),
                "install",
                self.service_name,
                str(self.python_exe),
                str(self.script_path)
            ], check=True)

            # Set service display name
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "DisplayName",
                self.service_display_name
            ], check=True)

            # Set service description
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "Description",
                self.service_description
            ], check=True)

            # Set working directory
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "AppDirectory",
                str(self.project_root)
            ], check=True)

            # Set startup type to automatic
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "Start",
                "SERVICE_AUTO_START"
            ], check=True)

            # Set restart behavior
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "AppExit",
                "Default",
                "Restart"
            ], check=True)

            # Set restart delay (10 seconds)
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "AppRestartDelay",
                "10000"
            ], check=True)

            # Set stdout log
            log_dir = self.project_root / "service_logs"
            log_dir.mkdir(exist_ok=True)

            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "AppStdout",
                str(log_dir / "service_stdout.log")
            ], check=True)

            # Set stderr log
            subprocess.run([
                str(self.nssm_path),
                "set",
                self.service_name,
                "AppStderr",
                str(log_dir / "service_stderr.log")
            ], check=True)

            print(f"\n[SUCCESS] Service '{self.service_name}' installed successfully!")
            print("\nNext steps:")
            print(f"1. Start service: net start {self.service_name}")
            print(f"2. Check status: sc query {self.service_name}")
            print(f"3. View logs: {log_dir}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Failed to install service: {e}")
            return False

    def uninstall_service(self) -> bool:
        """Uninstall the service"""
        if not self.check_nssm():
            return False

        print(f"Uninstalling service: {self.service_name}")

        try:
            # Stop service first
            subprocess.run([
                str(self.nssm_path),
                "stop",
                self.service_name
            ], check=False)  # Don't fail if already stopped

            # Remove service
            subprocess.run([
                str(self.nssm_path),
                "remove",
                self.service_name,
                "confirm"
            ], check=True)

            print(f"\n[SUCCESS] Service '{self.service_name}' uninstalled successfully!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Failed to uninstall service: {e}")
            return False

    def start_service(self) -> bool:
        """Start the service"""
        try:
            subprocess.run([
                "net", "start", self.service_name
            ], check=True)
            print(f"[SUCCESS] Service '{self.service_name}' started")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to start service: {e}")
            return False

    def stop_service(self) -> bool:
        """Stop the service"""
        try:
            subprocess.run([
                "net", "stop", self.service_name
            ], check=True)
            print(f"[SUCCESS] Service '{self.service_name}' stopped")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to stop service: {e}")
            return False

    def restart_service(self) -> bool:
        """Restart the service"""
        print(f"Restarting service: {self.service_name}")
        self.stop_service()
        return self.start_service()

    def status_service(self) -> bool:
        """Check service status"""
        try:
            result = subprocess.run([
                "sc", "query", self.service_name
            ], capture_output=True, text=True, check=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Service not found or error: {e}")
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Manage Gold Tier Employee Windows Service")
    parser.add_argument("action", choices=["install", "uninstall", "start", "stop", "restart", "status"],
                        help="Service action to perform")

    args = parser.parse_args()

    manager = ServiceManager()

    if args.action == "install":
        manager.install_service()
    elif args.action == "uninstall":
        manager.uninstall_service()
    elif args.action == "start":
        manager.start_service()
    elif args.action == "stop":
        manager.stop_service()
    elif args.action == "restart":
        manager.restart_service()
    elif args.action == "status":
        manager.status_service()


if __name__ == "__main__":
    main()
