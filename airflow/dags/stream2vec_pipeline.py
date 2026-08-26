"""
Stream2Vec — Main Airflow DAG.

Supervises the streaming pipeline (does not replace spark-job):
1. Health-check backend, Qdrant, Spark master
2. List pending documents in PostgreSQL
3. Confirm the Stream2Vec Spark streaming app is registered
4. Re-publish pending documents to Kafka so spark-job can consume them
5. Verify Qdrant indexation against PostgreSQL chunk counts
6. Data quality: stuck jobs, Kafka topic, MinIO

Schedule: Every 15 minutes
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

default_args: Dict[str, Any] = {
    "owner": "stream2vec-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=20),
}

POSTGRES_DSN = os.environ.get(
    "POSTGRES_DSN",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://stream2vec:stream2vec@postgres:5432/stream2vec",
    ),
).replace("postgresql+asyncpg://", "postgresql://")

QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_HTTP_PORT", os.environ.get("QDRANT_PORT", "6333")))
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION_DOCUMENTS", "documents")
SPARK_MASTER_UI = os.environ.get("SPARK_MASTER_UI", "http://spark-master:8080")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC_DOCUMENTS", "documents.raw")
STUCK_JOB_THRESHOLD_MINUTES = int(os.environ.get("STUCK_JOB_THRESHOLD_MINUTES", "60"))


def check_pending_documents(**context: Any) -> Dict[str, Any]:
    """Query PostgreSQL for documents with status='pending'."""
    import psycopg2  # type: ignore

    log.info("Connecting to PostgreSQL to check pending documents")
    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, filename, created_at
                FROM documents
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 500
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    pending_ids = [str(row[0]) for row in rows]
    result = {"pending_count": len(pending_ids), "document_ids": pending_ids}
    log.info("Found %d pending documents", len(pending_ids))
    context["ti"].xcom_push(key="pending_documents", value=result)
    return result


def ensure_spark_streaming(**context: Any) -> Dict[str, Any]:
    """Confirm the Stream2Vec streaming app is registered on the Spark master."""
    import requests  # type: ignore

    url = f"{SPARK_MASTER_UI.rstrip('/')}/json/"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    apps = data.get("activeapps") or data.get("activeApps") or []
    names = [str(app.get("name", "")) for app in apps]
    running = any("Stream2Vec" in name or "streaming_job" in name for name in names)
    result = {"spark_app_running": running, "active_apps": names, "master": data.get("url")}
    if not running:
        raise RuntimeError(
            "Spark streaming job is not registered on the master. "
            "Start the spark-job service: docker compose up -d spark-job. "
            f"Active apps: {names}"
        )
    log.info("Spark streaming app is running: %s", names)
    return result


def requeue_pending_documents(**context: Any) -> Dict[str, Any]:
    """Re-publish pending documents to Kafka so spark-job can consume them.

    Needed because the Spark source uses startingOffsets=latest: events
    published while spark-job was down are never read otherwise.
    """
    import psycopg2  # type: ignore
    from kafka import KafkaProducer  # type: ignore

    ti = context["ti"]
    pending = ti.xcom_pull(task_ids="check_pending_documents", key="pending_documents") or {}
    if pending.get("pending_count", 0) == 0:
        log.info("No pending documents to requeue.")
        return {"requeued": 0}

    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, filename, minio_path, content_type, file_size
                FROM documents
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 500
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
        acks="all",
    )
    count = 0
    try:
        for doc_id, filename, minio_path, content_type, file_size in rows:
            key = str(doc_id)
            payload = {
                "event": "document.uploaded",
                "document_id": key,
                "filename": filename,
                "content_type": content_type,
                "file_size": int(file_size or 0),
                "minio_path": minio_path,
            }
            producer.send(KAFKA_TOPIC, key=key, value=payload)
            count += 1
        producer.flush(timeout=30)
    finally:
        producer.close()

    log.info("Requeued %d pending documents to %s", count, KAFKA_TOPIC)
    return {"requeued": count, "topic": KAFKA_TOPIC}


def verify_qdrant_indexation(**context: Any) -> Dict[str, Any]:
    """Compare PostgreSQL chunk_count to Qdrant point counts via HTTP."""
    import psycopg2  # type: ignore
    import requests  # type: ignore

    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, filename, chunk_count
                FROM documents
                WHERE status = 'completed'
                  AND updated_at >= NOW() - INTERVAL '30 minutes'
                LIMIT 50
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        log.info("No recently completed documents to verify.")
        return {"checked": 0, "discrepancies": []}

    discrepancies = []
    count_url = f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{QDRANT_COLLECTION}/points/count"
    for doc_id, filename, expected_chunks in rows:
        doc_id_str = str(doc_id)
        resp = requests.post(
            count_url,
            json={
                "filter": {
                    "must": [
                        {"key": "document_id", "match": {"value": doc_id_str}}
                    ]
                },
                "exact": True,
            },
            timeout=15,
        )
        resp.raise_for_status()
        actual = int(resp.json().get("result", {}).get("count", 0))
        if actual != expected_chunks:
            discrepancies.append(
                {
                    "document_id": doc_id_str,
                    "filename": filename,
                    "expected": expected_chunks,
                    "actual": actual,
                }
            )
            log.warning(
                "Qdrant discrepancy for %s: expected=%d actual=%d",
                filename,
                expected_chunks,
                actual,
            )

    log.info(
        "Qdrant verification: checked=%d discrepancies=%d",
        len(rows),
        len(discrepancies),
    )
    return {"checked": len(rows), "discrepancies": discrepancies}


def run_data_quality_checks(**context: Any) -> Dict[str, Any]:
    """Stuck documents, Kafka topic presence, MinIO reachability."""
    import psycopg2  # type: ignore

    results: Dict[str, Any] = {"checks_passed": 0, "checks_failed": 0, "details": {}}

    try:
        conn = psycopg2.connect(POSTGRES_DSN)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*), array_agg(id::text)
                    FROM documents
                    WHERE status = 'processing'
                      AND updated_at < NOW() - (%s * INTERVAL '1 minute')
                    """,
                    (STUCK_JOB_THRESHOLD_MINUTES,),
                )
                stuck_count, stuck_ids = cur.fetchone()
        finally:
            conn.close()

        stuck_ids = stuck_ids or []
        results["details"]["stuck_documents"] = {
            "count": stuck_count,
            "ids": stuck_ids[:20],
        }
        if stuck_count > 0:
            log.warning("%d documents stuck in processing state", stuck_count)
            results["checks_failed"] += 1
        else:
            results["checks_passed"] += 1
    except Exception as exc:
        log.error("Stuck-job check failed: %s", exc)
        results["details"]["stuck_documents"] = {"error": str(exc)}
        results["checks_failed"] += 1

    try:
        from kafka import KafkaConsumer  # type: ignore

        consumer = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP)
        topics = consumer.topics()
        consumer.close()
        present = KAFKA_TOPIC in topics
        results["details"]["kafka_topic"] = {
            "topic": KAFKA_TOPIC,
            "present": present,
        }
        if present:
            results["checks_passed"] += 1
        else:
            results["checks_failed"] += 1
    except Exception as exc:
        log.warning("Kafka topic check skipped: %s", exc)
        results["details"]["kafka_topic"] = {"skipped": str(exc)}

    try:
        import urllib.request

        minio_endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
        urllib.request.urlopen(f"http://{minio_endpoint}/minio/health/live", timeout=5)
        results["details"]["minio"] = {"status": "healthy"}
        results["checks_passed"] += 1
    except Exception as exc:
        log.error("MinIO health check failed: %s", exc)
        results["details"]["minio"] = {"status": "unreachable", "error": str(exc)}
        results["checks_failed"] += 1

    overall = "ok" if results["checks_failed"] == 0 else "degraded"
    results["status"] = overall
    log.info(
        "Data quality: %s (passed=%d failed=%d)",
        overall,
        results["checks_passed"],
        results["checks_failed"],
    )
    return results


with DAG(
    dag_id="stream2vec_pipeline",
    default_args=default_args,
    description="Supervise Stream2Vec Spark streaming and requeue pending documents",
    schedule="*/15 * * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=False,
    tags=["stream2vec", "nlp", "vectorization"],
) as dag:

    start = EmptyOperator(task_id="start")

    health_check = BashOperator(
        task_id="health_check",
        bash_command="""
            set -e
            echo "Checking service health..."
            curl -sf http://backend:8000/health >/dev/null
            echo "Backend OK"
            curl -sf http://qdrant:6333/healthz >/dev/null
            echo "Qdrant OK"
            curl -sf http://spark-master:8080 >/dev/null
            echo "Spark master OK"
        """,
    )

    check_documents = PythonOperator(
        task_id="check_pending_documents",
        python_callable=check_pending_documents,
    )

    ensure_spark = PythonOperator(
        task_id="ensure_spark_streaming",
        python_callable=ensure_spark_streaming,
    )

    requeue_pending = PythonOperator(
        task_id="requeue_pending_documents",
        python_callable=requeue_pending_documents,
    )

    verify_indexation = PythonOperator(
        task_id="verify_qdrant_indexation",
        python_callable=verify_qdrant_indexation,
    )

    data_quality = PythonOperator(
        task_id="data_quality_checks",
        python_callable=run_data_quality_checks,
    )

    end = EmptyOperator(task_id="end")

    (
        start
        >> health_check
        >> check_documents
        >> ensure_spark
        >> requeue_pending
        >> verify_indexation
        >> data_quality
        >> end
    )
