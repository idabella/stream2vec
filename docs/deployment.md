# Déploiement — Stream2Vec

## Environnements

| Environnement | Description | Infrastructure |
|--------------|-------------|----------------|
| `development` | Développement local | Docker Compose |
| `staging` | Validation pré-production | À définir |
| `production` | Production | À définir (K8s / cloud) |

## Développement local

### Prérequis

- Docker >= 24.0
- Docker Compose >= 2.0
- 8 Go RAM minimum (16 Go recommandé)

### Démarrage

```bash
# 1. Cloner le projet
git clone https://github.com/votre-org/stream2vec.git
cd stream2vec

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env

# 3. Démarrer la stack
make up

# 4. Vérifier les services
make logs
```

### Ports exposés

| Service | Port |
|---------|------|
| Backend API | 8000 |
| PostgreSQL | 5432 |
| MinIO API | 9000 |
| MinIO Console | 9001 |
| Kafka | 29092 |
| Qdrant | 6333 |
| Spark Master UI | 8090 |
| Airflow | 8088 |
| Prometheus | 9090 |
| Grafana | 3000 |

## Production

### TODO

- [ ] Définir la stratégie de déploiement cloud (AWS / GCP / Azure)
- [ ] Écrire les Kubernetes manifests ou Helm charts
- [ ] Configurer CI/CD (GitHub Actions)
- [ ] Définir la stratégie de backup des données
- [ ] Configurer les certificats TLS
- [ ] Définir la stratégie de scaling
