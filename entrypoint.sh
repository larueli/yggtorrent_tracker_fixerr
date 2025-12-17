#!/bin/sh
set -e

LISTEN_HOST="${LISTEN_HOST:-0.0.0.0}"
LISTEN_PORT="${LISTEN_PORT:-8000}"

exec litestar run --host "$LISTEN_HOST" --port "$LISTEN_PORT" "$@"
