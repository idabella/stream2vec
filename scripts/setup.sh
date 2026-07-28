#!/bin/bash
# =============================================================
# Stream2Vec — Project Setup Script
# Initializes the development environment
# =============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "Setting up Stream2Vec development environment..."

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &>/dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &>/dev/null; then
    log_error "Docker Compose is not installed."
    exit 1
fi

log_info "Docker version: $(docker --version)"
log_info "Docker Compose version: $(docker-compose --version)"

# Setup environment file
if [ ! -f ".env" ]; then
    log_info "Creating .env from .env.example..."
    cp .env.example .env
    log_warn "Please edit .env and fill in your configuration values."
else
    log_info ".env already exists — skipping."
fi

# Build Docker images
log_info "Building Docker images..."
docker-compose build --no-cache

# Start infrastructure services
log_info "Starting infrastructure services..."
docker-compose up -d postgres zookeeper kafka minio qdrant

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 15

# Run database migrations
log_info "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# Create Kafka topics
log_info "Creating Kafka topics..."
docker-compose up kafka-init

log_info "✅ Stream2Vec setup complete!"
log_info "Run 'make up' to start all services."
log_info "API docs available at: http://localhost:8000/docs"
