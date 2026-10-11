#!/usr/bin/env bash
set -euo pipefail

# ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# cd "$ROOT"

usage() {
  echo "Usage: $0 {master|knowledge|frontend} [extra args...]"
  echo ""
  echo "  master     启动 Master 服务 (port 8000)"
  echo "  knowledge  启动 Knowledge 服务 (port 8001)"
  echo "  frontend   启动前端开发服务 (vite)"
  exit 1
}

[ $# -ge 1 ] || usage

SERVICE="$1"
shift

case "$SERVICE" in
  master)
    cd nap-backend
    uv run uvicorn nap.master.asgi:APP --reload --reload-dir nap --port 8000 "$@"
    ;;
  knowledge)
    cd nap-backend
    uv run uvicorn nap.knowledge.asgi:APP --reload --reload-dir nap --port 8001 "$@"
    ;;
  frontend)
    npm -C nap-frontend run dev "$@"
    ;;
  *)
    echo "Unknown service: $SERVICE"
    usage
    ;;
esac
