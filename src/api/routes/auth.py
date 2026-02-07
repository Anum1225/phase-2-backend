"""
Authentication route handlers for user signup and signin.

Implements secure user registration and login with JWT token issuance.
All passwords are hashed with bcrypt before storage.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from ...core.database import get_session
from ...core.security import hash_password, verify_password, create_access_token
from ...models.user import User
from ..schemas.auth import SignupRequest, SigninRequest, AuthResponse, ErrorResponse


# ============================================================================
# ROUTER INITIALIZATION
# ============================================================================

router = APIRouter()


# ============================================================================
# SIGNUP ENDPOINT
# ============================================================================

@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    responses={
        201: {"description": "User created successfully"},
        422: {
            "description": "Validation error (duplicate email, invalid format, weak password)",
            "model": ErrorResponse,
        },
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def signup(
    request: SignupRequest,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Create new user account and return JWT token.

    **Security Features**:
    - Password hashed with bcrypt (12 rounds) before storage
    - Email uniqueness enforced at database level
    - Minimum 8 character password requirement
    - JWT token with 24-hour expiration

    **Process**:
    1. Validate email format and password length (Pydantic)
    2. Check email uniqueness in database
    3. Hash password with bcrypt
    4. Create user record in database
    5. Generate JWT token with user_id
    6. Return user info and token

    Args:
        request: Signup request with email and password
        session: Database session (injected by FastAPI)

    Returns:
        AuthResponse with user_id, email, token, created_at

    Raises:
        HTTPException 422: If email already exists or validation fails
        HTTPException 500: If database error occurs
    """
    # Check if email already exists
    # SECURITY: Prevents duplicate accounts per email
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists",
        )

    # Hash password before storage
    # SECURITY: Never store plain-text passwords in database
    password_hash = hash_password(request.password)

    # Create new user
    new_user = User(
        email=request.email,
        password_hash=password_hash,
    )

    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except IntegrityError:
        # Handle race condition where duplicate email was inserted between check and insert
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists",
        )
    except Exception as e:
        session.rollback()
        # SECURITY: Don't expose internal error details to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account",
        )

    # Generate JWT token
    # SECURITY: Token contains user_id (sub), email, iat, exp claims
    token = create_access_token(user_id=str(new_user.id), email=new_user.email)

    # Return user info and token
    return AuthResponse(
        user_id=str(new_user.id),
        email=new_user.email,
        token=token,
        created_at=new_user.created_at,
    )


# ============================================================================
# SIGNIN ENDPOINT
# ============================================================================

@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate existing user",
    responses={
        200: {"description": "Authentication successful"},
        401: {
            "description": "Invalid credentials (wrong email or password)",
            "model": ErrorResponse,
        },
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def signin(
    request: SigninRequest,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Verify user credentials and return JWT token.

    **Security Features**:
    - Timing-safe password comparison (bcrypt.checkpw)
    - Generic error message to prevent email enumeration
    - Fresh JWT token generated on each signin
    - Failed attempts logged (future enhancement)

    **Process**:
    1. Find user by email
    2. Verify password hash with bcrypt
    3. Generate new JWT token
    4. Return user info and token

    Args:
        request: Signin request with email and password
        session: Database session (injected by FastAPI)

    Returns:
        AuthResponse with user_id, email, token, created_at

    Raises:
        HTTPException 401: If email not found or password incorrect
        HTTPException 500: If database error occurs
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    # SECURITY: Return generic error to prevent email enumeration
    # Don't reveal whether email exists or password is wrong
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password with bcrypt
    # SECURITY: bcrypt.checkpw provides timing-safe comparison
    password_valid = verify_password(request.password, user.password_hash)

    if not password_valid:
        # SECURITY: Same generic error message as above
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate new JWT token
    # SECURITY: Fresh token on each signin (no token reuse)
    token = create_access_token(user_id=str(user.id), email=user.email)

    # Return user info and token
    return AuthResponse(
        user_id=str(user.id),
        email=user.email,
        token=token,
        created_at=user.created_at,
    )
