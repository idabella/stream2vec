# Roadmap — Stream2Vec

## Phases de développement

### Phase 1 — Fondations ✅ *[Actuelle]*

> Architecture, configuration, structure du projet

- [x] Structure du projet
- [x] Docker Compose (stack complète)
- [x] Backend FastAPI (architecture, configuration)
- [x] Pipeline Spark (squelette)
- [x] Monitoring (Prometheus + Grafana)
- [x] Documentation initiale

---

### Phase 2 — Ingestion de documents

> Endpoint d'upload, stockage MinIO, événement Kafka

- [ ] Endpoint `POST /api/v1/documents/upload`
- [ ] Modèle `Document` (PostgreSQL)
- [ ] Migration Alembic initiale
- [ ] Upload vers MinIO
- [ ] Publication événement Kafka
- [ ] Endpoint `GET /api/v1/documents/{id}` (statut)
- [ ] Tests unitaires et d'intégration

---

### Phase 3 — Pipeline de traitement

> Spark Structured Streaming : extraction, nettoyage, chunking

- [ ] Job Spark consommant Kafka
- [ ] Extracteur de texte (PDF, DOCX, TXT)
- [ ] Module de nettoyage du texte
- [ ] Module de chunking avec overlap
- [ ] Mise à jour statut PostgreSQL
- [ ] Tests des transformations Spark

---

### Phase 4 — Vectorisation

> Embeddings SentenceTransformers + indexation Qdrant

- [ ] Intégration SentenceTransformers dans Spark
- [ ] Création collection Qdrant
- [ ] Indexation des chunks avec métadonnées
- [ ] Endpoint de recherche sémantique
- [ ] Tests de recherche

---

### Phase 5 — RAG et intégration LLM

> Recherche sémantique + génération de réponses

- [ ] API de recherche sémantique
- [ ] Intégration LLM (OpenAI / Ollama)
- [ ] Pipeline RAG complet
- [ ] Gestion du contexte et des sources

---

### Phase 6 — Frontend

> Interface utilisateur

- [ ] Choix du framework frontend
- [ ] Interface d'upload de documents
- [ ] Interface de recherche
- [ ] Tableau de bord de suivi

---

### Phase 7 — Production

> CI/CD, déploiement cloud, monitoring avancé

- [ ] Pipeline CI/CD (GitHub Actions)
- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] Alertes Prometheus
- [ ] SLOs et SLAs
