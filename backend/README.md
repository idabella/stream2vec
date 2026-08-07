# Stream2Vec — Backend

> FastAPI REST API for document ingestion, metadata management, and search.

## Rôle

Le backend est le point d'entrée de la plateforme Stream2Vec.
Il expose une API REST pour :
- L'ingestion de documents
- La consultation des métadonnées
- La recherche sémantique (future)

## Architecture

```
app/
├── api/v1/          # Endpoints REST (routes FastAPI)
├── core/            # Configuration, logging, sécurité
├── database/        # Sessions SQLAlchemy async
├── models/          # Modèles ORM (SQLAlchemy)
├── schemas/         # Schémas de validation (Pydantic)
├── repositories/    # Accès aux données (pattern Repository)
├── services/        # Logique applicative
├── storage/         # Client MinIO
├── messaging/       # Client Kafka
├── dependencies/    # Injection de dépendances FastAPI
├── middlewares/     # Middlewares HTTP
├── exceptions/      # Exceptions et handlers
└── utils/           # Utilitaires
```

## Démarrage rapide

```bash
# Démarrer via Docker Compose (recommandé)
docker compose up backend -d

# Accéder à la documentation
open http://localhost:8000/docs

# Vérifier la santé
curl http://localhost:8000/health
```

## Variables d'environnement

Voir `.env.example` à la racine du projet.

## Migrations

```bash
# Créer une migration
make migration name=add_documents_table

# Appliquer les migrations
make migrate
```

## Tests

```bash
make test-unit
make test-integration
```
