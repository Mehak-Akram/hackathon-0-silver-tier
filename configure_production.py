"""
Production Configuration Wizard
Interactive setup for real credentials
"""

import os
import sys
from pathlib import Path
from getpass import getpass

def print_header(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def print_section(title):
    print(f"\n{title}")
    print("-"*60)

def get_input(prompt, default=None, required=True):
    """Get user input with optional default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    while True:
        value = input(prompt).strip()
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("This field is required. Please enter a value.")

def get_password(prompt):
    """Get password input (hidden)"""
    while True:
        password = getpass(f"{prompt}: ")
        if password:
            return password
        print("Password is required. Please enter a value.")

def yes_no(prompt, default="n"):
    """Get yes/no input"""
    while True:
        response = input(f"{prompt} (y/n) [{default}]: ").strip().lower()
        if not response:
            response = default
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def test_email_connection(email, password):
    """Test email credentials"""
    print("\n  Testing IMAP connection...", end=" ")
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email, password)
        mail.logout()
        print("✓ Success")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_smtp_connection(email, password):
    """Test SMTP credentials"""
    print("  Testing SMTP connection...", end=" ")
    try:
        import smtplib
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        print("✓ Success")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_odoo_connection(url, db, username, password):
    """Test Odoo credentials"""
    print("\n  Testing Odoo connection...", end=" ")
    try:
        import xmlrpc.client
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"✓ Success (User ID: {uid})")
            return True
        else:
            print("✗ Failed: Authentication failed")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    """Main configuration wizard"""
    print_header("PRODUCTION CONFIGURATION WIZARD")
    print("\nThis wizard will help you configure real credentials for production.")
    print("All sensitive data will be stored in .env file (not in version control).")
    print("\nPress Ctrl+C at any time to cancel.")

    config = {}

    # Read existing .env if it exists
    env_path = Path('.env')
    existing_config = {}
    if env_path.exists():
        print("\n[INFO] Found existing .env file. Current values will be shown as defaults.")
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                existing_config[key.strip()] = value.strip()

    # Core Settings
    print_section("1. CORE SETTINGS")
    config['ENABLE_AUTONOMOUS_LOOP'] = 'true'
    config['LOOP_INTERVAL_SECONDS'] = get_input(
        "Loop interval in seconds",
        default=existing_config.get('LOOP_INTERVAL_SECONDS', '60')
    )

    # Odoo Configuration
    print_section("2. ODOO CONFIGURATION")
    print("\nOdoo is your CRM system for managing customers and leads.")

    config['ODOO_URL'] = get_input(
        "Odoo URL",
        default=existing_config.get('ODOO_URL', 'http://localhost:8069')
    )
    config['ODOO_DB'] = get_input(
        "Odoo database name",
        default=existing_config.get('ODOO_DB', 'odoo')
    )
    config['ODOO_USERNAME'] = get_input(
        "Odoo username",
        default=existing_config.get('ODOO_USERNAME', 'admin')
    )

    if yes_no("Change Odoo password?", default='n' if existing_config.get('ODOO_PASSWORD') else 'y'):
        config['ODOO_PASSWORD'] = get_password("Odoo password")
    else:
        config['ODOO_PASSWORD'] = existing_config.get('ODOO_PASSWORD', '')

    # Test Odoo connection
    if config['ODOO_PASSWORD']:
        if not test_odoo_connection(
            config['ODOO_URL'],
            config['ODOO_DB'],
            config['ODOO_USERNAME'],
            config['ODOO_PASSWORD']
        ):
            print("\n[WARNING] Odoo connection failed. Please verify credentials.")
            if not yes_no("Continue anyway?", default='n'):
                print("\nConfiguration cancelled.")
                return

    # Email Configuration
    print_section("3. EMAIL CONFIGURATION")
    print("\nEmail is used for:")
    print("  - Monitoring incoming customer emails (IMAP)")
    print("  - Sending auto-responses (SMTP)")
    print("  - Sending alerts and CEO briefings")
    print("\nFor Gmail:")
    print("  1. Enable 2-Factor Authentication")
    print("  2. Generate App Password: https://myaccount.google.com/apppasswords")
    print("  3. Use the 16-character App Password (not your regular password)")

    if yes_no("\nConfigure email now?", default='y'):
        config['EMAIL_ADDRESS'] = get_input(
            "Email address",
            default=existing_config.get('EMAIL_ADDRESS', '')
        )

        if yes_no("Change email password?", default='n' if existing_config.get('EMAIL_PASSWORD') else 'y'):
            print("\nEnter your Gmail App Password (16 characters, no spaces):")
            config['EMAIL_PASSWORD'] = get_password("App Password")
        else:
            config['EMAIL_PASSWORD'] = existing_config.get('EMAIL_PASSWORD', '')

        config['SMTP_HOST'] = get_input("SMTP host", default='smtp.gmail.com')
        config['SMTP_PORT'] = get_input("SMTP port", default='587')
        config['IMAP_HOST'] = get_input("IMAP host", default='imap.gmail.com')
        config['IMAP_PORT'] = get_input("IMAP port", default='993')
        config['EMAIL_FROM_NAME'] = get_input(
            "From name (displayed in emails)",
            default=existing_config.get('EMAIL_FROM_NAME', 'AI Employee')
        )

        # Test email connection
        if config['EMAIL_PASSWORD']:
            print("\nTesting email connection...")
            imap_ok = test_email_connection(config['EMAIL_ADDRESS'], config['EMAIL_PASSWORD'])
            smtp_ok = test_smtp_connection(config['EMAIL_ADDRESS'], config['EMAIL_PASSWORD'])

            if not (imap_ok and smtp_ok):
                print("\n[WARNING] Email connection failed.")
                print("Common issues:")
                print("  - Using regular password instead of App Password")
                print("  - 2-Factor Authentication not enabled")
                print("  - App Password not generated")
                if not yes_no("Continue anyway?", default='n'):
                    print("\nConfiguration cancelled.")
                    return
    else:
        # Keep existing or use defaults
        config['EMAIL_ADDRESS'] = existing_config.get('EMAIL_ADDRESS', '')
        config['EMAIL_PASSWORD'] = existing_config.get('EMAIL_PASSWORD', '')
        config['SMTP_HOST'] = existing_config.get('SMTP_HOST', 'smtp.gmail.com')
        config['SMTP_PORT'] = existing_config.get('SMTP_PORT', '587')
        config['IMAP_HOST'] = existing_config.get('IMAP_HOST', 'imap.gmail.com')
        config['IMAP_PORT'] = existing_config.get('IMAP_PORT', '993')
        config['EMAIL_FROM_NAME'] = existing_config.get('EMAIL_FROM_NAME', 'AI Employee')

    # Social Media (Optional)
    print_section("4. SOCIAL MEDIA MONITORING (Optional)")
    print("\nSocial media monitoring tracks mentions on Facebook, Twitter, and Instagram.")
    print("This is optional and can be configured later.")

    if yes_no("\nConfigure social media now?", default='n'):
        # Facebook
        if yes_no("  Configure Facebook?", default='n'):
            config['FACEBOOK_MONITORING_ENABLED'] = 'true'
            config['FACEBOOK_PAGE_ID'] = get_input("    Facebook Page ID")
            config['FACEBOOK_ACCESS_TOKEN'] = get_password("    Facebook Access Token")
        else:
            config['FACEBOOK_MONITORING_ENABLED'] = 'false'
            config['FACEBOOK_PAGE_ID'] = ''
            config['FACEBOOK_ACCESS_TOKEN'] = ''

        # Twitter
        if yes_no("  Configure Twitter?", default='n'):
            config['TWITTER_MONITORING_ENABLED'] = 'true'
            config['TWITTER_BEARER_TOKEN'] = get_password("    Twitter Bearer Token")
        else:
            config['TWITTER_MONITORING_ENABLED'] = 'false'
            config['TWITTER_BEARER_TOKEN'] = ''

        # Instagram
        if yes_no("  Configure Instagram?", default='n'):
            config['INSTAGRAM_MONITORING_ENABLED'] = 'true'
            config['INSTAGRAM_ACCESS_TOKEN'] = get_password("    Instagram Access Token")
            config['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = get_input("    Instagram Business Account ID")
        else:
            config['INSTAGRAM_MONITORING_ENABLED'] = 'false'
            config['INSTAGRAM_ACCESS_TOKEN'] = ''
            config['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = ''
    else:
        config['FACEBOOK_MONITORING_ENABLED'] = 'false'
        config['FACEBOOK_PAGE_ID'] = ''
        config['FACEBOOK_ACCESS_TOKEN'] = ''
        config['TWITTER_MONITORING_ENABLED'] = 'false'
        config['TWITTER_BEARER_TOKEN'] = ''
        config['INSTAGRAM_MONITORING_ENABLED'] = 'false'
        config['INSTAGRAM_ACCESS_TOKEN'] = ''
        config['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = ''

    # Health Monitoring
    print_section("5. HEALTH MONITORING")
    config['HEALTH_CHECK_PORT'] = get_input(
        "Health dashboard port",
        default=existing_config.get('HEALTH_CHECK_PORT', '8080')
    )

    # Alerting
    print_section("6. ALERTING")
    print("\nAlerts notify you of system issues via email.")

    if yes_no("Enable email alerts?", default='y'):
        config['ALERT_EMAIL_ENABLED'] = 'true'
        config['ALERT_EMAIL_TO'] = get_input(
            "Alert recipient email(s) (comma-separated)",
            default=existing_config.get('ALERT_EMAIL_TO', config.get('EMAIL_ADDRESS', ''))
        )
        config['ALERT_ERROR_RATE_THRESHOLD'] = get_input(
            "Error rate threshold (%)",
            default='10.0'
        )
        config['ALERT_CPU_THRESHOLD'] = get_input(
            "CPU usage threshold (%)",
            default='90.0'
        )
        config['ALERT_MEMORY_THRESHOLD'] = get_input(
            "Memory usage threshold (%)",
            default='90.0'
        )
    else:
        config['ALERT_EMAIL_ENABLED'] = 'false'
        config['ALERT_EMAIL_TO'] = ''
        config['ALERT_ERROR_RATE_THRESHOLD'] = '10.0'
        config['ALERT_CPU_THRESHOLD'] = '90.0'
        config['ALERT_MEMORY_THRESHOLD'] = '90.0'

    # CEO Briefing
    print_section("7. CEO BRIEFING SYSTEM")
    print("\nCEO briefings are weekly executive reports sent via email.")

    if yes_no("Enable CEO briefings?", default='y'):
        config['CEO_BRIEFING_EMAIL_ENABLED'] = 'true'
        config['CEO_BRIEFING_RECIPIENTS'] = get_input(
            "Briefing recipient email(s) (comma-separated)",
            default=existing_config.get('CEO_BRIEFING_RECIPIENTS', config.get('EMAIL_ADDRESS', ''))
        )
    else:
        config['CEO_BRIEFING_EMAIL_ENABLED'] = 'false'
        config['CEO_BRIEFING_RECIPIENTS'] = ''

    # Log Management
    print_section("8. LOG MANAGEMENT")
    config['LOG_MAX_AGE_DAYS'] = get_input("Maximum log age (days)", default='30')
    config['LOG_COMPRESS_AGE_DAYS'] = get_input("Compress logs older than (days)", default='7')

    # Write .env file
    print_section("9. SAVING CONFIGURATION")

    # Backup existing .env
    if env_path.exists():
        backup_path = Path('.env.backup')
        env_path.rename(backup_path)
        print(f"\n  Backed up existing .env to: {backup_path}")

    # Write new .env
    env_content = """# ============================================================
# Gold Tier Autonomous Employee - Production Configuration
# ============================================================
# Generated by Production Configuration Wizard
# DO NOT commit this file to version control

# ============================================================
# CORE SETTINGS
# ============================================================
ENABLE_AUTONOMOUS_LOOP={ENABLE_AUTONOMOUS_LOOP}
LOOP_INTERVAL_SECONDS={LOOP_INTERVAL_SECONDS}

# ============================================================
# ODOO CONFIGURATION
# ============================================================
ODOO_URL={ODOO_URL}
ODOO_DB={ODOO_DB}
ODOO_USERNAME={ODOO_USERNAME}
ODOO_PASSWORD={ODOO_PASSWORD}

# ============================================================
# EMAIL CONFIGURATION
# ============================================================
EMAIL_ADDRESS={EMAIL_ADDRESS}
EMAIL_PASSWORD={EMAIL_PASSWORD}
SMTP_HOST={SMTP_HOST}
SMTP_PORT={SMTP_PORT}
IMAP_HOST={IMAP_HOST}
IMAP_PORT={IMAP_PORT}
EMAIL_FROM_NAME={EMAIL_FROM_NAME}

# ============================================================
# SOCIAL MEDIA MONITORING
# ============================================================
FACEBOOK_MONITORING_ENABLED={FACEBOOK_MONITORING_ENABLED}
FACEBOOK_PAGE_ID={FACEBOOK_PAGE_ID}
FACEBOOK_ACCESS_TOKEN={FACEBOOK_ACCESS_TOKEN}

TWITTER_MONITORING_ENABLED={TWITTER_MONITORING_ENABLED}
TWITTER_BEARER_TOKEN={TWITTER_BEARER_TOKEN}

INSTAGRAM_MONITORING_ENABLED={INSTAGRAM_MONITORING_ENABLED}
INSTAGRAM_ACCESS_TOKEN={INSTAGRAM_ACCESS_TOKEN}
INSTAGRAM_BUSINESS_ACCOUNT_ID={INSTAGRAM_BUSINESS_ACCOUNT_ID}

# ============================================================
# HEALTH MONITORING
# ============================================================
HEALTH_CHECK_PORT={HEALTH_CHECK_PORT}

# ============================================================
# ALERTING
# ============================================================
ALERT_EMAIL_ENABLED={ALERT_EMAIL_ENABLED}
ALERT_EMAIL_TO={ALERT_EMAIL_TO}
ALERT_ERROR_RATE_THRESHOLD={ALERT_ERROR_RATE_THRESHOLD}
ALERT_CPU_THRESHOLD={ALERT_CPU_THRESHOLD}
ALERT_MEMORY_THRESHOLD={ALERT_MEMORY_THRESHOLD}
ALERT_NO_ITERATION_SECONDS=300
ALERT_COOLDOWN_MINUTES=30

# ============================================================
# CEO BRIEFING SYSTEM
# ============================================================
CEO_BRIEFING_EMAIL_ENABLED={CEO_BRIEFING_EMAIL_ENABLED}
CEO_BRIEFING_RECIPIENTS={CEO_BRIEFING_RECIPIENTS}

# ============================================================
# LOG MANAGEMENT
# ============================================================
LOG_MAX_AGE_DAYS={LOG_MAX_AGE_DAYS}
LOG_COMPRESS_AGE_DAYS={LOG_COMPRESS_AGE_DAYS}
LOG_MAX_SIZE_MB=100

# ============================================================
# SECURITY
# ============================================================
KILL_SWITCH_FILE=kill_switch.txt
""".format(**config)

    env_path.write_text(env_content)
    print(f"\n  ✓ Configuration saved to: {env_path}")

    # Summary
    print_header("CONFIGURATION COMPLETE")
    print("\n✓ Configuration saved successfully!")
    print("\nNext steps:")
    print("  1. Test the system: python start_autonomous_loop.bat")
    print("  2. Access dashboard: http://localhost:{HEALTH_CHECK_PORT}/".format(**config))
    print("  3. Send test email to: {EMAIL_ADDRESS}".format(**config))
    print("  4. Generate CEO briefing: python reporting/ceo_briefing_cli.py generate")
    print("\nFor production deployment as Windows service:")
    print("  1. Download NSSM: https://nssm.cc/download")
    print("  2. Run: install_service.bat (as Administrator)")
    print("\nConfiguration file: .env")
    print("Backup file: .env.backup (if existed)")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
