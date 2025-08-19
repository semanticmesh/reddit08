# Multi-stage build for Reddit08 CRE Intelligence Platform
FROM python:3.11-slim-bullseye as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim-bullseye as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r reddit08 && useradd -r -g reddit08 reddit08

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app && \
    chown -R reddit08:reddit08 /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=reddit08:reddit08 src/ /app/src/
COPY --chown=reddit08:reddit08 scripts/ /app/scripts/
COPY --chown=reddit08:reddit08 docs/ /app/docs/
COPY --chown=reddit08:reddit08 README.md /app/
COPY --chown=reddit08:reddit08 Makefile /app/
COPY --chown=reddit08:reddit08 .env.example /app/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R reddit08:reddit08 /app/data /app/logs /app/config

# Switch to non-root user
USER reddit08

# Set working directory
WORKDIR /app

# Expose port for FastAPI application
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "src.mcp.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
