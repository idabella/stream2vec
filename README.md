# Stream2Vec

> Plateforme Cloud-Native d'ingestion, traitement et vectorisation de documents pour applications RAG.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![Apache Spark](https://img.shields.io/badge/Spark-3.5-orange)](https://spark.apache.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Présentation

Stream2Vec est une plateforme Data Engineering conçue pour ingérer des documents, les traiter de manière asynchrone et les vectoriser pour alimenter des applications RAG (Retrieval-Augmented Generation).

Le projet suit une architecture **Cloud-Native** et est conçu pour être déployé sur des environnements de production.

---

## Objectifs

- **Ingestion** : Accepter des documents via une API REST
- **Stockage** : Persister les fichiers bruts dans MinIO (Object Storage)
- **Streaming** : Publier des événements dans Apache Kafka
- **Traitement** : Extraire, nettoyer et découper les documents avec Spark
- **Vectorisation** : Générer des embeddings via SentenceTransformers
- **Indexation** : Stocker les vecteurs dans Qdrant
- **Exploitation** : Servir les applications RAG via une API de recherche sémantique

---

## Architecture

```
Utilisateur
    ↓
FastAPI (REST API)
    ↓
MinIO (Object Storage)
    ↓
Kafka (Message Broker)
    ↓
Spark Structured Streaming
    ↓
  ┌─────────────────────┐
  │  Extraction          │
  │  Nettoyage           │
  │  Chunking            │
  │  Embeddings          │
  └─────────────────────┘
    ↓
Qdrant (Vector Database)
    ↓
Recherche Sémantique + LLM
```

---

## Technologies

| Couche | Technologie | Rôle |
|--------|------------|------|
| API | FastAPI | REST API, validation, documentation |
| Base de données | PostgreSQL + SQLAlchemy | Métadonnées des documents |
| Migrations | Alembic | Gestion du schéma de base de données |
| Object Storage | MinIO | Stockage des fichiers bruts |
| Message Broker | Apache Kafka | Découplage asynchrone |
| Traitement | Apache Spark | Pipeline de traitement distribué |
| Vectorisation | SentenceTransformers | Génération d'embeddings |
| Vector DB | Qdrant | Recherche sémantique |
| Orchestration | Apache Airflow | DAGs de coordination |
| Monitoring | Prometheus + Grafana | Métriques et tableaux de bord |
| Containerisation | Docker Compose | Déploiement local et staging |

---

## Pipeline

1. Un utilisateur soumet un document via l'API FastAPI
2. Le fichier est stocké dans MinIO
3. Un événement est publié dans Kafka
4. Spark Structured Streaming consomme l'événement
5. Le document est extrait, nettoyé et découpé en chunks
6. Les embeddings sont générés pour chaque chunk
7. Les vecteurs sont indexés dans Qdrant
8. Les applications RAG interrogent Qdrant pour la recherche sémantique

---

## Structure du projet

```
stream2vec/
├── backend/          # API FastAPI
├── spark/            # Jobs Spark Structured Streaming
├── airflow/          # DAGs Airflow
├── monitoring/       # Prometheus + Grafana
├── docs/             # Documentation technique
├── scripts/          # Scripts utilitaires
├── tests/            # Tests globaux
├── frontend/         # Interface utilisateur (à venir)
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

---

## Prérequis

- Docker >= 24.0
- Docker Compose >= 2.0
- Python 3.11+
- Make

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-org/stream2vec.git
cd stream2vec
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 3. Démarrer les services

```bash
make up
```

### 4. Vérifier le démarrage

```bash
make logs
```

### 5. Accéder aux services

| Service | URL |
|---------|-----|
| API Backend | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |
| Kafka UI | http://localhost:8080 |
| Airflow | http://localhost:8088 |
| Qdrant Dashboard | http://localhost:6333/dashboard |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

---

## Roadmap

- [ ] **Phase 1** : Fondations (architecture, configuration, structure) ← *Étape actuelle*
- [ ] **Phase 2** : Backend — Ingestion de documents (upload, MinIO, Kafka)
- [ ] **Phase 3** : Pipeline Spark — Extraction, nettoyage, chunking
- [ ] **Phase 4** : Vectorisation — SentenceTransformers + Qdrant
- [ ] **Phase 5** : API de recherche sémantique
- [ ] **Phase 6** : Intégration LLM (RAG)
- [ ] **Phase 7** : Frontend
- [ ] **Phase 8** : CI/CD + déploiement cloud

---

## Conventions de développement

- **Branches** : `main` (prod), `develop` (intégration), `feature/*`, `fix/*`
- **Commits** : [Conventional Commits](https://www.conventionalcommits.org)
- **Code** : PEP8, type hints, docstrings obligatoires
- **Tests** : Toute fonctionnalité doit être couverte par des tests

---

## Contribution

1. Fork le projet
2. Créer une branche : `git checkout -b feature/ma-feature`
3. Committer : `git commit -m 'feat: ajouter ma feature'`
4. Pusher : `git push origin feature/ma-feature`
5. Ouvrir une Pull Request

---

## Licence

[MIT](LICENSE) — Stream2Vec Team
