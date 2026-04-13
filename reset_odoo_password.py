"""
Reset Odoo admin password directly in PostgreSQL
"""
import psycopg2
from passlib.context import CryptContext

# Password hashing context (same as Odoo uses)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha512"],
    deprecated="auto"
)

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="odoo_db",
    user="odoo",
    password="am9081"
)

cursor = conn.cursor()

# Hash the new password
new_password = "odoo"
password_hash = pwd_context.hash(new_password)

# Update the password
cursor.execute(
    "UPDATE res_users SET password = %s WHERE login = %s",
    (password_hash, "mehakakram128@gmail.com")
)

conn.commit()

# Verify update
cursor.execute(
    "SELECT login, active FROM res_users WHERE login = %s",
    ("mehakakram128@gmail.com",)
)
result = cursor.fetchone()

if result:
    print(f"[OK] Password reset successful for user: {result[0]}")
    print(f"     New password: {new_password}")
else:
    print("[FAIL] User not found")

cursor.close()
conn.close()
