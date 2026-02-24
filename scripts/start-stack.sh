#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start-stack.sh
#
# Starts the complete Prefect stack (postgres + server + worker) via Docker
# Compose and creates the default work pool if it does not exist yet.
#
# Usage:
#   ./scripts/start-stack.sh            # start in foreground (logs visible)
#   ./scripts/start-stack.sh -d         # start detached
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yml"
ENV_FILE="$REPO_ROOT/.env"

# Copy .env.example → .env if .env is missing
if [[ ! -f "$ENV_FILE" ]]; then
  echo "No .env found – copying .env.example → .env"
  cp "$REPO_ROOT/.env.example" "$ENV_FILE"
fi

echo "Starting Prefect stack …"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up "$@"
