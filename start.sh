#!/bin/bash
set -e
source "$(dirname "$0")/.venv/bin/activate"
. "$(dirname "$0")/.env"
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload