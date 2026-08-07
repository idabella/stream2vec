#!/bin/bash
# =============================================================================
# Stream2Vec — Script d'arrêt
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Arrêt de Stream2Vec..."

cd "$PROJECT_DIR"
docker compose down

echo "✅ Stream2Vec arrêté."
