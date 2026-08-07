# Pipeline de traitement — Stream2Vec

## Vue d'ensemble

Le pipeline de traitement est le cœur de Stream2Vec.
Il transforme un document brut en vecteurs indexés dans Qdrant.

## Étapes du pipeline

### 1. Ingestion

**Entrée** : Fichier document (PDF, DOCX, TXT, ...)
**Action** :
  - Validation du format
  - Stockage dans MinIO
  - Persistance des métadonnées dans PostgreSQL
  - Publication d'un événement dans Kafka

**Statut** : À implémenter (Phase 2)

---

### 2. Extraction

**Entrée** : Événement Kafka contenant l'ID et le chemin du document
**Action** :
  - Récupération du fichier depuis MinIO
  - Extraction du texte brut selon le format (PDF → PyMuPDF, DOCX → python-docx)

**Statut** : À implémenter (Phase 3)

---

### 3. Nettoyage

**Entrée** : Texte brut extrait
**Action** :
  - Suppression des caractères spéciaux et whitespace excessif
  - Normalisation Unicode
  - Suppression des doublons

**Statut** : À implémenter (Phase 3)

---

### 4. Chunking

**Entrée** : Texte nettoyé
**Action** :
  - Découpage en segments de taille configurable
  - Overlap configurable entre les segments
  - Attribution d'un identifiant unique par chunk

**Paramètres** : `chunk_size` (défaut: 512 tokens), `overlap` (défaut: 50 tokens)

**Statut** : À implémenter (Phase 3)

---

### 5. Vectorisation (Embeddings)

**Entrée** : Liste de chunks texte
**Action** :
  - Génération des vecteurs via SentenceTransformers
  - Modèle par défaut : `all-MiniLM-L6-v2` (384 dimensions)

**Statut** : À implémenter (Phase 4)

---

### 6. Indexation

**Entrée** : Paires (chunk, vecteur)
**Action** :
  - Upload dans Qdrant avec métadonnées
  - Mise à jour du statut dans PostgreSQL

**Statut** : À implémenter (Phase 4)

---

## Formats supportés

| Format | Extracteur | Statut |
|--------|-----------|--------|
| TXT | Natif Python | À implémenter |
| PDF | PyMuPDF | À implémenter |
| DOCX | python-docx | À implémenter |
| HTML | BeautifulSoup | À implémenter |
| Markdown | Natif Python | À implémenter |

## TODO

- [ ] Définir le schéma Kafka des événements
- [ ] Définir le schéma Qdrant (collection, distance, dimensions)
- [ ] Documenter la stratégie de chunking
- [ ] Définir la stratégie de gestion des erreurs
