# Task API Backend

A secure, stateless REST API backend for a multi-user todo application built with FastAPI and SQLModel.

## Architecture Overview

### Technology Stack

- **Framework**: FastAPI 0.100+
- **ORM**: SQLModel 0.0.14+
- **Database**: Neon PostgreSQL (serverless)
- **Authentication**: JWT tokens with PyJWT 2.8+
- **Password Hashing**: bcrypt 4.1+ (12 salt rounds)
- **Python**: 3.11+

### Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models
│   │   ├── user.py      # User entity
│   │   └── task.py      # Task entity
│   ├── api/             # API endpoints
│   │   ├── auth.py      # Signup/signin endpoints
│   │   ├── tasks.py     # Task CRUD endpoints
│   │   └── deps.py      # JWT authentication dependency
│   ├── core/            # Core utilities
│   │   ├── config.py    # Environment configuration
│   │   ├── security.py  # JWT and password utilities
│   │   └── database.py  # Database engine and session
│   └── main.py          # FastAPI application instance
├── tests/               # Test suite
├── schema.sql           # Database schema
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Neon PostgreSQL database (get connection string from Neon console)
- pip or uv package manager

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: Shared secret with frontend (min 32 characters)
   - `CORS_ORIGINS`: Frontend URL (e.g., http://localhost:3000)

5. **Initialize database schema**:
   ```bash
   # Connect to your Neon database and run schema.sql
   psql $DATABASE_URL -f schema.sql
   ```

### Running the Server

**Development mode** (with auto-reload):
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode**:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Sign in with credentials

### Tasks (Authenticated)

All task endpoints require JWT token in `Authorization: Bearer <token>` header.

- `GET /api/users/{user_id}/tasks` - List user's tasks
- `POST /api/users/{user_id}/tasks` - Create new task
- `GET /api/users/{user_id}/tasks/{task_id}` - Get single task
- `PUT /api/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/users/{user_id}/tasks/{task_id}` - Delete task

### Health Check

- `GET /health` - Server health status

## Security Features

1. **JWT Authentication**: All protected endpoints verify JWT signature
2. **Password Hashing**: Bcrypt with 12 salt rounds
3. **Authorization**: User ID in URL must match JWT payload
4. **Data Isolation**: All queries filtered by authenticated user ID
5. **CORS Protection**: Configured allowed origins only

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Development

### Adding New Endpoints

1. Create Pydantic request/response models
2. Implement endpoint in appropriate router (`api/auth.py` or `api/tasks.py`)
3. Add authentication dependency if needed (`Depends(get_current_user)`)
4. Register router in `main.py`
5. Add tests in `tests/`

### Database Migrations

This project uses manual SQL migrations:

1. Create new SQL file: `migrations/002_add_column.sql`
2. Apply to Neon database: `psql $DATABASE_URL -f migrations/002_add_column.sql`
3. Update SQLModel models in `src/models/`

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is correct in `.env`
- Check Neon database is active (serverless may sleep)
- Test connection: `psql $DATABASE_URL -c "SELECT 1"`

### JWT Authentication Failing

- Ensure `BETTER_AUTH_SECRET` matches frontend configuration
- Check token format: `Authorization: Bearer <token>`
- Verify token not expired (24-hour default)

### CORS Errors

- Add frontend URL to `CORS_ORIGINS` in `.env`
- Restart server after `.env` changes
- Check browser console for specific CORS error

## Production Deployment

### Environment Variables

Ensure all required variables are set:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Strong secret (32+ characters)
- `CORS_ORIGINS` - Production frontend domain (HTTPS)

### Docker Deployment

Build image:
```bash
docker build -t task-api-backend .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env task-api-backend
```

### Performance Configuration

- Enable connection pooling (default: 5 connections, max 10 overflow)
- Set worker count: `--workers 4` (CPU cores × 2 + 1)
- Use reverse proxy (nginx) for HTTPS termination

## Documentation

- **Specification**: `../specs/001-task-api-backend/spec.md`
- **Implementation Plan**: `../specs/001-task-api-backend/plan.md`
- **Data Model**: `../specs/001-task-api-backend/data-model.md`
- **API Contracts**: `../specs/001-task-api-backend/contracts/`

## License

MIT License - see LICENSE file for details
