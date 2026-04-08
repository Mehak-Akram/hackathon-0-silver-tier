"""
Deployment Verification Test
Verifies that all production deployment components are properly configured
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))


class DeploymentVerifier:
    """Verifies production deployment readiness"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0

    def run_all_checks(self):
        """Run all deployment verification checks"""
        print("="*60)
        print("DEPLOYMENT VERIFICATION")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        checks = [
            ("Python Version", self.check_python_version),
            ("Project Structure", self.check_project_structure),
            ("NSSM Installation", self.check_nssm),
            ("Environment Configuration", self.check_env_file),
            ("Dependencies", self.check_dependencies),
            ("Odoo Connection", self.check_odoo),
            ("Health Monitor", self.check_health_monitor),
            ("Alert Manager", self.check_alert_manager),
            ("Log Directories", self.check_log_directories),
            ("Service Scripts", self.check_service_scripts)
        ]

        for check_name, check_func in checks:
            print(f"[CHECK] {check_name}...")
            try:
                result = check_func()
                if result:
                    print(f"  [PASS] {check_name}")
                    self.checks_passed += 1
                else:
                    print(f"  [FAIL] {check_name}")
                    self.checks_failed += 1
            except Exception as e:
                print(f"  [ERROR] {check_name}: {e}")
                self.checks_failed += 1
            print()

        self.print_summary()

    def check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"  Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"  Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
            return False

    def check_project_structure(self) -> bool:
        """Check required directories exist"""
        required_dirs = [
            "orchestrator",
            "src",
            "mcp_server",
            "deployment"
        ]

        all_exist = True
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"  Found: {dir_name}/")
            else:
                print(f"  Missing: {dir_name}/")
                all_exist = False

        return all_exist

    def check_nssm(self) -> bool:
        """Check if NSSM is installed"""
        nssm_path = self.project_root / "tools" / "nssm.exe"
        if nssm_path.exists():
            size_mb = nssm_path.stat().st_size / (1024 * 1024)
            print(f"  Found: tools/nssm.exe ({size_mb:.2f} MB)")
            return True
        else:
            print(f"  Missing: tools/nssm.exe")
            print(f"  Download from: https://nssm.cc/download")
            return False

    def check_env_file(self) -> bool:
        """Check .env file exists and has required settings"""
        env_path = self.project_root / ".env"
        if not env_path.exists():
            print(f"  Missing: .env file")
            print(f"  Copy .env.example to .env and configure")
            return False

        # Check for required settings
        required_settings = [
            "ENABLE_AUTONOMOUS_LOOP",
            "ODOO_URL",
            "ODOO_DB",
            "ODOO_USERNAME"
        ]

        env_content = env_path.read_text()
        missing = []

        for setting in required_settings:
            if setting not in env_content:
                missing.append(setting)

        if missing:
            print(f"  Missing settings: {', '.join(missing)}")
            return False

        print(f"  Found: .env with required settings")
        return True

    def check_dependencies(self) -> bool:
        """Check if required Python packages are installed"""
        required_packages = [
            "dotenv",
            "psutil",
            "requests"
        ]

        missing = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if missing:
            print(f"  Missing packages: {', '.join(missing)}")
            print(f"  Install: pip install -r requirements.txt")
            return False

        print(f"  All required packages installed")
        return True

    def check_odoo(self) -> bool:
        """Check if Odoo is accessible"""
        try:
            import requests
            odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
            response = requests.get(odoo_url, timeout=5)
            if response.status_code == 200:
                print(f"  Odoo accessible at {odoo_url}")
                return True
            else:
                print(f"  Odoo returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"  Cannot connect to Odoo: {e}")
            print(f"  Start Odoo: docker-compose up -d")
            self.warnings += 1
            return False

    def check_health_monitor(self) -> bool:
        """Check if health monitor module exists"""
        health_monitor_path = self.project_root / "deployment" / "health_monitor.py"
        if health_monitor_path.exists():
            print(f"  Found: deployment/health_monitor.py")
            return True
        else:
            print(f"  Missing: deployment/health_monitor.py")
            return False

    def check_alert_manager(self) -> bool:
        """Check if alert manager module exists"""
        alert_manager_path = self.project_root / "deployment" / "alert_manager.py"
        if alert_manager_path.exists():
            print(f"  Found: deployment/alert_manager.py")
            return True
        else:
            print(f"  Missing: deployment/alert_manager.py")
            return False

    def check_log_directories(self) -> bool:
        """Check if log directories exist or can be created"""
        log_dirs = [
            "Audit_Logs",
            "service_logs"
        ]

        all_ok = True
        for dir_name in log_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"  Found: {dir_name}/")
            else:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"  Created: {dir_name}/")
                except Exception as e:
                    print(f"  Cannot create {dir_name}/: {e}")
                    all_ok = False

        return all_ok

    def check_service_scripts(self) -> bool:
        """Check if service management scripts exist"""
        scripts = [
            "install_service.bat",
            "uninstall_service.bat",
            "start_service.bat",
            "stop_service.bat",
            "restart_service.bat"
        ]

        all_exist = True
        for script in scripts:
            script_path = self.project_root / script
            if script_path.exists():
                print(f"  Found: {script}")
            else:
                print(f"  Missing: {script}")
                all_exist = False

        return all_exist

    def print_summary(self):
        """Print verification summary"""
        print("="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        print(f"Checks passed: {self.checks_passed}")
        print(f"Checks failed: {self.checks_failed}")
        print(f"Warnings: {self.warnings}")
        print()

        if self.checks_failed == 0:
            print("[SUCCESS] All checks passed!")
            print()
            print("Ready for production deployment:")
            print("1. Review .env configuration")
            print("2. Run: install_service.bat (as Administrator)")
            print("3. Run: net start GoldTierEmployee")
            print("4. Open: http://localhost:8080/")
        else:
            print("[WARNING] Some checks failed")
            print()
            print("Fix the issues above before deploying to production.")
            print("See DEPLOYMENT.md for detailed instructions.")

        print()


def main():
    """Main entry point"""
    verifier = DeploymentVerifier()
    verifier.run_all_checks()

    # Return exit code
    sys.exit(0 if verifier.checks_failed == 0 else 1)


if __name__ == "__main__":
    main()
