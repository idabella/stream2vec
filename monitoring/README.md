# Stream2Vec — Monitoring

> Prometheus + Grafana stack for observability.

## Rôle

Le monitoring collecte et visualise les métriques de tous les composants
de la plateforme Stream2Vec.

## Services

| Service | URL | Rôle |
|---------|-----|------|
| Prometheus | http://localhost:9090 | Collecte de métriques |
| Grafana | http://localhost:3000 | Tableaux de bord |

## Accès Grafana

- URL : http://localhost:3000
- Identifiants : définis dans `.env` (`GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`)

## Métriques collectées

- **Backend** : Requêtes HTTP, latence, erreurs
- **Kafka** : Messages/s, lag des consumers
- **Spark** : Throughput, durée des jobs
- **Qdrant** : Requêtes de recherche, indexation
- **PostgreSQL** : Connexions, requêtes

## Roadmap

- [ ] Configurer prometheus-fastapi-instrumentator sur le backend
- [ ] Ajouter JMX Exporter pour Kafka
- [ ] Créer les dashboards Grafana par composant
- [ ] Configurer les alertes Prometheus
- [ ] Ajouter Node Exporter pour les métriques système
