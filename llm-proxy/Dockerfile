FROM arm64v8/python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /home/app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 9999

CMD ["uv", "run", "python", "main.py"]
# CMD ["uv", "run", "gunicorn", "-c", "gunicorn.config.py", "main:app"]