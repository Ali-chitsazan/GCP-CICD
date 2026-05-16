FROM python:3.10-slim

WORKDIR /app

ARG IMAGE_VERSION=local
ARG GIT_SHA=local

ENV IMAGE_VERSION=$IMAGE_VERSION
ENV GIT_SHA=$GIT_SHA

RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8080

CMD ["python", "src/app.py"]
