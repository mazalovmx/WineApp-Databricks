FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY scripts ./scripts
COPY schemas ./schemas
COPY prompts ./prompts
COPY docs ./docs
COPY tests ./tests

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
