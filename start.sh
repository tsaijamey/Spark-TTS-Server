#!/bin/bash
source .venv/bin/activate
source .env
uvicorn app.main:app --host $HOST --port $PORT --reload