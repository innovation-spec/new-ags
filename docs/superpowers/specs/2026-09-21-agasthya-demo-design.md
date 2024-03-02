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
- customers
- products
- product_variants
- skus
- warehouses
- inventory
- inventory_ledger
- inventory_reservations
- customer_events
- customer_features
- customer_segments
- recommendations
- recommendation_items
- recommendation_feedback
- agent_runs
- agent_tasks
- agent_events
- shared_states
- state_events
- memory_entries
- external_sources
- external_results
- credibility_scores
- models
- model_versions

A compact schema is preferred; tables should only contain fields required by the demo and its tests.

## 9. Inventory Design

Inventory is authoritative backend state. LLMs and agents never update inventory directly.

Each SKU/location keeps:

- on_hand
- reserved
- available
- version

`available = on_hand - reserved`.

All stock-changing operations append an `inventory_ledger` record.

Reservation requirements:

- Transactional update.
- Idempotency key.
- Cannot reserve more than available stock.
- Safe under concurrent requests.
- Repeated identical idempotent request returns the original reservation.

Mandatory concurrency demonstration:

- Seed inventory = 5.
- Send 100 simultaneous reservation attempts for quantity 1.
- Exactly 5 succeed.
- 95 fail cleanly.
- Inventory never becomes negative.

## 10. Shared State Coordinator

Agents do not directly mutate shared JSON state.

`shared_states` contains the latest snapshot and a monotonically increasing version.

`state_events` records every proposed and applied mutation with:

- state_id
- tenant_id
- agent_id
- operation_id
- base_version
- resulting_version
- patch
- merge_policy
- status
- created_at

Mutation flow:

1. Agent reads state version N.
2. Agent submits a typed patch referencing base version N.
3. State coordinator validates tenant, schema, operation id, and base version.
4. If no conflict exists, patch is applied transactionally.
5. If a conflict exists, field-level deterministic merge rules are used.
6. State version increments.
7. State event is recorded.
8. State update event is emitted to Redis Streams.

Initial merge policies:

- inventory: transactional / never merged through LLM state
- append-only events: append
- counters: additive
- customer interests: weighted union
- verified internal fields: internal-authority wins
- external values: credibility resolver
- task lifecycle: state-machine transition validation

Mandatory shared-state demonstration:

- 100 concurrent workers submit changes against the same shared state.
- No lost updates.
- All accepted/rejected/conflicted operations are recorded.
- Final version number is internally consistent.

## 11. Eventing

Redis Streams is the only event backbone in V1.

Initial streams:

- `stream:customer-events`
- `stream:inventory-events`
- `stream:agent-events`
- `stream:state-events`
- `stream:recommendation-events`

Events are typed and validated with Pydantic schemas.

Kafka compatibility is deferred; event envelopes should still contain stable identifiers so a future transport migration is straightforward.

## 12. Recommendation Engine

The recommendation pipeline is deterministic/ML-first, not LLM-first.

Pipeline:

1. Load tenant + customer context.
2. Generate candidates from multiple sources.
3. Remove unavailable inventory.
4. Build ranking features.
5. Score candidates.
6. Apply simple business constraints.
7. Persist recommendation result.
8. Let the LLM explain the already-selected result when needed.

V1 candidate generators:

- tenant popularity
- category affinity
- recent customer interactions
- product embedding similarity
- simple similar-user/category signals

Initial features:

- category affinity
- brand affinity
- semantic similarity
- recent views
- recent purchases
- popularity
- price
- available inventory

Ranking modes:

- Baseline weighted scorer must always work.
- Optional LightGBM/XGBoost ranker is trained from synthetic data.
- Model selection is controlled by registry metadata.

## 13. Model Registry and MinIO

MinIO is local S3-compatible storage.

Required buckets:

- `agasthya-models`
- `agasthya-datasets`
- `agasthya-artifacts`
- `agasthya-reports`
- `agasthya-state-archives`

PostgreSQL stores model metadata; MinIO stores model binaries and artifacts.

Example object layout:

```text
agasthya-models/
└── recommendation/
    └── v1/
        ├── model.bin
        ├── metrics.json
        ├── features.json
        └── training_config.json
```

Only one model version per model name may be marked ACTIVE in the demo registry.

## 14. OpenAI Integration

The LLM integration is deliberately minimal.

Environment:
