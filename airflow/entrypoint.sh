#!/bin/bash
# =============================================================================
# Stream2Vec Airflow — Entrypoint
# Starts scheduler + webserver (not `standalone`, which times out under load).
# Copies DAGs from the bind mount into a container-local folder so Windows
# Docker bind mounts do not crash the DAG parser with Errno 5.
# =============================================================================
set -euo pipefail

DAGS_LOCAL="${AIRFLOW__CORE__DAGS_FOLDER:-/opt/airflow/dags}"
DAGS_SRC="${AIRFLOW_DAGS_SRC:-/opt/airflow/dags-src}"

sync_dags() {
  mkdir -p "${DAGS_LOCAL}"
  if [ -d "${DAGS_SRC}" ]; then
    cp -a "${DAGS_SRC}/." "${DAGS_LOCAL}/" 2>/dev/null || true
  fi
}

sync_dags

echo ">>> Migrating Airflow metadata database..."
airflow db migrate

echo ">>> Ensuring admin user exists..."
airflow users create \
  --username "${_AIRFLOW_WWW_USER_USERNAME:-admin}" \
  --firstname Admin \
  --lastname Stream2Vec \
  --role Admin \
  --email "${AIRFLOW_ADMIN_EMAIL:-admin@stream2vec.local}" \
  --password "${_AIRFLOW_WWW_USER_PASSWORD:-admin}" \
  || true

# Live-reload DAGs without parsing the Windows bind mount directly
(
  while true; do
    sync_dags
    sleep 20
  done
) &

echo ">>> Starting Airflow scheduler..."
airflow scheduler &

echo ">>> Starting Airflow webserver on port 8080..."
exec airflow webserver --port 8080 --workers 1
