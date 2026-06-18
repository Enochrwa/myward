#!/usr/bin/env bash
# Docker container entrypoint — runs migrations then starts the server.
set -euo pipefail

echo "▶ Running Alembic migrations..."
alembic upgrade head

echo "▶ Starting MyWard API..."
exec uvicorn myward.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${UVICORN_WORKERS:-4}" \
  --log-level "${LOG_LEVEL:-info}"
