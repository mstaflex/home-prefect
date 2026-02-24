#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy-flows.sh
#
# Registers all deployment definitions with the running Prefect server.
# Run from the repo root after the server is up.
#
# Usage:
#   ./scripts/deploy-flows.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

export PYTHONPATH="$REPO_ROOT/src"
export PREFECT_API_URL="${PREFECT_API_URL:-http://localhost:4200/api}"

echo "Deploying flows to $PREFECT_API_URL …"
python3 -m home_prefect.deployments.network
echo "Done."
