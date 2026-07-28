"""
Stream2Vec — Spark Structured Streaming Job.

Main entry point for the document processing pipeline.

Pipeline:
  Kafka (documents.uploaded)
  → Text Extraction
  → Text Cleaning
  → Chunking
  → Embedding Generation
  → Qdrant Storage

Usage:
  spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    jobs/streaming_job.py
"""

import logging
import sys
from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType

from config.spark_config import SparkConfig

logger = logging.getLogger(__name__)


def create_spark_session(config: SparkConfig) -> SparkSession:
    """Create and configure Spark session.
    
    Args:
        config: Spark configuration object.
        
    Returns:
        SparkSession: Configured Spark session.
    """
    return (
        SparkSession.builder
        .appName(config.APP_NAME)
        .master(config.MASTER_URL)
        .config("spark.sql.shuffle.partitions", config.SHUFFLE_PARTITIONS)
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
        )
        .getOrCreate()
    )


def read_kafka_stream(spark: SparkSession, config: SparkConfig) -> DataFrame:
    """Read streaming data from Kafka topic.
    
    Args:
        spark: Active Spark session.
        config: Spark configuration object.
        
    Returns:
        DataFrame: Kafka streaming DataFrame.
    """
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", config.KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", config.KAFKA_TOPIC_INPUT)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )


def define_schema() -> StructType:
    """Define the expected Kafka message schema.
    
    Returns:
        StructType: Schema for incoming Kafka messages.
    """
    return StructType([
        StructField("document_id", StringType(), False),
        StructField("filename", StringType(), False),
        StructField("minio_path", StringType(), False),
        StructField("content_type", StringType(), True),
    ])


def process_stream(df: DataFrame, schema: StructType) -> DataFrame:
    """Apply the processing pipeline to the streaming DataFrame.
    
    Args:
        df: Raw Kafka streaming DataFrame.
        schema: Expected message schema.
        
    Returns:
        DataFrame: Processed DataFrame.
    """
    # Parse JSON messages from Kafka
    parsed = df.select(
        F.from_json(F.col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    # TODO: Apply processing steps
    # Step 1: Extract text (from MinIO file)
    # Step 2: Clean text
    # Step 3: Chunk text
    # Step 4: Generate embeddings
    # Step 5: Write to Qdrant

    return parsed


def write_to_kafka_output(df: DataFrame, config: SparkConfig):
    """Write processed results back to Kafka.
    
    Args:
        df: Processed DataFrame.
        config: Spark configuration object.
    """
    return (
        df.writeStream
        .format("kafka")
        .option("kafka.bootstrap.servers", config.KAFKA_BOOTSTRAP_SERVERS)
        .option("topic", config.KAFKA_TOPIC_OUTPUT)
        .option("checkpointLocation", config.CHECKPOINT_LOCATION)
        .outputMode("append")
        .start()
    )


def main() -> None:
    """Main entry point for the Spark streaming job."""
    config = SparkConfig()
    spark = create_spark_session(config)

    logger.info("Starting Stream2Vec Spark Streaming Job")
    logger.info(f"Kafka input topic: {config.KAFKA_TOPIC_INPUT}")
    logger.info(f"Kafka output topic: {config.KAFKA_TOPIC_OUTPUT}")

    try:
        # Read from Kafka
        raw_stream = read_kafka_stream(spark, config)
        schema = define_schema()

        # Process stream
        processed = process_stream(raw_stream, schema)

        # Write output
        query = write_to_kafka_output(processed, config)

        # Await termination
        query.awaitTermination()

    except KeyboardInterrupt:
        logger.info("Streaming job stopped by user")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
