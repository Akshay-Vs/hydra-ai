# Build stage
FROM python:3.12-slim AS builder
WORKDIR /build

# Install uv and build tools
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files needed for build
COPY pyproject.toml uv.lock README.md ./
COPY app/ ./app/

# Create virtual environment and install build dependencies
RUN uv venv
RUN uv pip install hatchling build

# Build the wheel
RUN uv run python -m build --wheel

# Runtime stage
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy wheel from build stage
COPY --from=builder /build/dist/*.whl ./
COPY --from=builder /build/uv.lock ./

# Install dependencies and the built wheel
RUN uv pip install --system *.whl
RUN uv pip install --system gunicorn

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000
CMD ["python", "-m", "gunicorn", "app.main:asgi_app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
