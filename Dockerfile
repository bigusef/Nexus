# =============================================================================
# Stage 1: Builder - Install dependencies at system level
# =============================================================================
FROM python:3.13-slim AS builder

# Copy UV binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /build

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install production dependencies at system level
RUN uv pip install --system --no-cache --compile-bytecode -r pyproject.toml

# Copy application code
COPY src/ ./src/
COPY cli/ ./cli/
COPY workers/ ./workers/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY locales/ ./locales/

# Install the package itself (for CLI entry points like 'nexus')
RUN uv pip install --system --no-cache --no-deps .


# =============================================================================
# Stage 2: Development - Full development environment with UV and dev tools
# =============================================================================
FROM python:3.13-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy UV binary for development workflow
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/
COPY --from=builder /usr/local/bin/pybabel /usr/local/bin/
COPY --from=builder /usr/local/bin/arq /usr/local/bin/
COPY --from=builder /usr/local/bin/nexus /usr/local/bin/

# Copy dependency files for dev installs
COPY pyproject.toml uv.lock ./

# Install dev dependencies
RUN uv pip install --system --no-cache --group dev

# Note: Source code is mounted as volume in docker-compose for hot reloading

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# =============================================================================
# Stage 3: Production - Minimal runtime image
# =============================================================================
FROM python:3.13-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only required Python packages (no dev dependencies)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy only required binaries
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/
COPY --from=builder /usr/local/bin/pybabel /usr/local/bin/
COPY --from=builder /usr/local/bin/arq /usr/local/bin/
COPY --from=builder /usr/local/bin/nexus /usr/local/bin/

# Copy application code
COPY --from=builder /build/src ./src
COPY --from=builder /build/cli ./cli
COPY --from=builder /build/workers ./workers
COPY --from=builder /build/alembic ./alembic
COPY --from=builder /build/alembic.ini ./
COPY --from=builder /build/locales ./locales

# Create non-root user and clean up in single layer
RUN useradd --create-home --user-group --uid 1000 appuser \
    && chown -R appuser:appuser /app \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /app -type f -name "*.pyc" -delete 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -type f -name "*.pyc" -delete 2>/dev/null || true

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
