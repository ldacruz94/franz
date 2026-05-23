#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

C='\033[0;36m'  # cyan
G='\033[0;32m'  # green
Y='\033[1;33m'  # yellow
R='\033[0;31m'  # red
N='\033[0m'     # reset

log()  { echo -e "${C}[franz]${N} $*"; }
ok()   { echo -e "${G}[franz]${N} $*"; }
warn() { echo -e "${Y}[franz]${N} $*"; }
err()  { echo -e "${R}[error]${N} $*" >&2; }

PIDS=()
cleanup() {
  echo ""
  log "Stopping all services..."
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  ok "Stopped."
}
trap cleanup EXIT INT TERM

# ── Ollama ────────────────────────────────────────────────────────────────────
log "Checking Ollama..."

if ! command -v ollama &>/dev/null; then
  err "Ollama not installed. Run:"
  err "  curl -fsSL https://ollama.com/install.sh | sh"
  exit 1
fi

if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
  log "Starting Ollama..."
  ollama serve &>/tmp/franz-ollama.log &
  PIDS+=($!)
  sleep 2
else
  log "Ollama already running."
fi

if ! ollama list 2>/dev/null | grep -q "llama3.2:3b"; then
  log "Pulling llama3.2:3b (one-time download ~2 GB)..."
  ollama pull llama3.2:3b
fi

ok "Ollama ready."

# ── Backend ───────────────────────────────────────────────────────────────────
log "Starting backend..."

if [[ ! -f "$ROOT/.venv/bin/activate" ]]; then
  log "No .venv found — creating one..."
  python3 -m venv "$ROOT/.venv"
fi

source "$ROOT/.venv/bin/activate"

if ! python -c "import uvicorn" &>/dev/null; then
  log "Installing backend dependencies..."
  pip install -r "$ROOT/backend/requirements.txt" --quiet
fi
cd "$ROOT/backend"
uvicorn main:app --host 127.0.0.1 --port 8000 &>/tmp/franz-backend.log &
PIDS+=($!)
cd "$ROOT"

# Wait for backend to be ready (model loading can take ~30-60s on first run)
log "Waiting for backend (loading models)..."
for i in {1..60}; do
  if curl -sf http://localhost:8000/health &>/dev/null; then
    break
  fi
  sleep 1
  if [[ $i -eq 60 ]]; then
    err "Backend failed to start. Check: tail /tmp/franz-backend.log"
    exit 1
  fi
done
ok "Backend ready."

# ── Frontend ──────────────────────────────────────────────────────────────────
log "Starting frontend..."

export NVM_DIR="$HOME/.nvm"
if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  # shellcheck source=/dev/null
  source "$NVM_DIR/nvm.sh"
fi

if ! command -v npm &>/dev/null; then
  err "npm not found. Install Node.js via nvm:"
  err "  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash"
  err "  nvm install --lts"
  exit 1
fi

cd "$ROOT/frontend"
npm run dev &>/tmp/franz-frontend.log &
PIDS+=($!)
cd "$ROOT"

# Wait for Vite to be ready
for i in {1..15}; do
  if curl -sf http://localhost:5173 &>/dev/null; then
    break
  fi
  sleep 1
done
ok "Frontend ready."

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${G}★ Franz is running${N}"
echo -e "    Frontend  →  ${C}http://localhost:5173${N}"
echo -e "    Backend   →  ${C}http://localhost:8000${N}"
echo -e "    Ollama    →  ${C}http://localhost:11434${N}"
echo ""
echo -e "  Logs  →  tail /tmp/franz-{frontend,backend,ollama}.log"
echo -e "  Stop  →  ${Y}Ctrl+C${N}"
echo ""

wait
