# ---- builder ----------------------------------------------------------------
FROM python:3.12-slim AS builder
WORKDIR /app

# Bring in the uv binary from the official distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifests first so Docker cache is only invalidated when
# they change, not on every app code change.
COPY pyproject.toml uv.lock ./

# Install only production dependencies into an in-project venv.
# --frozen    — refuse to update the lock file (fail fast if stale)
# --no-dev    — exclude the [dependency-groups] dev group (ruff, pytest)
RUN uv sync --frozen --no-dev

# ---- runtime ----------------------------------------------------------------
FROM python:3.12-slim AS runtime
WORKDIR /app

# Non-root user — Cloud Run best practice
RUN adduser --system --no-create-home appuser

# Copy the pre-built venv from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY app/ ./app/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

# Cloud Run injects PORT at runtime; we default to 8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
