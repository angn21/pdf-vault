#!/usr/bin/env bash
# Start PDF Vault worker + web UI locally (no Docker).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$ROOT/data/jobs"
mkdir -p "$DATA_DIR"

free_port() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
  elif command -v fuser >/dev/null 2>&1; then
    fuser -k 8000/tcp 2>/dev/null || true
  fi
}

start_mac_terminal() {
  osascript <<EOF
tell application "Terminal"
  do script "cd \"$ROOT/pdf-worker\" && export DATA_DIR=\"$DATA_DIR\" && python3 -m uvicorn main:app --host 127.0.0.1 --port 8000"
  delay 1
  do script "cd \"$ROOT/web\" && npm run dev"
  activate
end tell
EOF
}

start_foreground() {
  echo "Starting PDF Vault (Ctrl+C stops both)..."
  echo "PDF Worker: http://localhost:8000"
  echo "Web UI:     http://localhost:3000"
  echo

  cd "$ROOT/pdf-worker"
  export DATA_DIR
  python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
  WORKER_PID=$!

  cd "$ROOT/web"
  npm run dev &
  WEB_PID=$!

  trap 'kill "$WORKER_PID" "$WEB_PID" 2>/dev/null || true' EXIT INT TERM
  wait
}

echo "Starting PDF Vault..."
echo
echo "Stopping any existing worker on port 8000..."
free_port

if [[ "$(uname -s)" == "Darwin" ]] && [[ -z "${PDF_VAULT_NO_TERMINAL:-}" ]]; then
  start_mac_terminal
  echo
  echo "Opened two Terminal windows."
  echo "PDF Worker: http://localhost:8000"
  echo "Web UI:     http://localhost:3000"
  echo
  echo "Close both windows to stop."
else
  start_foreground
fi
