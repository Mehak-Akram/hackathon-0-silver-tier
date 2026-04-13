"""
Test OdooClient class directly
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from odoo_client import OdooClient
import os

print("Environment variables:")
print(f"  ODOO_URL: {os.getenv('ODOO_URL')}")
print(f"  ODOO_DB: {os.getenv('ODOO_DB')}")
print(f"  ODOO_USERNAME: {os.getenv('ODOO_USERNAME')}")
print(f"  ODOO_PASSWORD: {os.getenv('ODOO_PASSWORD')}")
print()

print("Creating OdooClient instance...")
client = OdooClient()

print(f"Client configuration:")
print(f"  URL: {client.url}")
print(f"  Database: {client.db}")
print(f"  Username: {client.username}")
print(f"  Password: {'*' * len(client.password)}")
print()

print("Testing authenticate() method...")
try:
    uid = client.authenticate()
    print(f"  [OK] Authenticated! User ID: {uid}")
    print(f"  client.uid: {client.uid}")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
