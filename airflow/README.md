# Stream2Vec — Airflow Orchestration

Apache Airflow DAGs for pipeline orchestration.

## DAGs

| DAG | Schedule | Description |
|-----|----------|-------------|
| `stream2vec_pipeline` | */15 * * * * | Main processing pipeline |

## Setup

```bash
# Initialize Airflow DB
airflow db init

# Create admin user
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@stream2vec.io

# Start services
airflow webserver --port 8081 &
airflow scheduler
```

## Access

- Webserver: http://localhost:8081
- Default credentials: admin / admin
