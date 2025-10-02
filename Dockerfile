# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (if any needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Default environment for 24/7 interval mode
ENV RUN_MODE=daemon
ENV INTERVAL_SECONDS=1800
ENV TIMEZONE=Asia/Bangkok

# Use entrypoint script to load env if mounted
ENTRYPOINT ["/bin/sh", "-c", "chmod +x /app/run.sh && /app/run.sh"]