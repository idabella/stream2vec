# Stream2Vec — Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User / Client                         │
└─────────────────────┬───────────────────────────────────────┘
                       │ HTTP REST
┌─────────────────────▼───────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────┐ │
│  │  Documents  │ │    Search    │ │    Health / Metrics    │ │
│  │  Endpoints  │ │  Endpoints   │ │      Endpoints         │ │
│  └──────┬──────┘ └──────┬───────┘ └───────────────────────┘ │
│         │               │                                     │
│  ┌──────▼──────────────▼───────────────────────────────────┐ │
│  │              Service Layer (Business Logic)              │ │
│  └──────┬──────────────────────────────┬────────────────────┘ │
│         │                              │                      │
│  ┌──────▼──────┐              ┌────────▼──────────────────┐  │
│  │ Repository  │              │    Storage / Messaging     │  │
│  │   Layer     │              │   MinIO │ Kafka │ Qdrant   │  │
│  └──────┬──────┘              └───────────────────────────┘  │
│         │ SQLAlchemy                                          │
└─────────┼──────────────────────────────────────────────────┘ │
          │                                                      │
┌─────────▼──────┐   ┌──────────┐   ┌────────────────────────┐
│   PostgreSQL   │   │  MinIO   │   │         Kafka           │
│   (Metadata)   │   │(Objects) │   │    (Event Streaming)   │
└────────────────┘   └──────────┘   └───────────┬────────────┘
                                                  │
                                    ┌─────────────▼────────────┐
                                    │   Apache Spark            │
                                    │   Structured Streaming    │
                                    │                           │
                                    │  Extract → Clean          │
                                    │  → Chunk → Embed → Write  │
                                    └─────────────┬────────────┘
                                                  │
                                    ┌─────────────▼────────────┐
                                    │          Qdrant           │
                                    │     Vector Database       │
                                    └──────────────────────────┘
```

## Design Principles

### Clean Architecture
- **Entities** (Models): Core business objects
- **Use Cases** (Services): Business logic
- **Interface Adapters** (Repositories, APIs): Data conversion
- **Frameworks** (FastAPI, SQLAlchemy): External tools

### SOLID Principles
- **S**ingle Responsibility: Each class has one purpose
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Interface contracts respected
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions

## Data Flow

1. User uploads document via POST /api/v1/documents/upload
2. FastAPI validates file type and size
3. File stored in MinIO (raw bucket)
4. Document record created in PostgreSQL
5. Event published to Kafka topic `documents.uploaded`
6. Spark reads event from Kafka
7. Spark downloads file from MinIO
8. Text extracted from document
9. Text cleaned and normalized
10. Text split into chunks
11. Chunks vectorized with SentenceTransformers
12. Vectors stored in Qdrant
13. Event published to `documents.processed`
14. PostgreSQL status updated to `completed`
