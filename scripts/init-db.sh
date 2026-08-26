#!/bin/bash
# =============================================================================
# Stream2Vec — PostgreSQL Initialization Script
#
# This script runs automatically when the PostgreSQL container starts for the
# first time (via /docker-entrypoint-initdb.d/).
#
# It creates the Airflow database and a dedicated Airflow user so that the
# main stream2vec database and the Airflow metadata database remain isolated.
#
# Environment variables are injected by Docker Compose from the .env file.
# =============================================================================

set -e

echo "[init-db] Creating Airflow database and user..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create Airflow user (skip if already exists)
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${AIRFLOW_DB_USER:-airflow}') THEN
            CREATE USER ${AIRFLOW_DB_USER:-airflow} WITH PASSWORD '${AIRFLOW_DB_PASSWORD}';
        END IF;
    END
    \$\$;

    -- Create Airflow database (skip if already exists)
    SELECT 'CREATE DATABASE ${AIRFLOW_DB_NAME:-airflow} OWNER ${AIRFLOW_DB_USER:-airflow}'
    WHERE NOT EXISTS (
        SELECT FROM pg_database WHERE datname = '${AIRFLOW_DB_NAME:-airflow}'
    )\gexec

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE ${AIRFLOW_DB_NAME:-airflow} TO ${AIRFLOW_DB_USER:-airflow};
EOSQL

echo "[init-db] Airflow database initialized successfully."
