"""
Authentication request/response schemas.

Pydantic models for signup, signin, and authentication responses.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class SignupRequest(BaseModel):
    """
    Request model for user signup.

    Attributes:
        email: User's email address (valid format required)
        password: Plain-text password (min 8 characters, will be hashed)
    """
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """
        Validate password meets minimum length requirement.

        SECURITY: Enforces minimum 8 character password policy.

        Args:
            v: Password string to validate

        Returns:
            Password if valid

        Raises:
            ValueError: If password is too short
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepass123"
            }
        }


class SigninRequest(BaseModel):
    """
    Request model for user signin.

    Attributes:
        email: User's registered email address
        password: Plain-text password to verify
    """
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepass123"
            }
        }


class AuthResponse(BaseModel):
    """
    Response model for successful authentication.

    Attributes:
        user_id: Unique user identifier
        email: User's email address
        token: JWT access token for subsequent requests
        created_at: Account creation timestamp
    """
    user_id: str
    email: str
    token: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "email": "user@example.com",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "created_at": "2026-02-04T12:34:56.789Z"
            }
        }


class ErrorResponse(BaseModel):
    """
    Structured error response model.

    Attributes:
        detail: Human-readable error message
        error_code: Machine-readable error code
        status: HTTP status code
    """
    detail: str
    error_code: str
    status: int
