# ============================================================================
# Task API Backend - Dockerfile
# ============================================================================
# Multi-stage build for optimized production image
# Python 3.11+ with FastAPI and SQLModel

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies to /install directory
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Create production image
# ============================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only (PostgreSQL client for psql)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY schema.sql ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Environment variables (defaults - override with docker run --env-file)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Start uvicorn server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Build and Run Instructions
# ============================================================================
# Build image:
#   docker build -t task-api-backend:latest .
#
# Run container (development):
#   docker run -p 8000:8000 --env-file .env task-api-backend:latest
#
# Run container (production with more workers):
#   docker run -p 8000:8000 --env-file .env \
#     task-api-backend:latest \
#     uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
#
# Run with docker-compose:
#   See docker-compose.yml for orchestration with database
