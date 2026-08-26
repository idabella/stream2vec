#!/bin/bash
# =============================================================================
# Stream2Vec Spark — Custom Entrypoint
# Translates SPARK_MODE=master|worker (Bitnami convention) into the correct
# apache/spark standalone cluster startup commands.
# =============================================================================
set -e

SPARK_HOME="${SPARK_HOME:-/opt/spark}"

case "${SPARK_MODE:-master}" in
  master)
    echo ">>> Starting Spark Master..."
    exec "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.master.Master \
      --host 0.0.0.0 \
      --port 7077 \
      --webui-port 8080
    ;;
  worker)
    echo ">>> Starting Spark Worker connecting to ${SPARK_MASTER_URL}..."
    exec "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.worker.Worker \
      --webui-port 8081 \
      "${SPARK_MASTER_URL:-spark://spark-master:7077}"
    ;;
  *)
    echo "ERROR: Unknown SPARK_MODE='${SPARK_MODE}'. Must be 'master' or 'worker'." >&2
    exit 1
    ;;
esac