#!/bin/bash
# Startup script for gwsGPT

set -e

echo "Starting gwsGPT API..."

# Set default values
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export LOG_LEVEL=${LOG_LEVEL:-info}
export ENVIRONMENT=${ENVIRONMENT:-production}

# Health check endpoint
echo "Application will be available at http://${HOST}:${PORT}"
echo "Health check: http://${HOST}:${PORT}/health"
echo "API docs: http://${HOST}:${PORT}/docs"

# Start the FastAPI application
exec uvicorn app_simplified.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --log-level ${LOG_LEVEL} \
    --access-log \
    --loop uvloop \
    --http httptools