# Testing Phase 3: User Registration and Authentication

## Prerequisites

1. **Database Setup**:
   ```bash
   # Connect to your Neon PostgreSQL database and run:
   psql <DATABASE_URL> -f schema.sql
   ```

2. **Environment Variables**:
   - Copy `.env.example` to `.env`
   - Set `DATABASE_URL` to your Neon connection string
   - Set `BETTER_AUTH_SECRET` (minimum 32 characters)

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

```bash
# From backend directory
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
# From backend directory
python src/main.py
```

## Running Tests

### Automated Test Script

```bash
python test_auth.py
```

This script tests:
- Health check endpoint
- Signup with valid credentials (201)
- Signup with duplicate email (422)
- Signup with short password (422)
- Signin with correct credentials (200)
- Signin with wrong password (401)
- Signin with non-existent email (401)
- JWT token structure validation

### Manual Testing with cURL

**Signup**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securepass123"}'
```

**Signin**:
```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securepass123"}'
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

### API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Expected Responses

### Successful Signup (201)
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "test@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "created_at": "2026-02-04T12:34:56.789Z"
}
```

### Successful Signin (200)
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "test@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "created_at": "2026-02-04T12:34:56.789Z"
}
```

### Invalid Credentials (401)
```json
{
  "detail": "Invalid email or password"
}
```

### Validation Error (422)
```json
{
  "detail": "Email already exists"
}
```

## Acceptance Criteria (Phase 3 - US1)

- [x] T019: User model created with UUID, email, password_hash, timestamps
- [x] T020: Signup endpoint validates, hashes password, creates user, returns JWT
- [x] T021: Signin endpoint verifies credentials, returns JWT
- [x] T022: Auth router registered at /api/auth
- [x] T023: Pydantic models for requests/responses implemented
- [x] T024: Error handlers for 400, 401, 422, 500 implemented

### Functional Tests

- [ ] Signup with valid email/password returns 201 and JWT token
- [ ] Signup with duplicate email returns 422
- [ ] Signin with correct credentials returns 200 and JWT token
- [ ] Signin with invalid credentials returns 401
- [ ] JWT token can be decoded and user_id extracted
- [ ] All endpoints follow contracts/auth-endpoints.md

## Security Verification

1. **Password Security**:
   - Passwords hashed with bcrypt (12 rounds)
   - Plain-text passwords never stored
   - Password minimum 8 characters enforced

2. **Token Security**:
   - JWT contains sub (user_id), email, iat, exp claims
   - Token expires after 24 hours
   - HS256 algorithm used for signing

3. **Error Handling**:
   - Generic error messages prevent email enumeration
   - "Invalid email or password" for both wrong email and wrong password

4. **Input Validation**:
   - Email format validated (Pydantic EmailStr)
   - Password length validated (minimum 8 characters)
   - Email uniqueness enforced at database level

## Troubleshooting

### Database Connection Errors
- Verify DATABASE_URL is correct in .env
- Ensure Neon database is accessible
- Check schema.sql has been executed

### JWT Token Errors
- Verify BETTER_AUTH_SECRET is set and >= 32 characters
- Ensure secret matches between signup and signin

### Import Errors
- Run `pip install -r requirements.txt`
- Ensure you're in the correct virtual environment

### Port Already in Use
- Change PORT in .env or use different port:
  ```bash
  uvicorn src.main:app --port 8001
  ```
