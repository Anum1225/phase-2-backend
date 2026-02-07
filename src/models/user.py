"""
User model for authentication and task ownership.

Represents an authenticated user account with email/password credentials.
Uses bcrypt for password hashing and UUID for primary key.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class User(SQLModel, table=True):
    """
    User database model.

    Attributes:
        id: Unique user identifier (UUID v4)
        email: User's email address (unique, used for login)
        password_hash: Bcrypt hashed password (60 characters)
        created_at: Account creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC)

    Example:
        user = User(email="test@example.com", password_hash="$2b$12$...")
        session.add(user)
        session.commit()
    """

    __tablename__ = "users"

    # Primary key with automatic UUID generation
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Email (unique identifier for login)
    # SECURITY: Enforced unique at database level to prevent duplicate accounts
    email: str = Field(unique=True, index=True, max_length=255)

    # Password hash (NEVER store plain-text passwords)
    # SECURITY: Bcrypt output is ~60 characters, 255 allows headroom for future algorithms
    password_hash: str = Field(max_length=255)

    # Audit timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "email": "user@example.com",
                "created_at": "2026-02-04T12:34:56.789Z",
                "updated_at": "2026-02-04T12:34:56.789Z",
            }
        }
