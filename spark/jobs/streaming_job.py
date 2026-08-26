"""
Stream2Vec — Spark Structured Streaming Job.

Main entry point for the document processing pipeline.

Pipeline:
  Kafka (documents.raw)
  → JSON parse
  → Text Extraction (MinIO download + pdfplumber/docx/txt)
  → Text Cleaning
  → Chunking (sliding window, 2000 chars, 200 overlap)
  → Embedding (sentence-transformers/all-MiniLM-L6-v2, 384-dim)
  → Qdrant upsert + PostgreSQL status update

Usage:
  spark-submit \\
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \\
    jobs/streaming_job.py
"""

import logging
import os
import sys

# ---------------------------------------------------------------------------
# Ensure the Spark work-dir is on sys.path so local modules are importable:
#   writers/, extractors/, embeddings/, chunkers/, cleaners/
# Hardcode /opt/spark/work-dir as primary path (reliable regardless of how
# spark-submit resolves __file__), then fall back to __file__-relative path.
# ---------------------------------------------------------------------------
_HARDCODED_WORK_DIR = "/opt/spark/work-dir"
_FILE_WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in [_HARDCODED_WORK_DIR, _FILE_WORK_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ArrayType,
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schema for Kafka message payload
# ---------------------------------------------------------------------------

KAFKA_MESSAGE_SCHEMA = StructType([
    StructField("event", StringType(), True),
    StructField("document_id", StringType(), False),
    StructField("filename", StringType(), False),
    StructField("minio_path", StringType(), False),
    StructField("content_type", StringType(), True),
    StructField("file_size", IntegerType(), True),
])

# Schema returned by the extract → clean → chunk → embed UDF
CHUNK_WITH_VECTOR_SCHEMA = ArrayType(
    StructType([
        StructField("chunk_index", IntegerType(), False),
        StructField("text", StringType(), False),
        StructField("vector", ArrayType(FloatType()), False),
    ])
)


# ---------------------------------------------------------------------------
# Spark session
# ---------------------------------------------------------------------------

def create_spark_session() -> SparkSession:
    """Create and configure the SparkSession for the streaming job."""
    app_name = os.environ.get("SPARK_APP_NAME", "Stream2Vec")
    master   = os.environ.get("SPARK_MASTER", "local[*]")
    kafka_bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

    return (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
        )
        .getOrCreate()
    )


# ---------------------------------------------------------------------------
# UDFs
# ---------------------------------------------------------------------------

def _process_document(document_id: str, minio_path: str, filename: str) -> list:
    """Combined UDF: download → extract → clean → chunk → embed.

    One Python call per document avoids a shuffle/groupBy and keeps the
    streaming sink in append mode. Failures mark the document as failed
    so it does not stay pending forever.
    """
    from writers.qdrant_writer import mark_document_failed, mark_document_processing

    try:
        mark_document_processing(document_id)
    except Exception as exc:
        logger.warning("Could not mark document %s as processing: %s", document_id, exc)

    try:
        from extractors.text_extractor import extract_text_from_minio
        from cleaners.text_cleaner import clean_text
        from chunkers.text_chunker import chunk_text_to_dicts
        from embeddings.sentence_transformer import embed_texts

        raw_text = extract_text_from_minio(minio_path, filename)
        clean = clean_text(raw_text)
        chunks = chunk_text_to_dicts(clean)
        if not chunks:
            mark_document_failed(document_id, "No text extracted from document")
            return []

        vectors = embed_texts([c["text"] for c in chunks])
        if len(vectors) != len(chunks) or any(not v for v in vectors):
            mark_document_failed(document_id, "Embedding failed for one or more chunks")
            return []

        return [
            {
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "vector": vector,
            }
            for chunk, vector in zip(chunks, vectors)
        ]
    except Exception as exc:
        logger.error("process_document failed for %s: %s", document_id, exc)
        try:
            mark_document_failed(document_id, str(exc))
        except Exception as pg_exc:
            logger.error("Could not mark document %s as failed: %s", document_id, pg_exc)
        return []


# ---------------------------------------------------------------------------
# Stream processing
# ---------------------------------------------------------------------------

def read_kafka_stream(spark: SparkSession) -> DataFrame:
    """Subscribe to the documents.uploaded Kafka topic."""
    return (
        spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        )
        .option("subscribe", os.environ.get("KAFKA_TOPIC_INPUT", "documents.raw"))
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )


def build_pipeline(raw_stream: DataFrame, spark: SparkSession) -> DataFrame:
    """Apply the full processing pipeline to the raw Kafka stream.

    Returns a DataFrame with columns:
        document_id, chunk_index, text, vector
    ready for the Qdrant foreachBatch sink.
    """
    process_document_udf = F.udf(_process_document, CHUNK_WITH_VECTOR_SCHEMA)

    parsed = (
        raw_stream
        .select(F.from_json(F.col("value").cast("string"), KAFKA_MESSAGE_SCHEMA).alias("msg"))
        .select("msg.*")
        .filter(F.col("document_id").isNotNull())
    )

    processed = parsed.withColumn(
        "chunks",
        process_document_udf(
            F.col("document_id"),
            F.col("minio_path"),
            F.col("filename"),
        ),
    )

    return (
        processed
        .filter(F.size("chunks") > 0)
        .withColumn("chunk", F.explode("chunks"))
        .select(
            F.col("document_id"),
            F.col("chunk.chunk_index").alias("chunk_index"),
            F.col("chunk.text").alias("text"),
            F.col("chunk.vector").alias("vector"),
        )
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for spark-submit."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")  # reduce JVM noise

    logger.info("Stream2Vec streaming job starting")

    from writers.qdrant_writer import write_batch

    raw = read_kafka_stream(spark)
    pipeline = build_pipeline(raw, spark)

    query = (
        pipeline.writeStream
        .outputMode("append")
        .foreachBatch(write_batch)
        .option(
            "checkpointLocation",
            os.environ.get("SPARK_CHECKPOINT_DIR", "/tmp/stream2vec/checkpoints"),
        )
        .trigger(processingTime=os.environ.get("SPARK_TRIGGER_INTERVAL", "30 seconds"))
        .start()
    )

    logger.info("Streaming query started — awaiting termination")
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        logger.info("Interrupted by user, stopping query")
        query.stop()
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
