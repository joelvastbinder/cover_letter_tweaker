FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Install system dependencies including libmagic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libmagic-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies with uv
# Use --no-install-project to only install dependencies, not the project itself
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies (libmagic)
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv .venv/
COPY . .
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
