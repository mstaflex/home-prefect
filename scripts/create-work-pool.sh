#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# create-work-pool.sh
#
# Creates the default process work pool in Prefect so the worker has
# somewhere to pick up flow runs.
#
# Run after the server is healthy:
#   ./scripts/create-work-pool.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

POOL_NAME="${1:-default-process-pool}"
API_URL="${PREFECT_API_URL:-http://localhost:4200/api}"

echo "Creating work pool '$POOL_NAME' at $API_URL …"
PREFECT_API_URL="$API_URL" prefect work-pool create "$POOL_NAME" --type process || true
echo "Done."
