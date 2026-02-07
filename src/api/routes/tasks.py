"""
Task API route handlers - CRUD operations for user tasks.

All endpoints require JWT authentication and enforce strict user ownership.
URL user_id must match authenticated user_id from JWT token.
"""

from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ...core.database import get_session
from ..deps import get_current_user, verify_user_access
from ...models.task import Task
from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse


# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(
    prefix="/api/users/{user_id}/tasks",
    tags=["Tasks"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User does not have permission"},
        404: {"description": "Not Found - Resource does not exist"},
        422: {"description": "Validation Error - Invalid input data"},
    },
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_user_ownership(
    url_user_id: str,
    authenticated_user_id: str
) -> UUID:
    """
    Validate that URL user_id matches authenticated user_id.

    Args:
        url_user_id: User ID from URL path parameter (string)
        authenticated_user_id: User ID from JWT token (string)

    Returns:
        UUID: Validated user ID as UUID object

    Raises:
        HTTPException: 403 if user_id mismatch
        HTTPException: 422 if URL user_id is not valid UUID
    """
    # Validate URL user_id is valid UUID format
    try:
        user_uuid = UUID(url_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user_id format - must be valid UUID",
        )

    # Verify URL user_id matches JWT user_id
    verify_user_access(url_user_id, authenticated_user_id)

    return user_uuid


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all tasks for user",
    description="Returns all tasks belonging to the authenticated user, ordered by creation date (newest first).",
)
async def list_tasks(
    user_id: str,
    authenticated_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskListResponse:
    """
    List all tasks for authenticated user.

    **Authorization:**
    - Requires valid JWT token
    - URL user_id must match JWT user_id

    **Business Rules:**
    - Returns only tasks where task.user_id = authenticated user_id
    - Tasks ordered by created_at DESC (newest first)
    - Returns empty array if user has no tasks (not 404)

    Args:
        user_id: User ID from URL path
        authenticated_user_id: User ID from JWT (injected)
        session: Database session (injected)

    Returns:
        TaskListResponse: List of tasks and count

    Raises:
        HTTPException: 401 if token invalid
        HTTPException: 403 if user_id mismatch
    """
    # Validate user ownership
    user_uuid = validate_user_ownership(user_id, authenticated_user_id)

    # Query tasks for authenticated user
    statement = (
        select(Task)
        .where(Task.user_id == user_uuid)
        .order_by(Task.created_at.desc())
    )
    tasks = session.exec(statement).all()

    # Convert to response format
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    return TaskListResponse(tasks=task_responses, count=len(task_responses))


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
    description="Creates a new task for the authenticated user with the provided title and optional description.",
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    authenticated_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Create new task for authenticated user.

    **Authorization:**
    - Requires valid JWT token
    - URL user_id must match JWT user_id

    **Business Rules:**
    - user_id set from JWT (ignores client-provided value)
    - completed defaults to false
    - created_at and updated_at set automatically

    Args:
        user_id: User ID from URL path
        task_data: Task creation data (title, description)
        authenticated_user_id: User ID from JWT (injected)
        session: Database session (injected)

    Returns:
        TaskResponse: Created task with generated ID and timestamps

    Raises:
        HTTPException: 401 if token invalid
        HTTPException: 403 if user_id mismatch
        HTTPException: 422 if validation fails
    """
    # Validate user ownership
    user_uuid = validate_user_ownership(user_id, authenticated_user_id)

    # Create task with authenticated user_id
    task = Task(
        user_id=user_uuid,
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks are incomplete by default
    )

    # Save to database
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single task by ID",
    description="Retrieves a specific task by ID with ownership verification.",
)
async def get_task(
    user_id: str,
    task_id: str,
    authenticated_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Get single task by ID with ownership check.

    **Authorization:**
    - Requires valid JWT token
    - URL user_id must match JWT user_id
    - Task must belong to authenticated user

    **Business Rules:**
    - Query filters by both task_id AND user_id
    - Returns 404 if task doesn't exist
    - Returns 403 if task belongs to different user

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        authenticated_user_id: User ID from JWT (injected)
        session: Database session (injected)

    Returns:
        TaskResponse: Task details

    Raises:
        HTTPException: 401 if token invalid
        HTTPException: 403 if user_id mismatch or task owned by different user
        HTTPException: 404 if task not found
        HTTPException: 422 if task_id not valid UUID
    """
    # Validate user ownership
    user_uuid = validate_user_ownership(user_id, authenticated_user_id)

    # Validate task_id format
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid task_id format - must be valid UUID",
        )

    # Query task with ownership check
    statement = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == user_uuid
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description="Updates task fields (title, description, or completed status) with ownership verification.",
)
async def update_task(
    user_id: str,
    task_id: str,
    task_data: TaskUpdate,
    authenticated_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Update task with ownership check.

    **Authorization:**
    - Requires valid JWT token
    - URL user_id must match JWT user_id
    - Task must belong to authenticated user

    **Business Rules:**
    - Partial update: only provided fields are updated
    - updated_at timestamp updated automatically
    - Validates ownership before update

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        task_data: Task update data (title, description, completed)
        authenticated_user_id: User ID from JWT (injected)
        session: Database session (injected)

    Returns:
        TaskResponse: Updated task

    Raises:
        HTTPException: 401 if token invalid
        HTTPException: 403 if user_id mismatch or task owned by different user
        HTTPException: 404 if task not found
        HTTPException: 422 if validation fails
    """
    # Validate user ownership
    user_uuid = validate_user_ownership(user_id, authenticated_user_id)

    # Validate task_id format
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid task_id format - must be valid UUID",
        )

    # Query task with ownership check
    statement = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == user_uuid
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update only provided fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Permanently deletes a task with ownership verification.",
)
async def delete_task(
    user_id: str,
    task_id: str,
    authenticated_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """
    Delete task with ownership check.

    **Authorization:**
    - Requires valid JWT token
    - URL user_id must match JWT user_id
    - Task must belong to authenticated user

    **Business Rules:**
    - Hard delete (permanent removal)
    - No recovery/undo functionality
    - Idempotent: second delete on same task returns 404

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        authenticated_user_id: User ID from JWT (injected)
        session: Database session (injected)

    Returns:
        None: 204 No Content on success

    Raises:
        HTTPException: 401 if token invalid
        HTTPException: 403 if user_id mismatch or task owned by different user
        HTTPException: 404 if task not found
        HTTPException: 422 if task_id not valid UUID
    """
    # Validate user ownership
    user_uuid = validate_user_ownership(user_id, authenticated_user_id)

    # Validate task_id format
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid task_id format - must be valid UUID",
        )

    # Query task with ownership check
    statement = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == user_uuid
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Delete task
    session.delete(task)
    session.commit()

    # 204 No Content - no return value
    return None
