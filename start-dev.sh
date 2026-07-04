#!/usr/bin/env bash
# Start PDF Vault worker + web UI locally (no Docker).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WORKER="$ROOT/pdf-worker"
WEB="$ROOT/web"
DATA_DIR="$ROOT/data/jobs"
VENV_PY="$WORKER/.venv/bin/python"

mkdir -p "$DATA_DIR"

resolve_python() {
  local candidate ver

  for ver in 3.12 3.11 3.10 3.9; do
    if command -v "python$ver" >/dev/null 2>&1; then
      candidate="$(command -v "python$ver")"
    elif command -v python3 >/dev/null 2>&1; then
      candidate="$(python3 -c "import sys; print(sys.executable)" 2>/dev/null || true)"
      if ! "$candidate" -c "import sys; sys.exit(0 if sys.version_info[:2] == tuple(map(int, '${ver}'.split('.'))) else 1)" 2>/dev/null; then
        candidate=""
      fi
    fi
    if [[ -n "${candidate:-}" ]] && "$candidate" -c "import sys; sys.exit(0 if sys.version_info < (3, 14) else 1)" 2>/dev/null; then
      echo "$candidate"
      return
    fi
  done

  if command -v python3 >/dev/null 2>&1; then
    candidate="$(python3 -c "import sys; print(sys.executable)")"
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info < (3, 14) else 1)" 2>/dev/null; then
      echo "$candidate"
      return
    fi
  fi

  echo "ERROR: Python 3.9–3.12 required (3.14+ is not supported yet)." >&2
  exit 1
}

bootstrap_venv() {
  local py="$1"

  if [[ -x "$VENV_PY" ]]; then
    if ! "$VENV_PY" -c "import sys; sys.exit(0 if sys.version_info < (3, 14) else 1)" 2>/dev/null; then
      echo "Removing incompatible venv (Python 3.14+)..."
      rm -rf "$WORKER/.venv"
    fi
  fi

  if [[ ! -x "$VENV_PY" ]]; then
    echo "Setting up Python venv in pdf-worker (first run only)..."
    "$py" -m venv "$WORKER/.venv"
  fi

  echo "$VENV_PY"
}

ensure_worker_deps() {
  local py="$1"
  if ! "$py" -c "import uvicorn" 2>/dev/null; then
    echo "Installing worker dependencies..."
    "$py" -m pip install -r "$WORKER/requirements.txt"
  fi
}

free_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -ti :"$port" | xargs kill -9 2>/dev/null || true
  elif command -v fuser >/dev/null 2>&1; then
    fuser -k "$port"/tcp 2>/dev/null || true
  fi
}

PYTHON="$(resolve_python)"
VENV_PY="$(bootstrap_venv "$PYTHON")"
ensure_worker_deps "$VENV_PY"

start_mac_terminal() {
  osascript <<EOF
tell application "Terminal"
  do script "cd \"$WORKER\" && export DATA_DIR=\"$DATA_DIR\" && \"$VENV_PY\" -m uvicorn main:app --host 127.0.0.1 --port 8000"
  delay 1
  do script "cd \"$WEB\" && npm run dev"
  activate
end tell
EOF
}

start_foreground() {
  echo "Starting PDF Vault (Ctrl+C stops both)..."
  echo "PDF Worker: http://localhost:8000"
  echo "Web UI:     http://localhost:3000"
  echo

  cd "$WORKER"
  export DATA_DIR
  "$VENV_PY" -m uvicorn main:app --host 127.0.0.1 --port 8000 &
  WORKER_PID=$!

  cd "$WEB"
  npm run dev &
  WEB_PID=$!

  trap 'kill "$WORKER_PID" "$WEB_PID" 2>/dev/null || true' EXIT INT TERM
  wait
}

echo "Starting PDF Vault..."
echo
echo "Stopping any existing services on ports 8000 and 3000..."
free_port 8000
free_port 3000

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
