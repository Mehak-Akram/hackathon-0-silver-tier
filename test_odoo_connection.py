"""
Test Odoo Connection and Basic Operations
Run this to verify Odoo integration is working correctly
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from odoo_client import OdooClient, OdooConnectionError, OdooAuthenticationError
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_connection():
    """Test basic connection and authentication"""
    print("\n" + "="*60)
    print("TEST 1: Connection and Authentication")
    print("="*60)

    try:
        client = OdooClient()
        success = client.test_connection()

        if success:
            print("[OK] Connection successful!")
            print(f"   URL: {client.url}")
            print(f"   Database: {client.db}")
            print(f"   User ID: {client.uid}")
            return client
        else:
            print("[FAIL] Connection failed")
            return None

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return None


def test_create_customer(client):
    """Test customer creation"""
    print("\n" + "="*60)
    print("TEST 2: Create Customer")
    print("="*60)

    try:
        # Check if test customer already exists
        existing_id = client.search_customer(email="test@example.com")

        if existing_id:
            print(f"[INFO] Test customer already exists (ID: {existing_id})")
            return existing_id

        # Create new customer
        customer_id = client.create_customer(
            name="Test Customer",
            email="test@example.com",
            phone="+1234567890",
            street="123 Test Street",
            city="Test City"
        )

        print(f"[OK] Customer created successfully!")
        print(f"   Customer ID: {customer_id}")
        print(f"   Name: Test Customer")
        print(f"   Email: test@example.com")

        return customer_id

    except Exception as e:
        print(f"[FAIL] Error creating customer: {e}")
        return None


def test_create_lead(client, partner_id):
    """Test lead creation"""
    print("\n" + "="*60)
    print("TEST 3: Create Lead/Opportunity")
    print("="*60)

    try:
        lead_id = client.create_lead(
            name="AI Generated Lead - Test",
            partner_id=partner_id,
            email="test@example.com",
            phone="+1234567890",
            description="This is a test lead created by the AI system"
        )

        print(f"[OK] Lead created successfully!")
        print(f"   Lead ID: {lead_id}")
        print(f"   Title: AI Generated Lead - Test")
        print(f"   Customer ID: {partner_id}")

        return lead_id

    except Exception as e:
        print(f"[FAIL] Error creating lead: {e}")
        return None


def test_search_customer(client):
    """Test customer search"""
    print("\n" + "="*60)
    print("TEST 4: Search Customer")
    print("="*60)

    try:
        customer_id = client.search_customer(email="test@example.com")

        if customer_id:
            print(f"[OK] Customer found!")
            print(f"   Customer ID: {customer_id}")
        else:
            print("[INFO] No customer found with that email")

        return customer_id

    except Exception as e:
        print(f"[FAIL] Error searching customer: {e}")
        return None


def test_get_invoices(client):
    """Test invoice retrieval"""
    print("\n" + "="*60)
    print("TEST 5: Get Invoices")
    print("="*60)

    try:
        invoices = client.get_invoices(limit=5)

        print(f"[OK] Retrieved {len(invoices)} invoices")

        if invoices:
            print("\n   Recent invoices:")
            for inv in invoices[:3]:
                print(f"   - {inv['name']}: ${inv['amount_total']} ({inv['state']})")
        else:
            print("   [INFO] No invoices found (this is normal for a new database)")

        return invoices

    except Exception as e:
        print(f"[FAIL] Error retrieving invoices: {e}")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ODOO CONNECTION TEST SUITE")
    print("="*60)
    print(f"Testing connection to: {os.getenv('ODOO_URL', 'http://localhost:8069')}")
    print(f"Database: {os.getenv('ODOO_DB', 'odoo_db')}")

    # Test 1: Connection
    client = test_connection()
    if not client:
        print("\n[FAIL] Cannot connect to Odoo")
        print("\nTroubleshooting:")
        print("1. Check if Odoo is running: docker ps")
        print("2. Verify .env file has correct credentials")
        print("3. Check Odoo logs: docker logs odoo-erp")
        return False

    # Test 2: Create customer
    customer_id = test_create_customer(client)
    if not customer_id:
        print("\n[WARN] Customer creation failed")

    # Test 3: Create lead
    if customer_id:
        lead_id = test_create_lead(client, customer_id)
        if not lead_id:
            print("\n[WARN] Lead creation failed")

    # Test 4: Search customer
    test_search_customer(client)

    # Test 5: Get invoices
    test_get_invoices(client)

    # Summary
    print("\n" + "="*60)
    print("[OK] TEST SUITE COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Check Odoo dashboard at http://localhost:8069")
    print("2. Verify test customer and lead appear in CRM")
    print("3. Ready to integrate with MCP server")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
