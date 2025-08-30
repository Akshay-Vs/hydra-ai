# Build stage
FROM python:3.12-slim AS builder
WORKDIR /build

# Install uv and build tools
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the entire monorepo structure to maintain relative paths
COPY packages/ ./packages/
COPY apps/server/ ./apps/server/

# Set working directory to server app
WORKDIR /build/apps/server

# First, build the local dependency (hydra-types)
WORKDIR /build/packages/python/libs/types
RUN uv venv
RUN uv add --dev build
RUN uv run python -m build --wheel

# Now build the main application
WORKDIR /build/apps/server
# Create virtual environment and install dependencies
RUN uv venv
RUN uv sync --frozen
RUN uv add --dev build

# Build the wheel
RUN uv run python -m build --wheel

# Runtime stage
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy all built wheels (including dependencies)
COPY --from=builder /build/apps/server/dist/ ./wheels/
COPY --from=builder /build/packages/python/libs/types/dist/ ./wheels/

# Install the application with all dependencies
RUN uv pip install --system --find-links ./wheels/ ./wheels/*.whl
RUN uv pip install --system gunicorn

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000
CMD ["python", "-m", "gunicorn", "app.main:asgi_app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
