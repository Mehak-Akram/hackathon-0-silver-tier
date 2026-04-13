"""
Debug Odoo XML-RPC Authentication
"""
import xmlrpc.client
import os

url = os.getenv('ODOO_URL', 'http://localhost:8069')
db = os.getenv('ODOO_DB', 'odoo_db')
username = os.getenv('ODOO_USERNAME', 'mehakakram128@gmail.com')
password = os.getenv('ODOO_PASSWORD', 'odoo')

print(f"Testing authentication:")
print(f"  URL: {url}")
print(f"  Database: {db}")
print(f"  Username: {username}")
print(f"  Password: {'*' * len(password)}")
print()

# Test 1: Check server version
print("Test 1: Checking server version...")
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    version = common.version()
    print(f"  [OK] Server version: {version['server_version']}")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 2: Authenticate
print("\nTest 2: Authenticating...")
try:
    uid = common.authenticate(db, username, password, {})
    print(f"  Result: {uid}")
    print(f"  Type: {type(uid)}")

    if uid:
        print(f"  [OK] Authenticated! User ID: {uid}")
    else:
        print(f"  [FAIL] Authentication returned False/None")

        # Try with different parameters
        print("\nTest 3: Trying alternative authentication...")
        uid2 = common.login(db, username, password)
        print(f"  Result: {uid2}")

except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
