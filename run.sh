#!/bin/bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
DATA_FILE="$ROOT_DIR/data/atp_tennis.csv"
SAMPLE_FILE="$ROOT_DIR/data/sample_atp_tennis.csv"

if [ -z "${DATA_PATH:-}" ]; then
  if [ -f "$DATA_FILE" ]; then
    export DATA_PATH="$DATA_FILE"
  elif [ -f "$SAMPLE_FILE" ]; then
    echo "Main dataset not found; using the small sample dataset."
    echo "Sample data is for setup checks only and is not suitable for accuracy claims."
    export DATA_PATH="$SAMPLE_FILE"
  else
    echo "No dataset found. Add data/atp_tennis.csv or set DATA_PATH to a CSV path."
    exit 1
  fi
elif [ ! -f "$DATA_PATH" ]; then
  echo "DATA_PATH does not point to a file: $DATA_PATH"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required but not installed."
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js/npm is required but not installed."
  exit 1
fi

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Creating project virtual environment..."
  python3 -m venv "$VENV_DIR" || {
    echo "Could not create a virtual environment. Check that Python's venv module is installed."
    exit 1
  }
fi

REQUIREMENTS_HASH="$(shasum -a 256 "$ROOT_DIR/requirements.txt" | awk '{print $1}')"
HASH_FILE="$VENV_DIR/.requirements.sha256"
if [ ! -f "$HASH_FILE" ] || [ "$(cat "$HASH_FILE")" != "$REQUIREMENTS_HASH" ]; then
  echo "Installing/updating backend dependencies..."
  "$VENV_PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt" || exit 1
  printf '%s' "$REQUIREMENTS_HASH" > "$HASH_FILE"
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$FRONTEND_DIR" && npm ci) || exit 1
fi

"$VENV_PYTHON" "$ROOT_DIR/backend/app.py" > "$ROOT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
(cd "$FRONTEND_DIR" && npm run dev -- --host 0.0.0.0) > "$ROOT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo "Backend started with PID $BACKEND_PID"
echo "Frontend started with PID $FRONTEND_PID"
echo "Open http://localhost:5173"
echo "Press Ctrl+C to stop both services"

cleanup() {
  echo "Stopping backend and frontend..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  exit 0
}

trap cleanup INT TERM
wait "$BACKEND_PID" "$FRONTEND_PID"
