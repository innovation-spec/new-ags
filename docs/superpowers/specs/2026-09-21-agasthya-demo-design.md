# Agasthya Multi-tenant Recommendation Engine + Inventory Demo — Design

Date: 2026-09-21
Status: Design approved in chat; written-spec review pending

## 1. Goal

Build a local-first demonstration of the Agasthya Technologies multi-tenant recommendation and inventory platform described in the SR&ED project narrative. The demo must prove the core technical concepts without production infrastructure overhead.

The system must demonstrate:

- Multi-tenant catalog, customer, inventory, recommendation, and agent-state isolation.
- Inventory updates and reservations that prevent overselling under concurrency.
- Recommendation generation using customer behavior, product similarity, and live inventory.
- Multiple autonomous agents that coordinate through deterministic backend tools.
- Concurrent shared-state updates with versioning, conflict detection, and merge rules.
- External-source retries, backoff, fallback, provenance, and credibility resolution.
- Working memory, persistent memory, semantic memory, pruning, and archival.
- Model artifact/version storage in local S3-compatible storage.
- LLM integration through the OpenAI API only.
- A simple Streamlit UI that makes the above behavior visible during a demo.

## 2. Explicit Non-goals

The following are intentionally deferred:

- Kubernetes, EKS, Helm, Terraform, Argo CD, or cloud deployment.
- Kafka, MSK, or other heavy event-streaming infrastructure.
- Prometheus, Grafana, OpenTelemetry, Jaeger, CloudWatch, or dedicated observability stack.
- Multi-region, autoscaling, production IAM, production secrets management, or HA design.
- Local LLM hosting, Ollama, vLLM, or multi-provider LLM abstraction.
- Full consumer-grade frontend design.
- Production-grade RL/PPO control of authoritative state.

The demo must run locally with Docker Compose.

## 3. Locked Technology Stack

### Application
- Python 3.12
- FastAPI backend
- Streamlit UI
- Pydantic schemas
- SQLAlchemy 2.x
- Alembic migrations

### Data
- PostgreSQL 16
- pgvector extension
- Redis 7
- Redis Streams
- MinIO for S3-compatible object storage

### Orchestration
- Temporal server + Temporal Python SDK
- Separate Temporal worker container

### ML / Recommendation
- Python
- scikit-learn utilities
- LightGBM or XGBoost for the first trainable ranker
- pgvector for content/semantic similarity

### LLM
- OpenAI API key via environment variable
- Official OpenAI Python SDK
- Responses API with tool/function calling
- No local model and no provider abstraction in V1

### Runtime
- Docker
- Docker Compose

## 4. Runtime Topology

The Docker Compose environment contains:

1. `postgres`
2. `redis`
3. `minio`
4. `minio-init`
5. `temporal`
6. `temporal-ui`
7. `api`
8. `worker`
9. `streamlit`

Expected local endpoints:

- Streamlit: `http://localhost:8501`
- FastAPI: `http://localhost:8000`
- FastAPI docs: `http://localhost:8000/docs`
- Temporal UI: `http://localhost:8080`
- MinIO console: `http://localhost:9001`

## 5. Architectural Shape

Use a modular monolith for business functionality plus a separate workflow worker.

```text
Streamlit UI
    |
    v
FastAPI
    |
    +-- Tenant module
    +-- Catalog module
    +-- Inventory module
    +-- Recommendation module
    +-- State coordinator
    +-- Memory module
    +-- Agent module
    +-- External-data module
    +-- Model registry module
    |
    +--> PostgreSQL + pgvector
    +--> Redis + Redis Streams
    +--> MinIO
    +--> Temporal
    +--> OpenAI API
```

Business modules remain separated by service interfaces even though they run inside one FastAPI deployment. This keeps the demo small while preserving future service-extraction boundaries.

## 6. Repository Structure

```text
agasthya-demo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── tenancy/
│   │   │   ├── catalog/
│   │   │   ├── inventory/
│   │   │   ├── recommendation/
│   │   │   ├── state/
│   │   │   ├── memory/
│   │   │   ├── external_data/
│   │   │   └── model_registry/
│   │   ├── agents/
│   │   ├── llm/
│   │   ├── workflows/
│   │   └── workers/
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
├── ui/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   ├── api/
│   ├── pyproject.toml
│   └── Dockerfile
├── ml/
│   ├── recommendation/
│   └── ppo/
├── scripts/
│   ├── seed_demo.py
│   ├── train_ranker.py
│   └── create_minio_buckets.py
├── tests/
│   ├── concurrency/
│   ├── integration/
│   └── demo_scenarios/
├── docs/
│   └── superpowers/
│       └── specs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 7. Multi-tenancy

Every tenant-owned business record must include `tenant_id`.

V1 demo includes at least two seeded tenants, `tenant-a` and `tenant-b`, with separate products, customers, inventory, recommendations, memories, and agent runs.

Application service methods require explicit tenant context. Cache keys and Redis stream metadata also include `tenant_id`.

The demo must include an automated isolation test proving Tenant A cannot retrieve Tenant B data through supported APIs.

## 8. Core Data Model

Required tables:

- tenants
- users
