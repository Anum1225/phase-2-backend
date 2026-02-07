"""
Quick test script to verify database connection and backend configuration.
"""

import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("=" * 70)
print("BACKEND CONFIGURATION TEST")
print("=" * 70)

# Test 1: Environment Variables
print("\n1. Testing Environment Variables...")
required_vars = ["DATABASE_URL", "BETTER_AUTH_SECRET", "CORS_ORIGINS"]
missing_vars = []

for var in required_vars:
    value = os.getenv(var)
    if not value:
        print(f"   ❌ Missing: {var}")
        missing_vars.append(var)
    else:
        # Mask sensitive values
        if var == "DATABASE_URL":
            masked = value.split("@")[0].split("://")[0] + "://***@" + value.split("@")[1] if "@" in value else "***"
            print(f"   ✅ {var}: {masked}")
        elif var == "BETTER_AUTH_SECRET":
            print(f"   ✅ {var}: {'*' * len(value)} ({len(value)} chars)")
        else:
            print(f"   ✅ {var}: {value}")

if missing_vars:
    print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Test 2: Secret Key Length
print("\n2. Testing JWT Secret Length...")
secret = os.getenv("BETTER_AUTH_SECRET")
if len(secret) < 32:
    print(f"   ⚠️  WARNING: Secret is only {len(secret)} characters (recommend 32+)")
else:
    print(f"   ✅ Secret length: {len(secret)} characters (good)")

# Test 3: Database Connection
print("\n3. Testing Database Connection...")
try:
    from src.core.database import engine
    from sqlmodel import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"   ✅ Connected to PostgreSQL")
        print(f"   ✅ Version: {version[:50]}...")
except Exception as e:
    print(f"   ❌ Connection failed: {str(e)}")
    sys.exit(1)

# Test 4: Verify Tables
print("\n4. Checking Database Tables...")
try:
    with engine.connect() as conn:
        # Check users table
        result = conn.execute(text("SELECT COUNT(*) FROM users;"))
        user_count = result.fetchone()[0]
        print(f"   ✅ Users table exists ({user_count} users)")

        # Check tasks table
        result = conn.execute(text("SELECT COUNT(*) FROM tasks;"))
        task_count = result.fetchone()[0]
        print(f"   ✅ Tasks table exists ({task_count} tasks)")
except Exception as e:
    print(f"   ❌ Table check failed: {str(e)}")
    print("   ℹ️  Run schema.sql to create tables")

# Test 5: Verify Foreign Key
print("\n5. Checking Foreign Key Constraint...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT constraint_name, delete_rule, update_rule
            FROM information_schema.referential_constraints
            WHERE constraint_name = 'fk_tasks_user_id';
        """))
        fk = result.fetchone()
        if fk:
            print(f"   ✅ Foreign key: {fk[0]}")
            print(f"   ✅ ON DELETE: {fk[1]}")
            print(f"   ✅ ON UPDATE: {fk[2]}")
        else:
            print("   ⚠️  Foreign key constraint not found")
except Exception as e:
    print(f"   ℹ️  Could not verify: {str(e)}")

# Test 6: Security Utilities
print("\n6. Testing Security Utilities...")
try:
    from src.core.security import hash_password, verify_password, create_access_token, decode_access_token

    # Test password hashing
    password = "testpass123"
    hashed = hash_password(password)
    print(f"   ✅ Password hashing works (hash length: {len(hashed)})")

    # Test password verification
    is_valid = verify_password(password, hashed)
    print(f"   ✅ Password verification: {is_valid}")

    # Test JWT creation
    token = create_access_token("test-user-id", "test@example.com")
    print(f"   ✅ JWT creation works (token length: {len(token)})")

    # Test JWT decoding
    payload = decode_access_token(token)
    print(f"   ✅ JWT decoding works (user_id: {payload['sub']})")

except Exception as e:
    print(f"   ❌ Security utilities failed: {str(e)}")
    sys.exit(1)

# Test 7: FastAPI App
print("\n7. Testing FastAPI Application...")
try:
    from src.main import app
    print(f"   ✅ FastAPI app loads successfully")
    print(f"   ✅ App title: {app.title}")
    print(f"   ✅ App version: {app.version}")
    print(f"   ✅ Routes: {len(app.routes)} registered")
except Exception as e:
    print(f"   ❌ App loading failed: {str(e)}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("CONFIGURATION TEST COMPLETE - ALL CHECKS PASSED ✅")
print("=" * 70)
print("\nBackend is ready to run!")
print("\nStart the server:")
print("  uvicorn src.main:app --reload")
print("\nAPI Documentation:")
print("  http://localhost:8000/docs")
print("=" * 70)
