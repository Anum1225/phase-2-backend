"""
Test script for authentication endpoints.

This script tests the signup and signin endpoints to verify
Phase 3 (US1) implementation is working correctly.

Usage:
    python test_auth.py
"""

import httpx
import sys
from uuid import uuid4


def test_auth_endpoints():
    """Test signup and signin endpoints."""
    base_url = "http://localhost:8000"

    # Generate unique email for this test
    test_email = f"test_{uuid4().hex[:8]}@example.com"
    test_password = "securepass123"

    print("=" * 60)
    print("Testing Authentication Endpoints")
    print("=" * 60)

    # Test 1: Health check
    print("\n1. Testing health check endpoint...")
    try:
        response = httpx.get(f"{base_url}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        print("✓ Health check passed")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

    # Test 2: Signup with valid credentials
    print(f"\n2. Testing signup with email: {test_email}...")
    try:
        response = httpx.post(
            f"{base_url}/api/auth/signup",
            json={"email": test_email, "password": test_password}
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "token" in data
        assert "created_at" in data
        assert data["email"] == test_email

        user_id = data["user_id"]
        token = data["token"]

        print(f"✓ Signup successful")
        print(f"  User ID: {user_id}")
        print(f"  Token: {token[:50]}...")
    except Exception as e:
        print(f"✗ Signup failed: {e}")
        if 'response' in locals():
            print(f"  Response: {response.text}")
        return False

    # Test 3: Signup with duplicate email (should fail)
    print(f"\n3. Testing signup with duplicate email...")
    try:
        response = httpx.post(
            f"{base_url}/api/auth/signup",
            json={"email": test_email, "password": test_password}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✓ Duplicate email rejected (422)")
    except Exception as e:
        print(f"✗ Duplicate email test failed: {e}")
        if 'response' in locals():
            print(f"  Response: {response.text}")
        return False

    # Test 4: Signup with short password (should fail)
    print(f"\n4. Testing signup with short password...")
    try:
        response = httpx.post(
            f"{base_url}/api/auth/signup",
            json={"email": f"another_{uuid4().hex[:8]}@example.com", "password": "short"}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✓ Short password rejected (422)")
    except Exception as e:
        print(f"✗ Short password test failed: {e}")
        if 'response' in locals():
            print(f"  Response: {response.text}")
        return False

    # Test 5: Signin with correct credentials
    print(f"\n5. Testing signin with correct credentials...")
    try:
        response = httpx.post(
            f"{base_url}/api/auth/signin",
            json={"email": test_email, "password": test_password}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "token" in data
        assert data["user_id"] == user_id
        assert data["email"] == test_email

        print(f"✓ Signin successful")
        print(f"  User ID: {data['user_id']}")
        print(f"  Token: {data['token'][:50]}...")
    except Exception as e:
        print(f"✗ Signin failed: {e}")
        if 'response' in locals():
            print(f"  Response: {response.text}")
        return False

    # Test 6: Signin with wrong password
    print(f"\n6. Testing signin with wrong password...")
    try:
        response = httpx.post(
            f"{base_url}/api/auth/signin",
            json={"email": test_email, "password": "wrongpassword"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Wrong password rejected (401)")
    except Exception as e:
        print(f"✗ Wrong password test failed: {e}")
        if 'response' in locals():
            print(f"  Response: {response.text}")
        return False

    # Test 7: Signin with non-existent email
    print(f"\n7. Testing signin with non-existent email...")
    try:
        response = httpx.post(
            f"{base_url}/api/auth/signin",
            json={"email": "nonexistent@example.com", "password": test_password}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Non-existent email rejected (401)")
    except Exception as e:
        print(f"✗ Non-existent email test failed: {e}")
        if 'response' in locals():
            print(f"  Response: {response.text}")
        return False

    # Test 8: Verify JWT token structure
    print(f"\n8. Verifying JWT token structure...")
    try:
        import jwt
        from dotenv import load_dotenv
        import os

        load_dotenv()
        secret = os.getenv("BETTER_AUTH_SECRET")

        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        assert "sub" in decoded
        assert "email" in decoded
        assert "iat" in decoded
        assert "exp" in decoded
        assert decoded["sub"] == user_id
        assert decoded["email"] == test_email

        print("✓ JWT token structure valid")
        print(f"  Claims: sub={decoded['sub']}, email={decoded['email']}")
    except Exception as e:
        print(f"✗ JWT verification failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_auth_endpoints()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
