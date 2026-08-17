#!/bin/bash

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Data files
DATA_FILE="$ROOT_DIR/data/atp_tennis.csv"
SAMPLE_FILE="$ROOT_DIR/data/sample_atp_tennis.csv"

if [ -f "$DATA_FILE" ]; then
  echo "Using dataset: $DATA_FILE"
elif [ -f "$SAMPLE_FILE" ]; then
  echo "Dataset not found. Falling back to sample dataset: $SAMPLE_FILE"
  export DATA_PATH="$SAMPLE_FILE"
else
  echo "Warning: no dataset found at $DATA_FILE and no sample available."
  echo "Place your full dataset at $DATA_FILE or create $SAMPLE_FILE, or set DATA_PATH to a CSV path."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required but not installed."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but not installed."
  exit 1
fi

cd "$BACKEND_DIR"
python3 -m pip install -q flask flask-cors pandas scikit-learn
python3 app.py > "$ROOT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

cd "$FRONTEND_DIR"
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev -- --host 0.0.0.0 > "$ROOT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo "Backend started with PID $BACKEND_PID"
echo "Frontend started with PID $FRONTEND_PID"
echo "Open http://localhost:5173"
echo "Press Ctrl+C to stop both services"

cleanup() {
  echo "Stopping backend and frontend..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  exit 0
}

trap cleanup INT TERM
wait "$BACKEND_PID" "$FRONTEND_PID"
