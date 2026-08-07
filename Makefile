# =============================================================================
# Stream2Vec — Makefile
# =============================================================================

.PHONY: help up down restart logs build clean test lint format

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Docker ---

up: ## Démarre tous les services
	docker compose up -d

down: ## Arrête tous les services
	docker compose down

restart: down up ## Redémarre tous les services

build: ## Reconstruit les images Docker
	docker compose build

logs: ## Affiche les logs de tous les services
	docker compose logs -f

logs-backend: ## Affiche les logs du backend
	docker compose logs -f backend

clean: ## Supprime les containers, volumes et images
	docker compose down -v --rmi local

# --- Backend ---

backend-shell: ## Ouvre un shell dans le container backend
	docker compose exec backend bash

migrate: ## Applique les migrations Alembic
	docker compose exec backend alembic upgrade head

migration: ## Crée une nouvelle migration Alembic
	docker compose exec backend alembic revision --autogenerate -m "$(name)"

# --- Tests ---

test: ## Lance tous les tests
	docker compose exec backend pytest tests/ -v

test-unit: ## Lance les tests unitaires
	docker compose exec backend pytest tests/unit/ -v

test-integration: ## Lance les tests d'intégration
	docker compose exec backend pytest tests/integration/ -v

# --- Qualité de code ---

lint: ## Lance le linter (ruff)
	docker compose exec backend ruff check app/

format: ## Formate le code (ruff)
	docker compose exec backend ruff format app/

typecheck: ## Vérifie les types (mypy)
	docker compose exec backend mypy app/

# --- Environnement ---

env: ## Copie .env.example vers .env
	cp .env.example .env
	@echo ".env créé. Pensez à renseigner les valeurs."
