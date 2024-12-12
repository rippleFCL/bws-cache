FROM python:3.12-slim-bookworm as requirement-builder

WORKDIR /app

COPY ./pyproject.toml /app
COPY ./poetry.lock /app

RUN pip install --no-cache-dir poetry

RUN poetry export --without-hashes -f requirements.txt --output requirements.txt

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

ENV ORG_ID=

WORKDIR /app

COPY --from=requirement-builder /app/requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "uvicorn", "server:api", "--host", "0.0.0.0" "--port" "5000" ]
