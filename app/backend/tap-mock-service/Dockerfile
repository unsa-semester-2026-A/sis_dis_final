# =============================================================================
# tap-mock-service — Dockerfile
#
# Multi-stage build:
#   Stage 1 (builder): installs uv and resolves/exports dependencies into a
#                      standard virtualenv at /app/.venv
#   Stage 2 (runtime): copies only the venv and the application source;
#                      runs as a non-root user on port 8000.
#
# Build:   docker build -t tap-mock-service .
# Run:     docker run -p 8000:8000 tap-mock-service
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1 — builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Install uv — the same package manager used in local development.
# Pinning to a specific version guarantees reproducible builds.
COPY --from=ghcr.io/astral-sh/uv:0.4.18 /uv /usr/local/bin/uv

# Disable uv's progress output and telemetry in CI / Docker contexts.
ENV UV_NO_PROGRESS=1 \
    UV_NO_TELEMETRY=1 \
    # Place the virtualenv inside the project so Stage 2 can copy it cleanly.
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    # Do not compile .pyc files during install (saves image space; the runtime
    # stage re-enables compilation via PYTHONDONTWRITEBYTECODE=0 if needed).
    UV_COMPILE_BYTECODE=0

WORKDIR /app

# Copy only the dependency manifests first so that Docker layer caching
# avoids re-installing packages when only source code changes.
COPY pyproject.toml ./

# Install production dependencies only (no dev extras).
# --frozen  → fail if uv.lock is out of sync with pyproject.toml
# --no-dev  → skip [tool.uv.dev-dependencies]
# If uv.lock does not exist yet (first build), replace --frozen with --no-cache.
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

# Copy the application source after dependencies are cached.
COPY src/ ./src/

# -----------------------------------------------------------------------------
# Stage 2 — runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Create a non-root user and group for security.
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy the resolved virtualenv and application source from the builder stage.
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src  /app/src

# Add the virtualenv's bin directory to PATH so that `uvicorn` resolves
# without an explicit path prefix.
ENV PATH="/app/.venv/bin:$PATH" \
    # Ensure Python output is sent straight to stdout/stderr (no buffering).
    PYTHONUNBUFFERED=1 \
    # Prevent Python from writing .pyc files to disk inside the container.
    PYTHONDONTWRITEBYTECODE=1 \
    # Tell Python where to find the application package.
    PYTHONPATH="/app/src"

# Drop to non-root before exposing the port and defining the entrypoint.
USER appuser

EXPOSE 8000

# Use exec form (no shell) so that uvicorn receives SIGTERM directly and can
# perform a graceful shutdown within Docker's stop timeout.
#
# --host 0.0.0.0   → listen on all interfaces inside the container
# --port 8000      → matches EXPOSE above
# --workers 1      → single worker; InMemoryMockStore is not thread-safe
# --no-access-log  → reduce noise; structured logging handled by the app
CMD ["uvicorn", "tapp_mock.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--no-access-log"]