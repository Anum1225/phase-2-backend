"""
Security utilities for password hashing and JWT token management.

Implements bcrypt password hashing with 12 salt rounds and JWT tokens
using HS256 algorithm for authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from .config import settings


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt with 12 salt rounds.

    Args:
        password: Plain-text password to hash

    Returns:
        Bcrypt hashed password (60 characters)

    Example:
        hashed = hash_password("mypassword123")
        # Returns: "$2b$12$..."
    """
    # Generate salt with 12 rounds (balance between security and performance)
    salt = bcrypt.gensalt(rounds=12)

    # Hash password with salt
    password_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # Return as UTF-8 string for database storage
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Args:
        plain_password: Plain-text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        is_valid = verify_password("mypassword123", stored_hash)
        if is_valid:
            print("Password correct")
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # bcrypt.checkpw handles timing-safe comparison
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

def create_access_token(user_id: str, email: Optional[str] = None, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for authenticated user.

    Args:
        user_id: User's unique identifier (UUID as string)
        email: User's email address (optional, included in token claims)
        expires_delta: Optional custom expiration time (default: 24 hours)

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            email="user@example.com"
        )
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    # Set expiration time
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    expire = datetime.utcnow() + expires_delta

    # Create JWT payload with standard claims
    payload: Dict[str, Any] = {
        "sub": user_id,  # Subject: user identifier
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at time
    }

    # Add email claim if provided
    if email:
        payload["email"] = email

    # Encode token with secret and algorithm
    token = jwt.encode(
        payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and verify JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        User ID (str) if token is valid, None otherwise

    Raises:
        No exceptions raised - returns None on any error

    Example:
        user_id = decode_access_token(token)
        if user_id:
            print(f"Authenticated as user {user_id}")
        else:
            print("Invalid or expired token")
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token, settings.BETTER_AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user ID from 'sub' claim
        user_id: Optional[str] = payload.get("sub")

        return user_id

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None

    except jwt.InvalidTokenError:
        # Token is invalid (malformed, wrong signature, etc.)
        return None

    except Exception:
        # Catch-all for any other errors
        return None


# ============================================================================
# TOKEN VALIDATION HELPERS
# ============================================================================

def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired without full verification.

    Args:
        token: JWT token string to check

    Returns:
        True if expired, False if valid or cannot determine

    Note: This does not verify signature, only expiration claim.
    """
    try:
        # Decode without verification (just to check expiration)
        payload = jwt.decode(
            token, options={"verify_signature": False}, algorithms=[settings.JWT_ALGORITHM]
        )

        exp = payload.get("exp")
        if exp is None:
            return True

        # Check if current time is past expiration
        return datetime.utcnow() > datetime.fromtimestamp(exp)

    except Exception:
        return True


def extract_token_from_header(authorization_header: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization_header: Full Authorization header value

    Returns:
        Token string if valid format, None otherwise

    Example:
        token = extract_token_from_header("Bearer eyJhbGci...")
        # Returns: "eyJhbGci..."
    """
    if not authorization_header:
        return None

    # Expected format: "Bearer <token>"
    parts = authorization_header.split()

    if len(parts) != 2:
        return None

    scheme, token = parts

    if scheme.lower() != "bearer":
        return None

    return token
