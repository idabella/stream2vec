# =============================================================
# Stream2Vec Airflow — Dockerfile
# Based on official Apache Airflow image
# =============================================================

FROM apache/airflow:2.10.0-python3.12

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy DAGs and plugins
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
COPY config/airflow.cfg /opt/airflow/airflow.cfg

# Expose Airflow webserver port
EXPOSE 8080
