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

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6
```

The API key is injected into the backend container through `.env` and must never be committed.

OpenAI responsibilities:

- classify user intent
- select approved tools
- coordinate high-level agent tasks
- explain recommendation results
- summarize structured external-data findings

OpenAI must not directly own:

- inventory truth
- tenant isolation
- database transactions
- state versions
- deterministic merge rules
- recommendation scores
- source authority

Required OpenAI tools exposed by the backend:

- get_customer_profile
- get_customer_history
- search_products
- get_recommendations
- check_inventory
- get_shared_state
- submit_state_patch
- search_external_data
- save_memory

Tool inputs and outputs use strict Pydantic/JSON schemas. Tool outputs are revalidated before they are returned to the model.

No raw SQL or unrestricted HTTP tool is exposed to the model.

## 15. Agent System

V1 contains four logical agents:

- Supervisor Agent
- Recommendation Agent
- Inventory Agent
- Research Agent

An optional reporting summary can be added later without changing the core architecture.

Agents are logical roles, not separate containers.

Agent lifecycle:

- CREATED
- PLANNING
- RUNNING
- WAITING_TOOL
- VALIDATING
- COMPLETED
- FAILED
- CANCELLED
- TIMED_OUT

Every transition is persisted in `agent_events`.

## 16. Temporal Workflows

Temporal handles durable workflow execution and retries.

Initial workflows:

### RecommendationWorkflow
1. Load customer.
2. Load shared state.
3. Generate candidates.
4. Check inventory.
5. Rank candidates.
6. Persist recommendation.
7. Optionally call OpenAI for explanation.

### ResearchWorkflow
1. Query preferred source.
2. On retryable failure, apply exponential backoff.
3. Fall back to secondary source.
4. Normalize results.
5. Apply credibility resolver.
6. Persist provenance.

### AgentWorkflow
Coordinates agent task creation, tool execution, state patches, and final response composition.

## 17. External Data / Failure Simulation

V1 uses two mock external providers and optionally one real public provider later.

Mock providers intentionally simulate:

- timeouts
- 429 responses
- malformed payloads
- conflicting values
- stale values

Retry behavior:

- finite retry count
- exponential backoff
- jitter
- fallback provider
- provenance recorded for every accepted value

This is a first-class demo capability, not test-only behavior.

## 18. Credibility Resolver

Source arbitration is deterministic in V1.

Initial authority order:

1. verified internal transactional data
2. tenant-managed verified data
3. trusted partner/mock provider A
4. external provider B
5. LLM-inferred value

Credibility inputs may include:

- authority level
- source reliability
- freshness
- corroboration
- historical quality

Internal authoritative values cannot be overwritten solely because an external source has a higher numeric confidence score.

## 19. Memory

Memory tiers:

### Working memory
Redis with TTL.

### Persistent structured memory
PostgreSQL `memory_entries`.

### Semantic memory
pgvector embeddings for products and selected memory entries.

### Large/archive artifacts
MinIO.

Each memory entry includes:

- tenant_id
- owner/entity
- memory type
- importance
- source
- created_at
- last_accessed_at
- expires_at
- reconstructible flag

A scheduled worker deletes expired temporary memories and can compact old state events into snapshots archived to MinIO.

## 20. PPO Scope

PPO is an experimental, late-stage demo track only.

It may learn source-selection actions such as:

- use internal only
- query provider A
- query provider B
- query both
- fallback
- abstain

It may not update authoritative inventory, tenant permissions, or state merge rules.

The deterministic policy remains production/demo truth; PPO operates in shadow/evaluation mode unless explicitly promoted for a controlled demo.

## 21. Streamlit UI

The UI is a demo/control console, not a production retail frontend.

Required pages:

### AI Assistant
- select tenant
- select customer
- chat input
- streamed response/status
- recommended products
- inventory availability
- brief explanation

### Recommendation Explorer
- customer features
- segment
- candidate scores
- ranked results
- inventory state
- active model version

### Agent Runs
- run list
- agent/task statuses
- tool calls
- state version timeline
- conflicts and resolutions
- retry/fallback events

### Demo Control
Buttons/scenarios for:

- concurrent state conflict
- inventory oversell prevention
- external timeout/retry
- external 429/fallback
- conflicting external data
- recommendation generation
- memory pruning
- agent retry

Streamlit talks to FastAPI only; it never accesses PostgreSQL, Redis, Temporal, or MinIO directly.

## 22. Seed Data

The demo seeder creates at minimum:

- 2 tenants
- 1,000 customers per tenant
- 1,000 products total or per tenant depending on resource cost
- multiple categories and brands
- warehouse inventory
- at least 20,000 synthetic customer interaction events
- synthetic purchase history
- product embeddings

Seed generation must be deterministic with a configurable random seed.

## 23. API Surface

Initial route groups:

- `/health`
- `/tenants`
- `/catalog`
- `/inventory`
- `/customers`
- `/recommendations`
- `/agents`
- `/state`
- `/models`
- `/demo`

Representative endpoints:

- `POST /inventory/reserve`
- `GET /inventory/{sku_id}`
- `POST /recommendations/{customer_id}`
- `GET /recommendations/{customer_id}/latest`
- `POST /agents/chat`
- `GET /agents/runs/{run_id}`
- `GET /state/{entity_type}/{entity_id}`
- `POST /state/{entity_type}/{entity_id}/patch`
- `GET /models`
- `POST /models/{model_name}/{version}/activate`
- `POST /demo/inventory-race`
- `POST /demo/state-conflict`
- `POST /demo/external-failure`

## 24. Testing Strategy

### Unit tests
- ranking feature calculations
- merge policies
- credibility scoring
- inventory calculations
- schema validation

### Integration tests
- PostgreSQL repositories
- Redis Streams consumers
- MinIO upload/download
- Temporal workflow execution
- OpenAI integration mocked by default

### Concurrency tests
- inventory oversell test
- shared-state version conflict test
- idempotency replay test

### Tenant isolation tests
- cross-tenant catalog access denied/not found
- cross-tenant inventory access denied/not found
- cross-tenant memory unavailable
- cross-tenant recommendation leakage impossible

### Demo scenario tests
Each Streamlit demo control maps to an API scenario with an automated backend test.

## 25. Logging

No observability stack in V1.

Use structured application logs with fields such as:

- timestamp
- level
- tenant_id
- request_id
- agent_id
- run_id
- action
- duration_ms

Logs go to stdout so they are visible through Docker Compose.

## 26. Configuration

`.env.example` includes only non-secret placeholders and local configuration.

Required values include:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `DATABASE_URL`
- `REDIS_URL`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `TEMPORAL_ADDRESS`

Local defaults are provided for everything except `OPENAI_API_KEY`.

The demo must still boot without a key; LLM-dependent endpoints/pages report that OpenAI integration is disabled until a key is supplied. Non-LLM demos must continue to work.

## 27. Definition of Done

The build is considered complete when all of the following are true:

1. `docker compose up --build` starts the full local stack.
2. Database migrations complete successfully.
3. MinIO buckets are created automatically.
4. Seed data can be loaded with one command.
5. Streamlit opens and can select two different tenants.
6. Recommendation generation returns inventory-aware ranked products.
7. OpenAI chat can call approved backend tools when an API key is configured.
8. Inventory concurrency demo proves no overselling.
9. Shared-state demo proves versioned conflict handling without lost updates.
10. External-provider demo shows retry, fallback, provenance, and credibility selection.
11. Agent-run UI shows tool execution and state transitions.
12. Model artifact is loadable from MinIO and registry activation is reflected by the recommendation service.
13. Memory pruning can be triggered and verified.
14. Cross-tenant isolation tests pass.
15. Core unit/integration/concurrency tests pass.

## 28. Future Extension Points

The design deliberately leaves clean seams for later replacement:

- Redis Streams -> Kafka/MSK
- MinIO -> AWS S3
- Docker Compose -> Kubernetes/EKS
- local Postgres -> managed PostgreSQL
- Streamlit -> production web application
- modular monolith modules -> independent services
- simple ranker -> larger retrieval/ranking models
- deterministic source policy -> evaluated RL policy

None of these extensions are required for the demo.

## 29. Key Design Invariants

These are non-negotiable during implementation:

1. LLMs never directly mutate authoritative business state.
2. Every tenant-owned access is tenant-scoped.
3. Inventory changes are transactional and idempotent.
4. Shared-state mutations are versioned and auditable.
5. Recommendation selection is backend/ML-controlled; the LLM may explain but does not fabricate catalog items.
6. External values retain provenance.
7. OpenAI integration is optional at boot and requires only an API key when enabled.
8. The entire demo runs with Docker Compose and no cloud infrastructure.
