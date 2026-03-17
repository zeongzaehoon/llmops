FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR=/root/.cache/uv

WORKDIR /home/app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8888

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
# CMD ["uv", "run", "gunicorn", "-c", "gunicorn.config.py", "main:app"]
