#!/bin/bash
# =============================================================================
# Stream2Vec — Script de reset complet
# ⚠️  ATTENTION : Supprime tous les volumes (données perdues)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "⚠️  ATTENTION : Ce script va supprimer TOUTES les données."
read -r -p "Êtes-vous sûr ? (oui/non) : " confirm

if [ "$confirm" != "oui" ]; then
    echo "Annulé."
    exit 0
fi

echo "🔄 Reset de Stream2Vec..."

cd "$PROJECT_DIR"
docker compose down -v --remove-orphans
docker compose build --no-cache

echo "✅ Reset terminé. Lancez './scripts/start.sh' pour redémarrer."
