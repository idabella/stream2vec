# Stream2Vec — Airflow

Orchestration for batch supervision of the Stream2Vec pipeline.

Airflow does **not** replace Kafka/Spark for real-time streaming. The
`spark-job` service runs Structured Streaming continuously. This DAG
health-checks dependencies, re-queues documents stuck in `pending`, and
verifies Qdrant indexation.

## DAG

| DAG | Schedule | Role |
|-----|----------|------|
| `stream2vec_pipeline` | Every 15 minutes | Health checks, Spark app presence, Kafka requeue, Qdrant QA |

## Access

```bash
docker compose up -d --build airflow
```

UI: http://localhost:8088

Credentials: `AIRFLOW_ADMIN_USERNAME` / `AIRFLOW_ADMIN_PASSWORD` from `.env`.

The DAG starts unpaused. Confirm a run:

```bash
docker compose exec airflow airflow dags unpause -y stream2vec_pipeline
docker compose exec airflow airflow dags trigger stream2vec_pipeline
docker compose exec airflow airflow dags list-runs -d stream2vec_pipeline
```
