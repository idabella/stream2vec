# Stream2Vec — API Reference

Base URL: `http://localhost:8000/api/v1`

## Documents

### Upload Document

```http
POST /documents/upload
Content-Type: multipart/form-data

file: <binary>
```

Response `202 Accepted`:
```json
{
  "message": "Document upload accepted — processing queued",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "report.pdf",
  "status": "pending"
}
```

### List Documents

```http
GET /documents/?skip=0&limit=20
```

Response `200 OK`:
```json
{
  "data": [...],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

### Get Document

```http
GET /documents/{document_id}
```

### Delete Document

```http
DELETE /documents/{document_id}
```
Response `204 No Content`

### Get Processing Status

```http
GET /documents/{document_id}/status
```

Response `200 OK`:
```json
{
  "document_id": "...",
  "status": "processing",
  "pipeline_stage": "chunking"
}
```

## Search

### Semantic Search

```http
POST /search/
Content-Type: application/json

{
  "query": "machine learning algorithms",
  "top_k": 5,
  "score_threshold": 0.7
}
```

Response `200 OK`:
```json
{
  "query": "machine learning algorithms",
  "results": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "content": "...",
      "score": 0.92
    }
  ],
  "total": 5
}
```

## Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "Stream2Vec",
  "version": "0.1.0"
}
```
