FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

ENV ORG_ID=
ENV SECRET_TTL=
ENV DEBUG=false

WORKDIR /app

COPY build-requirements.txt .

RUN pip install --no-cache -r build-requirements.txt

COPY server/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "python", "server.py" ]
