# Stream2Vec — Tests

Architecture de tests pour la plateforme Stream2Vec.

## Structure

```
tests/
├── unit/         # Tests unitaires (sans dépendances externes)
├── integration/  # Tests d'intégration (avec DB, Kafka, MinIO)
└── README.md
```

## Tests unitaires (`unit/`)

Tests isolés qui ne nécessitent aucune infrastructure.
Toutes les dépendances externes sont mockées.

```bash
# Via Make
make test-unit

# Directement
docker compose exec backend pytest tests/unit/ -v
```

## Tests d'intégration (`integration/`)

Tests qui interagissent avec les services réels (PostgreSQL, MinIO, Kafka).
Nécessitent que la stack Docker soit démarrée.

```bash
# Via Make
make test-integration

# Directement
docker compose exec backend pytest tests/integration/ -v
```

## Conventions

- Nommage : `test_<module>_<behaviour>.py`
- Un test = une assertion principale
- Utiliser des fixtures pytest pour la configuration commune
- Viser une couverture > 80% sur les modules critiques

## Roadmap

- [ ] Tests unitaires des services (Phase 2)
- [ ] Tests d'intégration de l'API (Phase 2)
- [ ] Tests du pipeline Spark (Phase 3)
- [ ] Tests de bout en bout (Phase 4)
