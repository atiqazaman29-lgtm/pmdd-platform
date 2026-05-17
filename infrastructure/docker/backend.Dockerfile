FROM python:3.11-slim as builder

WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

COPY . /app

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./backend /app/backend
COPY ./agents /app/agents
COPY ./memory /app/memory
COPY ./orchestration /app/orchestration
COPY ./reporting /app/reporting
COPY ./validation /app/validation

# Run uvicorn securely as non-root
RUN useradd -m pmdd_user
USER pmdd_user

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
