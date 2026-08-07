# Stream2Vec — Airflow

> Orchestration des pipelines avec Apache Airflow.

## Rôle

Airflow orchestre les workflows périodiques et les tâches de coordination
du pipeline Stream2Vec.

Il ne remplace pas Kafka/Spark pour le streaming temps réel,
mais gère les tâches batch et les workflows planifiés.

## DAGs

| DAG | Description | Schedule |
|-----|-------------|----------|
| `document_pipeline_dag` | Surveillance et déclenchement du pipeline | À définir |
| `reindex_dag` | Réindexation complète de Qdrant | Hebdomadaire |
| `cleanup_dag` | Nettoyage des fichiers temporaires | Quotidien |

## Accès

```bash
# Démarrer Airflow
docker compose up airflow -d

# Interface web
open http://localhost:8088
```

Identifiants par défaut : `admin` / `admin`

## Variables d'environnement

Voir `.env.example`.
