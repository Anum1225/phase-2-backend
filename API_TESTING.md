# API Testing Guide

Quick reference for testing Task API Backend endpoints.

## Prerequisites

1. Server running at `http://localhost:8000`
2. Valid JWT token from signup/signin
3. User ID from token (check `/docs` for authenticated endpoints)

## Authentication Endpoints

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Response** (201):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "test@example.com",
    "created_at": "2026-02-04T12:00:00Z"
  }
}
```

### Signin
```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Response** (200): Same as signup

---

## Task Endpoints (Authenticated)

**Note**: Replace `{USER_ID}` and `{TOKEN}` with your actual values.

### Create Task
```bash
curl -X POST http://localhost:8000/api/users/{USER_ID}/tasks \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response** (201):
```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-04T12:00:00Z",
  "updated_at": "2026-02-04T12:00:00Z"
}
```

### List Tasks
```bash
curl -X GET http://localhost:8000/api/users/{USER_ID}/tasks \
  -H "Authorization: Bearer {TOKEN}"
```

**Response** (200):
```json
{
  "tasks": [
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-02-04T12:00:00Z",
      "updated_at": "2026-02-04T12:00:00Z"
    }
  ],
  "count": 1
}
```

### Get Single Task
```bash
curl -X GET http://localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  -H "Authorization: Bearer {TOKEN}"
```

**Response** (200): Same as create task response

### Update Task
```bash
# Update completed status
curl -X PUT http://localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'

# Update title and description
curl -X PUT http://localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and snacks",
    "description": "Updated description"
  }'

# Update all fields
curl -X PUT http://localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New title",
    "description": "New description",
    "completed": true
  }'
```

**Response** (200): Updated task object

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  -H "Authorization: Bearer {TOKEN}"
```

**Response** (204): No content

---

## Error Responses

### 401 Unauthorized
Missing or invalid token:
```json
{
  "detail": "Invalid or expired authentication token",
  "error_code": "UNAUTHORIZED",
  "status": 401
}
```

### 403 Forbidden
User ID mismatch or accessing another user's resource:
```json
{
  "detail": "You do not have permission to access this resource",
  "error_code": "FORBIDDEN",
  "status": 403
}
```

### 404 Not Found
Task doesn't exist:
```json
{
  "detail": "Task not found",
  "error_code": "NOT_FOUND",
  "status": 404
}
```

### 422 Validation Error
Invalid input data:
```json
{
  "detail": "Title cannot be empty",
  "error_code": "VALIDATION_ERROR",
  "status": 422
}
```

---

## Testing Workflow

### 1. Create User
```bash
# Signup
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}')

# Extract token and user_id
TOKEN=$(echo $RESPONSE | jq -r '.access_token')
USER_ID=$(echo $RESPONSE | jq -r '.user.id')

echo "Token: $TOKEN"
echo "User ID: $USER_ID"
```

### 2. Create Tasks
```bash
# Create task 1
curl -X POST http://localhost:8000/api/users/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task 1","description":"First task"}'

# Create task 2
curl -X POST http://localhost:8000/api/users/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task 2"}'
```

### 3. List Tasks
```bash
curl -X GET http://localhost:8000/api/users/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 4. Update Task
```bash
# Get task ID from list
TASK_ID="<task-id-from-list>"

# Mark as complete
curl -X PUT http://localhost:8000/api/users/$USER_ID/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

### 5. Delete Task
```bash
curl -X DELETE http://localhost:8000/api/users/$USER_ID/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## Using httpie (Alternative)

If you prefer httpie over curl:

```bash
# Signup
http POST localhost:8000/api/auth/signup email=test@example.com password=password123

# List tasks (httpie automatically formats Authorization header)
http GET localhost:8000/api/users/{USER_ID}/tasks Authorization:"Bearer {TOKEN}"

# Create task
http POST localhost:8000/api/users/{USER_ID}/tasks \
  Authorization:"Bearer {TOKEN}" \
  title="Buy groceries" \
  description="Milk, eggs, bread"

# Update task
http PUT localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  Authorization:"Bearer {TOKEN}" \
  completed:=true

# Delete task
http DELETE localhost:8000/api/users/{USER_ID}/tasks/{TASK_ID} \
  Authorization:"Bearer {TOKEN}"
```

---

## Swagger UI (Recommended)

The easiest way to test the API is through the interactive documentation:

1. Open http://localhost:8000/docs
2. Click "Authorize" button in top-right
3. Enter your JWT token: `Bearer <token>`
4. Click "Authorize" to save
5. Use the UI to test all endpoints interactively

---

## Data Isolation Testing

Verify users can only access their own tasks:

```bash
# Create user A
USER_A_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"usera@example.com","password":"password123"}')
USER_A_TOKEN=$(echo $USER_A_RESPONSE | jq -r '.access_token')
USER_A_ID=$(echo $USER_A_RESPONSE | jq -r '.user.id')

# Create user B
USER_B_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"userb@example.com","password":"password123"}')
USER_B_TOKEN=$(echo $USER_B_RESPONSE | jq -r '.access_token')
USER_B_ID=$(echo $USER_B_RESPONSE | jq -r '.user.id')

# User A creates task
TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/users/$USER_A_ID/tasks \
  -H "Authorization: Bearer $USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"User A Task"}')
TASK_ID=$(echo $TASK_RESPONSE | jq -r '.id')

# User B tries to access User A's task (should fail with 403)
curl -X GET http://localhost:8000/api/users/$USER_A_ID/tasks/$TASK_ID \
  -H "Authorization: Bearer $USER_B_TOKEN"
# Expected: 403 Forbidden

# User B tries to list User A's tasks (should fail with 403)
curl -X GET http://localhost:8000/api/users/$USER_A_ID/tasks \
  -H "Authorization: Bearer $USER_B_TOKEN"
# Expected: 403 Forbidden
```

---

## Health Check

```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

---

## Common Issues

### Token Expired
JWT tokens expire after 24 hours by default. Sign in again to get a new token.

### User ID Mismatch
Ensure the user_id in the URL matches the user_id in your JWT token. Check token payload at https://jwt.io

### CORS Errors
If testing from a browser, ensure your frontend URL is in the CORS_ORIGINS environment variable.
