"""
Test MCP Server Odoo Integration
Verifies that Odoo tools are accessible through MCP server
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from mcp_server.server import GoldTierMCPServer
import asyncio
import json

async def test_odoo_integration():
    """Test Odoo integration in MCP server"""

    print("="*60)
    print("MCP SERVER ODOO INTEGRATION TEST")
    print("="*60)

    # Initialize server
    print("\n[1/5] Initializing MCP server...")
    try:
        server = GoldTierMCPServer()
        if server.odoo_client is None:
            print("   [FAIL] Odoo client not initialized")
            return False
        print("   [OK] MCP server initialized with Odoo client")
    except Exception as e:
        print(f"   [FAIL] Server initialization failed: {e}")
        return False

    # Test 1: Create customer
    print("\n[2/5] Testing odoo_create_customer...")
    try:
        result = await server._handle_odoo_create_customer({
            "name": "MCP Test Customer",
            "email": "mcp-test@example.com",
            "phone": "+1234567890"
        })
        response = json.loads(result[0].text)
        if response.get('success'):
            customer_id = response.get('customer_id')
            print(f"   [OK] Customer created: ID {customer_id}")
        else:
            print(f"   [FAIL] {response.get('message')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

    # Test 2: Search customer
    print("\n[3/5] Testing odoo_search_customer...")
    try:
        result = await server._handle_odoo_search_customer({
            "email": "mcp-test@example.com"
        })
        response = json.loads(result[0].text)
        if response.get('success') and response.get('customer_id'):
            print(f"   [OK] Customer found: ID {response.get('customer_id')}")
        else:
            print(f"   [FAIL] Customer not found")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

    # Test 3: Create lead
    print("\n[4/5] Testing odoo_create_lead...")
    try:
        result = await server._handle_odoo_create_lead({
            "name": "MCP Test Lead",
            "partner_id": customer_id,
            "email": "mcp-test@example.com",
            "description": "Lead created via MCP server integration test"
        })
        response = json.loads(result[0].text)
        if response.get('success'):
            lead_id = response.get('lead_id')
            print(f"   [OK] Lead created: ID {lead_id}")
        else:
            print(f"   [FAIL] {response.get('message')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

    # Test 4: Get invoices
    print("\n[5/5] Testing odoo_get_invoices...")
    try:
        result = await server._handle_odoo_get_invoices({
            "limit": 5
        })
        response = json.loads(result[0].text)
        if response.get('success'):
            count = response.get('count')
            print(f"   [OK] Retrieved {count} invoices")
        else:
            print(f"   [FAIL] {response.get('message')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

    print("\n" + "="*60)
    print("[OK] ALL TESTS PASSED")
    print("="*60)
    print("\nMCP Server Odoo Integration is working correctly!")
    print("\nNext steps:")
    print("1. Your AI system can now use Odoo tools via MCP")
    print("2. Check Odoo dashboard: http://localhost:8069")
    print("3. Verify test customer and lead appear in CRM")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_odoo_integration())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
