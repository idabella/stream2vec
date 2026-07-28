# Stream2Vec — Backend

FastAPI backend with Clean Architecture for the Stream2Vec platform.

## Architecture

```
app/
├── api/v1/endpoints/    # HTTP handlers (thin layer)
├── core/                # Config, security, logging
├── database/            # SQLAlchemy engine and session
├── models/              # ORM models (DB tables)
├── schemas/             # Pydantic I/O models
├── repositories/        # Data access layer
├── services/            # Business logic layer
├── storage/             # MinIO + Qdrant adapters
├── messaging/           # Kafka adapters
├── middlewares/         # Request/response processing
├── exceptions/          # Custom exceptions
├── dependencies/        # FastAPI DI providers
└── utils/               # Shared helpers
```

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/documents/upload | Upload document |
| GET | /api/v1/documents/ | List documents |
| GET | /api/v1/documents/{id} | Get document |
| DELETE | /api/v1/documents/{id} | Delete document |
| GET | /api/v1/documents/{id}/status | Processing status |
| POST | /api/v1/search/ | Semantic search |

## Testing

```bash
pytest tests/ -v --cov=app
```
