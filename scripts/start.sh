#!/bin/bash
# =============================================================================
# Stream2Vec — Script de démarrage
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Démarrage de Stream2Vec..."

# Vérifier que .env existe
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "❌ Fichier .env introuvable."
    echo "   Exécutez : cp .env.example .env"
    exit 1
fi

# Démarrer la stack Docker
cd "$PROJECT_DIR"
docker compose up -d

echo ""
echo "✅ Stream2Vec démarré !"
echo ""
echo "   API Backend : http://localhost:8000"
echo "   API Docs    : http://localhost:8000/docs"
echo "   MinIO       : http://localhost:9001"
echo "   Airflow     : http://localhost:8088"
echo "   Grafana     : http://localhost:3000"
echo "   Qdrant      : http://localhost:6333/dashboard"
echo ""
echo "   Logs : docker compose logs -f"
