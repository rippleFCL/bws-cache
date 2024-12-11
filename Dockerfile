FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

ENV ORG_ID=

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "python", "server.py" ]
