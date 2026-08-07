"""
Airflow DAGs Package — Pipeline orchestration DAGs.

DAGs to implement:
    - document_pipeline_dag: Monitors and triggers document processing
    - reindex_dag: Full reindexing of the Qdrant collection
    - cleanup_dag: Periodic cleanup of processed documents
"""

# DAG files are auto-discovered by Airflow from this directory.
# No imports needed here.
