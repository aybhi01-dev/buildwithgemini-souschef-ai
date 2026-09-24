FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /bin/
WORKDIR /code
COPY ./pyproject.toml ./README.md ./
COPY ./app ./app
COPY ./frontend ./frontend
RUN uv sync
EXPOSE 8080
CMD ["uv", "run", "python", "-m", "uvicorn", "frontend.main:app", "--host", "0.0.0.0", "--port", "8080"]
