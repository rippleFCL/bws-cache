FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

ENV ORG_ID=

WORKDIR /app

COPY ./pyproject.toml /work
COPY ./poetry.lock /work

RUN pip install --no-cache-dir poetry && \
    poetry export --without-hashes -f requirements.txt --output requirements.txt && \


RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "uvicorn", "server:api", "--host", "0.0.0.0" "--port" "5000" ]
