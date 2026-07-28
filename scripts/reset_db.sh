#!/bin/bash
# =============================================================
# Stream2Vec — Database Reset Script
# Drops and recreates all database tables
# =============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_warn "⚠️  This will DELETE ALL DATA in the database!"
read -rp "Are you sure? Type 'yes' to continue: " confirm

if [ "$confirm" != "yes" ]; then
    log_info "Aborted."
    exit 0
fi

log_info "Resetting database..."

# Downgrade all migrations
log_info "Running Alembic downgrade..."
docker-compose exec backend alembic downgrade base

# Upgrade to latest
log_info "Running Alembic upgrade..."
docker-compose exec backend alembic upgrade head

log_info "✅ Database reset complete!"
