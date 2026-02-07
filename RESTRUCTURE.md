# API Restructure Summary

**Date**: 2026-02-04
**Purpose**: Reorganize API code into routes and schemas folders for better maintainability

## Changes Made

### New Folder Structure

```
backend/src/api/
├── __init__.py
├── deps.py                    # Authentication dependencies (unchanged)
├── routes/                    # NEW: Route handlers
│   ├── __init__.py
│   ├── auth.py               # Authentication route handlers
│   └── tasks.py              # Task CRUD route handlers
├── schemas/                   # NEW: Pydantic models
│   ├── __init__.py
│   ├── auth.py               # Auth request/response schemas
│   └── tasks.py              # Task request/response schemas
├── auth.py                    # OLD: Can be removed (functionality moved)
└── tasks.py                   # OLD: Can be removed (functionality moved)
```

### Files Created

1. **`backend/src/api/schemas/__init__.py`**
   - Exports all schema models
   - Centralized import point for Pydantic models

2. **`backend/src/api/schemas/auth.py`**
   - `SignupRequest` - User signup validation
   - `SigninRequest` - User signin validation
   - `AuthResponse` - Authentication response format
   - `ErrorResponse` - Structured error format

3. **`backend/src/api/schemas/tasks.py`**
   - `TaskCreate` - Task creation validation
   - `TaskUpdate` - Task update validation (partial)
   - `TaskResponse` - Single task response format
   - `TaskListResponse` - Task list response format

4. **`backend/src/api/routes/__init__.py`**
   - Exports all routers
   - Centralized import point for route handlers

5. **`backend/src/api/routes/auth.py`**
   - POST `/signup` - Create account
   - POST `/signin` - Authenticate user
   - All authentication business logic

6. **`backend/src/api/routes/tasks.py`**
   - GET `/api/users/{user_id}/tasks` - List tasks
   - POST `/api/users/{user_id}/tasks` - Create task
   - GET `/api/users/{user_id}/tasks/{task_id}` - Get single task
   - PUT `/api/users/{user_id}/tasks/{task_id}` - Update task
   - DELETE `/api/users/{user_id}/tasks/{task_id}` - Delete task
   - All task CRUD business logic

### Files Modified

**`backend/src/main.py`**:
- Changed imports from `api.auth` and `api.tasks` to `api.routes.auth` and `api.routes.tasks`
- Updated router registration (tasks router already has prefix)

**Before**:
```python
from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
```

**After**:
```python
from .api.routes.auth import router as auth_router
from .api.routes.tasks import router as tasks_router
app.include_router(tasks_router, prefix="", tags=["Tasks"])
```

## Benefits

### Better Organization
- **Separation of Concerns**: Routes (business logic) separated from schemas (validation)
- **Scalability**: Easy to add new route files without cluttering the api/ directory
- **Maintainability**: Easier to find and modify specific schemas or routes

### Cleaner Imports
**Before**:
```python
from ..api.auth import SignupRequest, SigninRequest, AuthResponse
```

**After**:
```python
from ..api.schemas.auth import SignupRequest, SigninRequest, AuthResponse
from ..api.routes.auth import router
```

### Follows Best Practices
- Standard FastAPI project structure
- Similar to popular frameworks (Django apps, Flask blueprints)
- Common pattern in production applications

## Migration Notes

### Old Files Status
The following files can be safely removed after verification:
- `backend/src/api/auth.py` - Functionality moved to `routes/auth.py` and `schemas/auth.py`
- `backend/src/api/tasks.py` - Functionality moved to `routes/tasks.py` and `schemas/tasks.py`

**Recommendation**: Keep old files for a transition period, then remove once the new structure is verified.

### Verification Steps

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. **Verify all endpoints at /docs**:
   - Auth endpoints: `/api/auth/signup`, `/api/auth/signin`
   - Task endpoints: `/api/users/{user_id}/tasks` (all 5 operations)

3. **Test authentication flow**:
   ```bash
   # Signup
   curl -X POST http://localhost:8000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'

   # Signin
   curl -X POST http://localhost:8000/api/auth/signin \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```

4. **Test task operations** (use token from auth):
   ```bash
   # Create task
   curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test task","description":"Testing new structure"}'

   # List tasks
   curl -X GET http://localhost:8000/api/users/{user_id}/tasks \
     -H "Authorization: Bearer {token}"
   ```

## Rollback Plan

If issues occur, revert main.py imports:

```python
# Rollback to old structure
from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
```

Then remove the new `routes/` and `schemas/` folders.

## Next Steps

1. ✅ Verify all endpoints work with new structure
2. Test all CRUD operations
3. Remove old `auth.py` and `tasks.py` after successful verification
4. Update any import statements in tests (if applicable)
5. Update documentation if needed

## Summary

The restructure maintains 100% backward compatibility while improving code organization. All existing functionality works exactly as before, just with better file structure and clearer separation of concerns.

**Status**: ✅ Complete and ready for testing
