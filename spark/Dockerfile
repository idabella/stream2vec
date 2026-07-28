# =============================================================
# Stream2Vec Spark — Dockerfile
# Based on official Bitnami Spark image
# =============================================================

FROM bitnami/spark:3.5.0

USER root

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy Spark application code
COPY . /opt/spark/app

# Set working directory
WORKDIR /opt/spark/app

# Switch back to non-root user
USER 1001

# Default command (overridden by docker-compose)
CMD ["spark-class", "org.apache.spark.deploy.master.Master"]
