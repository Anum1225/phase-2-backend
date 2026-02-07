"""
Task request/response schemas.

Pydantic models for task CRUD operations.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Attributes:
        title: Task title (1-500 characters, required)
        description: Optional task description (max 5000 characters)
    """
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, max_length=5000, description="Optional task description")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    All fields are optional - only provided fields will be updated.

    Attributes:
        title: Updated task title (1-500 characters)
        description: Updated task description (max 5000 characters, nullable)
        completed: Updated completion status
    """
    title: str | None = Field(None, min_length=1, max_length=500, description="Updated task title")
    description: str | None = Field(None, max_length=5000, description="Updated task description")
    completed: bool | None = Field(None, description="Updated completion status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and snacks",
                "completed": True
            }
        }


class TaskResponse(BaseModel):
    """
    Response schema for single task.

    Attributes:
        id: Unique task identifier
        user_id: Owner user ID
        title: Task title
        description: Optional task description
        completed: Completion status
        created_at: Creation timestamp (ISO 8601)
        updated_at: Last update timestamp (ISO 8601)
    """
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-04T12:00:00Z",
                "updated_at": "2026-02-04T12:00:00Z"
            }
        }


class TaskListResponse(BaseModel):
    """
    Response schema for task list.

    Attributes:
        tasks: List of task objects
        count: Number of tasks returned
    """
    tasks: list[TaskResponse]
    count: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                        "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-02-04T12:00:00Z",
                        "updated_at": "2026-02-04T12:00:00Z"
                    }
                ],
                "count": 1
            }
        }
