"""
Spark Jobs Package — Entry points for Spark Structured Streaming jobs.

Each job in this package is a self-contained Spark application
that can be submitted independently via spark-submit.

Jobs to implement:
    - document_pipeline: Main document processing pipeline
      (extract → clean → chunk → embed → write to Qdrant)
"""

# TODO: Import job entry points as they are implemented
# from spark.jobs.document_pipeline import run
