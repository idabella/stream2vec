# =============================================================================
# Stream2Vec Backend — Dockerfile
# Multi-stage build: builder installs deps, runtime runs the app
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — Install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build-time system dependencies (gcc for native extensions, libpq-dev for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into the user site-packages.
# Using --user so they can be copied cleanly to the runtime stage.
COPY requirements.txt .
# Install torch CPU-only FIRST to avoid downloading 2.5GB of NVIDIA CUDA libraries.
# The PyTorch index provides a CPU-only wheel (~200MB instead of ~2.5GB).
RUN pip install --no-cache-dir --user \
    torch==2.3.1+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime — Minimal production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Install runtime system dependencies:
#   libpq5   → PostgreSQL client library (required by asyncpg at runtime)
#   curl     → used by the Docker HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: run as a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source (owned by appuser)
COPY --chown=appuser:appuser . .

USER appuser

# PATH: user-installed packages from builder stage
ENV PATH=/home/appuser/.local/bin:$PATH
# Ensure Python finds the app package when running from /app
ENV PYTHONPATH=/app
# Prevent Python from buffering stdout/stderr (important for Docker logs)
ENV PYTHONUNBUFFERED=1
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Docker-native health check — hits the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn; reload is disabled in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
