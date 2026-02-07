"""
Backend setup verification script (Windows-compatible).
"""

import sys
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 70)
print("BACKEND CONFIGURATION TEST")
print("=" * 70)

# Test 1: Environment Variables
print("\n1. Environment Variables:")
required_vars = ["DATABASE_URL", "BETTER_AUTH_SECRET", "CORS_ORIGINS"]
all_present = True

for var in required_vars:
    value = os.getenv(var)
    if not value:
        print(f"   [MISSING] {var}")
        all_present = False
    else:
        if var == "DATABASE_URL":
            masked = "postgresql://***@" + value.split("@")[1] if "@" in value else "***"
            print(f"   [OK] {var}: {masked}")
        elif var == "BETTER_AUTH_SECRET":
            print(f"   [OK] {var}: {'*' * min(len(value), 20)} ({len(value)} chars)")
        else:
            print(f"   [OK] {var}: {value}")

if not all_present:
    print("\n[ERROR] Missing required variables")
    sys.exit(1)

# Test 2: Database Connection
print("\n2. Database Connection:")
try:
    from src.core.database import engine
    from sqlmodel import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;"))
        print("   [OK] Database connection successful")

        # Check tables
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name IN ('users', 'tasks')
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"   [OK] Tables found: {', '.join(tables)}")

        # Check foreign key
        result = conn.execute(text("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY' AND table_name = 'tasks';
        """))
        fks = [row[0] for row in result.fetchall()]
        if fks:
            print(f"   [OK] Foreign key: {', '.join(fks)}")
        else:
            print("   [WARNING] No foreign key found")

except Exception as e:
    print(f"   [ERROR] {str(e)}")
    sys.exit(1)

# Test 3: Security Functions
print("\n3. Security Functions:")
try:
    from src.core.security import hash_password, verify_password, create_access_token

    # Test password hashing
    hashed = hash_password("test123456")
    print(f"   [OK] Password hashing (length: {len(hashed)})")

    # Test password verification
    valid = verify_password("test123456", hashed)
    print(f"   [OK] Password verification: {valid}")

    # Test JWT
    token = create_access_token("test-id", "test@test.com")
    print(f"   [OK] JWT creation (length: {len(token)})")

except Exception as e:
    print(f"   [ERROR] {str(e)}")
    sys.exit(1)

# Test 4: FastAPI App
print("\n4. FastAPI Application:")
try:
    from src.main import app
    print(f"   [OK] App loads: {app.title} v{app.version}")
    print(f"   [OK] Routes registered: {len(app.routes)}")
except Exception as e:
    print(f"   [ERROR] {str(e)}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED - BACKEND READY")
print("=" * 70)
print("\nStart server: uvicorn src.main:app --reload")
print("API docs: http://localhost:8000/docs")
print("=" * 70)
