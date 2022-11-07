#!/bin/sh

python3 worker.py &

uvicorn main:app --host "$HOST" --port "$PORT" --workers 1 --reload --log-level info