"""
Task model for todo items with user ownership.

Represents a single task belonging to a user with title, description,
and completion status. Uses UUID for primary key and foreign key relationship.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task database model.

    Attributes:
        id: Unique task identifier (UUID v4)
        user_id: Owner user ID (foreign key to users.id)
        title: Task title (1-500 characters, required)
        description: Optional task description (max 5000 characters)
        completed: Completion status (default: false)
        created_at: Task creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC)

    Foreign Keys:
        user_id references users.id ON DELETE CASCADE

    Example:
        task = Task(
            user_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            title="Buy groceries",
            description="Milk, eggs, bread"
        )
        session.add(task)
        session.commit()
    """

    __tablename__ = "tasks"

    # Primary key with automatic UUID generation
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to users table (enforces task ownership)
    # INDEX: user_id indexed for efficient filtering by owner
    # CASCADE: Tasks deleted when user is deleted
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Task title (required, non-empty)
    # VALIDATION: 1-500 characters enforced at Pydantic layer and database
    title: str = Field(max_length=500, min_length=1)

    # Task description (optional)
    # VALIDATION: Max 5000 characters, nullable
    description: Optional[str] = Field(default=None, max_length=5000)

    # Completion status (default: false for new tasks)
    completed: bool = Field(default=False)

    # Audit timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-04T12:00:00.000Z",
                "updated_at": "2026-02-04T12:00:00.000Z",
            }
        }
