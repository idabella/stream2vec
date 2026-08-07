# Architecture — Stream2Vec

## Vue d'ensemble

Stream2Vec est une plateforme Cloud-Native d'ingestion et vectorisation de documents.
Elle est conçue selon les principes **Event-Driven Architecture** et **Clean Architecture**.

## Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                               │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                            │
│         (Ingestion API + Metadata + Search API)             │
└────────────┬─────────────────────────────┬──────────────────┘
             │                             │
    ┌────────▼──────┐             ┌────────▼──────┐
    │    MinIO      │             │  PostgreSQL    │
    │ (Raw Files)   │             │ (Metadata)     │
    └────────┬──────┘             └───────────────┘
             │ Event
    ┌────────▼──────┐
    │    Kafka      │
    │  (Broker)     │
    └────────┬──────┘
             │ Stream
    ┌────────▼──────────────────────────┐
    │     Spark Structured Streaming    │
    │  Extract → Clean → Chunk → Embed  │
    └────────┬──────────────────────────┘
             │
    ┌────────▼──────┐
    │    Qdrant     │
    │ (Vector DB)   │
    └───────────────┘
```

## Composants

### Backend (FastAPI)

- **Rôle** : Point d'entrée REST, gestion des métadonnées
- **Responsabilités** : Validation, persistance PostgreSQL, upload MinIO, publication Kafka
- **Pattern** : Clean Architecture (API → Service → Repository)

### MinIO

- **Rôle** : Stockage objet des fichiers bruts (compatible S3)
- **Bucket principal** : `documents`

### Apache Kafka

- **Rôle** : Message broker découplant l'ingestion du traitement
- **Topic principal** : `documents.raw`

### Spark Structured Streaming

- **Rôle** : Traitement distribué du pipeline de vectorisation
- **Mode** : Streaming (micro-batches depuis Kafka)

### Qdrant

- **Rôle** : Base de données vectorielle pour la recherche sémantique
- **Collection principale** : `documents`

### PostgreSQL

- **Rôle** : Persistance des métadonnées (statut, historique)

## Décisions d'architecture

### Pourquoi Kafka plutôt qu'un appel direct à Spark ?

Kafka découple l'ingestion du traitement. Le backend peut répondre instantanément
sans attendre la fin du traitement. Spark peut scaler indépendamment.

### Pourquoi MinIO ?

MinIO est compatible S3, ce qui permet une migration transparente vers AWS S3
sans changer le code applicatif.

### Pourquoi Qdrant ?

Qdrant est optimisé pour la recherche vectorielle avec support natif du filtrage
sur les métadonnées et des distances cosinus/dot product.

## TODO

- [ ] Ajouter un diagramme de séquence pour le flux d'ingestion
- [ ] Documenter les décisions de design (ADRs)
- [ ] Décrire la stratégie de scalabilité
- [ ] Documenter la stratégie de sécurité
