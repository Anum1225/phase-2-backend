"""
Dependency injection utilities for FastAPI endpoints.

Provides authentication and authorization dependencies that can be injected
into endpoint functions to enforce security requirements.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.security import decode_access_token


# HTTP Bearer token scheme for Swagger UI documentation
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    FastAPI dependency that extracts and validates JWT token from Authorization header.

    Extracts user_id from verified JWT token. Raises 401 if token is missing,
    invalid, or expired.

    Usage in endpoints:
        @router.get("/protected")
        def protected_endpoint(user_id: str = Depends(get_current_user)):
            # user_id is guaranteed to be valid here
            return {"user_id": user_id}

    Args:
        credentials: HTTP Bearer token credentials (injected by FastAPI)

    Returns:
        user_id: Authenticated user's ID (UUID as string)

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or missing
    """
    # Extract token from credentials
    token = credentials.credentials

    # Decode and verify token
    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def verify_user_access(user_id: str, authenticated_user_id: str) -> None:
    """
    Verify that URL user_id matches authenticated user_id from JWT.

    This enforces that users can only access their own resources.
    Raises 403 Forbidden if user_id mismatch.

    Usage in endpoints:
        @router.get("/users/{user_id}/tasks")
        def get_tasks(
            user_id: str,
            authenticated_user_id: str = Depends(get_current_user)
        ):
            verify_user_access(user_id, authenticated_user_id)
            # Proceed with authorized operation
            ...

    Args:
        user_id: User ID from URL path parameter
        authenticated_user_id: User ID from verified JWT token

    Raises:
        HTTPException: 403 Forbidden if user_id does not match JWT user_id
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )


# ============================================================================
# OPTIONAL DEPENDENCIES
# ============================================================================

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[str]:
    """
    Optional authentication dependency for endpoints that work with/without auth.

    Returns user_id if valid token provided, None if no token.
    Does not raise exception if token is missing (unlike get_current_user).

    Usage in endpoints:
        @router.get("/public-or-private")
        def mixed_endpoint(user_id: Optional[str] = Depends(get_current_user_optional)):
            if user_id:
                # Return personalized content
                return {"message": f"Hello user {user_id}"}
            else:
                # Return public content
                return {"message": "Hello guest"}

    Args:
        credentials: Optional HTTP Bearer token credentials

    Returns:
        user_id: Authenticated user's ID if valid token provided, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    user_id = decode_access_token(token)

    return user_id
