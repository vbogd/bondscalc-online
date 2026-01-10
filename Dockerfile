# Build stage
FROM docker.io/astral/uv:python3.14-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# Omit development dependencies
ENV UV_NO_DEV=1
# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --group production

# Runtime stage
FROM docker.io/python:3.14-slim

ENV DASH_DEBUG_MODE False
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY src/ .

ENV PATH="/app/.venv/bin:$PATH"
ENV DASH_DEBUG_MODE False
ENV PYTHONUNBUFFERED=1

EXPOSE 8050

CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "app:server"]
