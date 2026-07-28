# Stream2Vec — Spark Processing Pipeline

Apache Spark Structured Streaming pipeline for document vectorization.

## Pipeline

```
Kafka (documents.uploaded)
  ↓ ExtractorProcessor     — Extract text from PDF/DOCX/TXT
  ↓ CleanerProcessor       — Normalize and clean text
  ↓ ChunkerProcessor       — Split into semantic chunks
  ↓ EmbeddingProcessor     — Generate vectors (SentenceTransformers)
  ↓ QdrantWriter           — Store in Qdrant
  ↓ Kafka (documents.processed)
```

## Structure

```
spark/
├── jobs/
│   └── streaming_job.py    # Main Spark entry point
├── processors/             # Pipeline orchestration
├── extractors/             # Text extraction by format
├── cleaners/               # Text normalization
├── chunkers/               # Text segmentation strategies
├── embeddings/             # Vector generation
├── writers/                # Qdrant output writers
├── utils/                  # Shared helpers
└── config/
    └── spark_config.py     # Centralized configuration
```

## Submit Job

```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  --master spark://spark-master:7077 \
  jobs/streaming_job.py
```

## Configuration

All settings are read from environment variables. See `config/spark_config.py`.
