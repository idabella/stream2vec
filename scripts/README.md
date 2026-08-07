# Stream2Vec — Scripts

Scripts utilitaires pour le développement et la gestion de la stack.

## Scripts disponibles

| Script | Description |
|--------|-------------|
| `start.sh` | Démarre toute la stack Docker Compose |
| `stop.sh` | Arrête tous les services |
| `reset.sh` | Reset complet (⚠️ supprime les volumes) |

## Utilisation

```bash
# Démarrer
bash scripts/start.sh

# Arrêter
bash scripts/stop.sh

# Reset complet
bash scripts/reset.sh
```

Sur Linux/macOS, vous pouvez rendre les scripts exécutables :

```bash
chmod +x scripts/*.sh
```

## Note

Ces scripts sont des wrappers autour de `docker compose`.
Préférez `make` pour les commandes de développement quotidiennes (voir `Makefile`).
