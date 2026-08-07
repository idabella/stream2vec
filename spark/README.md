# Stream2Vec — Spark

> Apache Spark Structured Streaming pipeline for document processing and vectorization.

## Rôle

Ce module contient les jobs Spark Structured Streaming qui constituent
le cœur du pipeline de traitement de Stream2Vec.

Le pipeline Spark consomme les événements Kafka, traite les documents
et indexe les vecteurs dans Qdrant.

## Pipeline

```
Kafka (documents.raw)
    ↓
Extraction (texte brut depuis PDF/DOCX/TXT)
    ↓
Nettoyage (normalisation, déduplication)
    ↓
Chunking (découpage en segments)
    ↓
Embeddings (SentenceTransformers)
    ↓
Qdrant (indexation vectorielle)
```

## Structure

```
spark/
├── jobs/          # Entry points spark-submit
├── processors/    # Orchestrateurs de pipeline
├── config/        # Configuration SparkSession
└── utils/         # Utilitaires partagés
```

## Démarrage

```bash
# Via Docker Compose
docker compose up spark-master spark-worker -d

# Soumettre un job (quand implémenté)
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark/work-dir/jobs/document_pipeline.py
```

## Variables d'environnement

Voir `.env.example`.

## Roadmap

- [ ] Implémentation de l'extraction de texte (PDF, DOCX, TXT)
- [ ] Nettoyage et normalisation du texte
- [ ] Chunking avec overlap configurable
- [ ] Intégration SentenceTransformers
- [ ] Écriture dans Qdrant
