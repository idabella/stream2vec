# =============================================================================
# Stream2Vec Airflow — Dockerfile
# =============================================================================

FROM apache/airflow:2.9.1-python3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
COPY entrypoint.sh /opt/airflow/entrypoint.sh
COPY dags /opt/airflow/dags-builtin
COPY plugins /opt/airflow/plugins

RUN sed -i 's/\r//' /opt/airflow/entrypoint.sh \
    && sed -i '1s/^\xEF\xBB\xBF//' /opt/airflow/entrypoint.sh \
    && chmod +x /opt/airflow/entrypoint.sh \
    && mkdir -p /opt/airflow/dags \
    && cp -a /opt/airflow/dags-builtin/. /opt/airflow/dags/ \
    && chown -R airflow:root /opt/airflow/dags /opt/airflow/plugins /opt/airflow/entrypoint.sh

USER airflow

RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
