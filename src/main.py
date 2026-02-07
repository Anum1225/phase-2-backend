"""
Task API Backend - FastAPI Application

Main application entry point with CORS middleware and health check endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.database import close_db


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Task API Backend",
    description="Secure, stateless REST API for multi-user todo application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

# Explicit CORS origins including Vercel frontend and development environments
# These are merged with any environment-specific origins from settings
cors_allowed_origins = [
    "http://localhost:3000",  # Next.js development
    "http://localhost:5173",  # Vite development
    "https://hackathon-2-iota-three.vercel.app",  # Vercel production frontend
    *settings.CORS_ORIGINS,  # Additional origins from environment variables
]

# Remove duplicates while preserving order
cors_allowed_origins = list(dict.fromkeys(cors_allowed_origins))

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,  # Frontend domains
    allow_credentials=True,  # Allow cookies and Authorization headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allow all headers (including Authorization)
    expose_headers=["*"],  # Expose all headers to frontend
)


# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup handler.

    Runs once when the application starts.
    """
    print("=" * 60)
    print("Task API Backend - Starting Up")
    print("=" * 60)
    print(f"CORS Origins: {settings.CORS_ORIGINS}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print(f"JWT Algorithm: {settings.JWT_ALGORITHM}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown handler.

    Runs once when the application is shutting down.
    Closes database connections gracefully.
    """
    print("=" * 60)
    print("Task API Backend - Shutting Down")
    print("=" * 60)
    close_db()
    print("Database connections closed")
    print("=" * 60)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", tags=["System"], summary="Health check endpoint")
async def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status response

    Example:
        GET /health
        Response: {"status": "ok"}
    """
    return {"status": "ok"}


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["System"], summary="API root endpoint")
async def root() -> dict:
    """
    API root endpoint with basic information.

    Returns:
        dict: API information

    Example:
        GET /
        Response: {
            "name": "Task API Backend",
            "version": "1.0.0",
            "docs": "/docs"
        }
    """
    return {
        "name": "Task API Backend",
        "version": "1.0.0",
        "description": "Secure REST API for multi-user todo application",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(400)
async def bad_request_handler(request, exc):
    """
    Custom 400 handler with structured JSON response.

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns:
        JSONResponse: Structured error response
    """
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Bad request",
            "error_code": "BAD_REQUEST",
            "status": 400,
        },
    )


@app.exception_handler(401)
async def unauthorized_handler(request, exc):
    """
    Custom 401 handler with structured JSON response.

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns:
        JSONResponse: Structured error response
    """
    return JSONResponse(
        status_code=401,
        content={
            "detail": "Unauthorized",
            "error_code": "UNAUTHORIZED",
            "status": 401,
        },
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 handler with structured JSON response.

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns:
        JSONResponse: Structured error response
    """
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "error_code": "NOT_FOUND",
            "status": 404,
        },
    )


@app.exception_handler(422)
async def validation_error_handler(request, exc):
    """
    Custom 422 handler with structured JSON response.

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns:
        JSONResponse: Structured error response
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "status": 422,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Custom 500 handler with structured JSON response.

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns:
        JSONResponse: Structured error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "status": 500,
        },
    )


# ============================================================================
# ROUTER REGISTRATION
# ============================================================================

# Authentication endpoints
from .api.routes.auth import router as auth_router
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# Task endpoints
from .api.routes.tasks import router as tasks_router
app.include_router(tasks_router, prefix="", tags=["Tasks"])  # Tasks router already has /api/users/{user_id}/tasks prefix


# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info",
    )
