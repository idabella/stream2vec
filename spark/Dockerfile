# =============================================================================
# Stream2Vec Spark — Dockerfile
# PySpark with Kafka and MinIO connectors
# =============================================================================
# The resolved bitnami/spark:3.5.5 image is actually apache/spark whose
# entrypoint only handles K8s driver/executor CLI args and exits immediately
# when invoked with no command — causing a restart loop.
# We override ENTRYPOINT with our custom script that reads SPARK_MODE=master|worker.

FROM apache/spark:3.5.5

USER root

# Install Python dependencies
# CPU-only torch first so sentence-transformers does not pull a ~800MB CUDA wheel.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir \
    torch==2.4.1+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy Spark application code and custom entrypoint
COPY . /opt/spark/work-dir/
COPY entrypoint.sh /opt/spark/entrypoint.sh
# Strip UTF-8 BOM and convert CRLF→LF (Windows editors may add these)
RUN sed -i 's/\r//' /opt/spark/entrypoint.sh \
    && sed -i '1s/^\xEF\xBB\xBF//' /opt/spark/entrypoint.sh \
    && chmod +x /opt/spark/entrypoint.sh

WORKDIR /opt/spark/work-dir

# Switch back to the non-root spark user (uid 185 in apache/spark)
USER spark

ENTRYPOINT ["/opt/spark/entrypoint.sh"]
