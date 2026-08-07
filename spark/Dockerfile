# =============================================================================
# Stream2Vec Spark — Dockerfile
# PySpark with Kafka and MinIO connectors
# =============================================================================

FROM bitnami/spark:3.5

USER root

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy Spark application code
COPY . /opt/spark/work-dir/

WORKDIR /opt/spark/work-dir

USER 1001
