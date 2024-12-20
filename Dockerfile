FROM python:3.12-slim-bookworm AS requirement-builder

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml /app
COPY ./poetry.lock /app


RUN poetry export --without-hashes -f requirements.txt --output requirements.txt

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    ORG_ID= \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=5000

WORKDIR /app

COPY --from=requirement-builder /app/requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "uvicorn", "server:api" ]
