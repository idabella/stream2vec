"""
Spark Configuration — Centralized Spark session and configuration.

Provides a factory function for creating configured SparkSession instances.
All Spark configuration is centralized here.
"""

import os
from typing import Optional

# TODO: Import pyspark when implementing Spark jobs
# from pyspark.sql import SparkSession


def create_spark_session(
    app_name: Optional[str] = None,
    master: Optional[str] = None,
) -> object:  # -> SparkSession when implemented
    """Create and configure a SparkSession for Stream2Vec.

    Configuration includes:
    - Kafka connector for Structured Streaming
    - MinIO (S3-compatible) storage connector
    - Qdrant connector settings

    Args:
        app_name: Spark application name. Defaults to APP_NAME env var.
        master: Spark master URL. Defaults to SPARK_MASTER env var.

    Returns:
        SparkSession: Configured Spark session.

    Raises:
        NotImplementedError: Until Spark integration is implemented.
    """
    _app_name = app_name or os.getenv("SPARK_APP_NAME", "Stream2Vec")
    _master = master or os.getenv("SPARK_MASTER", "local[*]")

    # TODO: Implement SparkSession creation
    # return (
    #     SparkSession.builder
    #     .appName(_app_name)
    #     .master(_master)
    #     .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints")
    #     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
    #     .getOrCreate()
    # )
    raise NotImplementedError("SparkSession not yet implemented.")
