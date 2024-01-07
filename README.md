# Agasthya Multi-tenant Recommendation + Inventory Demo

A local-first implementation of the Agasthya 2024 retail R&D platform with a React + shadcn/ui systems console: multi-tenant catalog/customer isolation, transactional inventory, inventory-aware recommendations, deterministic shared-state coordination, Redis Streams event envelopes, MinIO model/artifact storage, Temporal workflows, resilient external providers, tiered memory, PPO shadow evaluation, application-level anomaly reporting, and optional OpenAI tool-driven explanations.

## Local architecture

```text
React + shadcn/ui + Nginx -> FastAPI modular monolith
                    |-> PostgreSQL 16 + pgvector
                    |-> Redis 7 + Redis Streams
                    |-> MinIO (local S3-compatible artifacts/models)
                    |-> Temporal worker
                    `-> OpenAI API (optional; API key only)
```

The React browser app never connects directly to PostgreSQL. It calls FastAPI through Nginx's `/api` reverse proxy; PostgreSQL remains the local source of truth.

No Kubernetes, Kafka, cloud deployment, local LLM, Prometheus, Grafana or OpenTelemetry stack is required.

## Requirements

- Docker + Docker Compose
- An OpenAI API key only if you want the AI Assistant to use the LLM. All deterministic demos work without it.

## Start everything

```bash
cp .env.example .env
# Optional: set OPENAI_API_KEY in .env
docker compose up --build
```

The `bootstrap` container automatically:

1. runs Alembic migrations,
2. enables pgvector through the initial migration,
3. seeds two tenants, 2,000 customers, 1,000 products, inventory and 20,000 interaction events,
4. trains/registers an initial recommendation-ranker artifact in MinIO.
