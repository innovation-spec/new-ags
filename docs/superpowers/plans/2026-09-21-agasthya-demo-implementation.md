# Agasthya Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete local Docker Compose demo of the multi-tenant recommendation, inventory, shared-state, agent, external-data, memory, model-registry, and Streamlit system in the approved spec.

**Architecture:** A FastAPI modular monolith owns authoritative state, PostgreSQL/pgvector is the system of record, Redis provides working memory and Streams, MinIO stores model/artifact blobs, Temporal executes durable workflows, and Streamlit calls FastAPI only. OpenAI is optional at boot and is used only for LLM reasoning/tool selection/explanation; deterministic backend services own inventory, state, ranking, and tenant isolation.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL 16 + pgvector, Redis 7, Temporal Python SDK, MinIO, OpenAI Python SDK, scikit-learn/XGBoost-compatible registry artifacts, Streamlit, pytest, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-09-21-agasthya-demo-design.md`

## Global Constraints

- Local-only demo; Docker Compose is the deployment boundary.
- No Kubernetes/EKS, Kafka/MSK, Terraform/Helm, Prometheus/Grafana/OpenTelemetry, or local LLM.
- LLM integration requires only `OPENAI_API_KEY`; system must boot without it.
- LLMs never directly mutate authoritative business state.
- Every tenant-owned read/write is tenant-scoped.
- Inventory mutations are transactional and idempotent.
- Shared-state mutations are versioned and auditable.
- Redis Streams is the only event backbone in V1.
- MinIO is the local S3-compatible artifact/model store.
- Streamlit never accesses infrastructure directly; it uses FastAPI.

## Review Focus

1. Missing/invalid tenant IDs must never leak another tenant's records; API tests pin this behavior.
2. Replayed idempotency keys must return the original reservation rather than reserve twice; inventory tests pin this behavior.
3. Concurrent state patches against stale versions must be recorded and merged/rejected deterministically without lost updates; state tests pin this behavior.
4. OpenAI-unavailable/no-key mode must still boot and preserve all non-LLM demos; health/agent tests pin this behavior.
5. External-provider malformed/timeout/429 responses must terminate after bounded retries and fall back with provenance; external-data tests pin this behavior.

---

### Task 1: Project foundation, configuration, health API, and Compose topology

**Files:**
- Create: `backend/pyproject.toml`, `backend/Dockerfile`, `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/api/health.py`, `backend/tests/test_health.py`
- Create: `ui/pyproject.toml`, `ui/Dockerfile`, `ui/app.py`
- Create: `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`

**Interfaces:**
- Produces `Settings` from `app.core.config`, `create_app() -> FastAPI`, and `GET /health` returning service + OpenAI-enabled state.
- Produces Compose service names `postgres`, `redis`, `minio`, `temporal`, `api`, `worker`, `streamlit` consumed by later tasks.

- [ ] Write `backend/tests/test_health.py` asserting `/health` returns 200 and `openai_enabled=false` when the key is absent.
- [ ] Run the test and verify failure because the application does not exist.
- [ ] Implement settings, FastAPI app, health router, Python dependency manifests, Dockerfiles, Compose topology, env sample, README skeleton.
- [ ] Run the focused test and then the backend test suite.
- [ ] Commit `feat: bootstrap local demo platform`.

### Task 2: Database models, migrations, tenancy, catalog, and seeded demo data

**Files:**
- Create: `backend/app/db/base.py`, `backend/app/db/session.py`, `backend/app/models/*.py`, `backend/app/schemas/tenant.py`, `backend/app/schemas/catalog.py`
- Create: `backend/app/services/tenancy/service.py`, `backend/app/services/catalog/service.py`, `backend/app/api/tenants.py`, `backend/app/api/catalog.py`
- Create: `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/0001_initial.py`
- Create: `scripts/seed_demo.py`, `backend/tests/test_tenant_isolation.py`

**Interfaces:**
- Produces SQLAlchemy models for all spec-required tables and `TenantService`, `CatalogService` methods that require explicit `tenant_id`.
- Produces deterministic seeding invoked by `python /scripts/seed_demo.py`.

- [ ] Write tenant isolation/API tests showing Tenant A cannot retrieve Tenant B products.
- [ ] Verify tests fail before repositories/routes exist.
- [ ] Implement model set, migration, tenant/catalog services and routes, seed script with two tenants and deterministic products/customers/events.
- [ ] Run focused tests then full backend suite.
- [ ] Commit `feat: add multi-tenant domain and seed data`.

### Task 3: Transactional inventory and idempotent reservations

**Files:**
- Create: `backend/app/schemas/inventory.py`, `backend/app/services/inventory/service.py`, `backend/app/api/inventory.py`
- Create: `backend/tests/test_inventory.py`, `tests/concurrency/test_inventory_race.py`

**Interfaces:**
- Produces `InventoryService.get_stock(tenant_id, sku_id)` and `reserve(tenant_id, sku_id, quantity, idempotency_key)`.
- Emits typed inventory events through the event publisher introduced in Task 4; until then the service owns a no-op event hook.

- [ ] Write tests for available calculation, insufficient stock, tenant isolation, and idempotency replay.
- [ ] Verify RED.
- [ ] Implement row-locked transactional reservation and ledger append.
- [ ] Add a 100-attempt race test expecting exactly seeded-stock successes and no negative inventory.
- [ ] Run focused and full suites.
- [ ] Commit `feat: add transactional inventory reservations`.

### Task 4: Redis Streams event envelope and shared-state coordinator

**Files:**
- Create: `backend/app/core/redis.py`, `backend/app/schemas/events.py`, `backend/app/services/events/publisher.py`
- Create: `backend/app/schemas/state.py`, `backend/app/services/state/merge.py`, `backend/app/services/state/service.py`, `backend/app/api/state.py`
- Create: `backend/tests/test_state_merge.py`, `tests/concurrency/test_state_conflicts.py`

**Interfaces:**
- Produces `EventPublisher.publish(stream, envelope)` and `StateService.get_state(...)`, `submit_patch(...)`.
- State patches accept `operation_id`, `base_version`, `agent_id`, `patch`, `merge_policy` and return resulting version/status.

- [ ] Write merge-policy tests (append, additive counter, weighted interest, internal authority) and stale-version tests.
- [ ] Verify RED.
- [ ] Implement Redis publisher with graceful no-Redis test mode, state snapshot/event persistence, deterministic field-level merges, idempotent operation IDs.
- [ ] Add concurrency test for 100 stale-base operations and assert internally consistent version/event counts.
- [ ] Run suites.
- [ ] Commit `feat: add versioned shared state and events`.

### Task 5: Recommendation engine and pgvector-ready semantic scoring

**Files:**
- Create: `backend/app/schemas/recommendation.py`, `backend/app/services/recommendation/features.py`, `candidate.py`, `ranking.py`, `service.py`, `backend/app/api/recommendations.py`
- Create: `backend/tests/test_recommendation.py`

**Interfaces:**
- Produces `RecommendationService.generate(tenant_id, customer_id, limit=10)` with persisted items and inventory-aware output.
- Baseline scorer supports category affinity, brand affinity, behavior, popularity, price, semantic score, inventory.

- [ ] Write tests proving unavailable SKUs are excluded, cross-tenant products never appear, and scores are deterministic.
- [ ] Verify RED.
- [ ] Implement candidate generation, features, weighted scorer, persistence, API routes.
- [ ] Run tests.
- [ ] Commit `feat: add inventory-aware recommendation engine`.

### Task 6: MinIO model registry and artifact activation

**Files:**
- Create: `backend/app/core/minio.py`, `backend/app/services/model_registry/service.py`, `backend/app/api/models.py`, `scripts/create_minio_buckets.py`, `scripts/train_ranker.py`
- Create: `backend/tests/test_model_registry.py`

**Interfaces:**
- Produces `ModelRegistry.register`, `activate`, `get_active`, and artifact put/get methods.
- Exactly one active version per model name is enforced transactionally.

- [ ] Write tests for registration, activation exclusivity, and missing artifact behavior with an in-memory/fake object-store adapter.
- [ ] Verify RED.
- [ ] Implement MinIO adapter, registry metadata, bucket initializer, deterministic baseline model artifact script.
- [ ] Run tests.
- [ ] Commit `feat: add MinIO-backed model registry`.

### Task 7: External providers, retry/backoff/fallback, and credibility resolver

**Files:**
- Create: `backend/app/services/external_data/providers.py`, `retry.py`, `credibility.py`, `service.py`, `backend/app/api/demo.py`
- Create: `backend/tests/test_external_data.py`

**Interfaces:**
- Produces `ExternalDataService.resolve(query, scenario)` returning accepted value plus complete provenance/attempt history.
- Produces deterministic `CredibilityResolver.resolve(candidates, internal_value=None)`.

- [ ] Write tests for timeout retry, 429 retry, malformed payload fallback, conflicting source selection, and internal-authority precedence.
- [ ] Verify RED.
- [ ] Implement deterministic mock providers, bounded exponential backoff with injectable sleep/jitter, fallback, persistence/provenance, credibility resolver.
- [ ] Run tests.
- [ ] Commit `feat: add resilient external-data resolution`.

### Task 8: Working/persistent/semantic memory and pruning/archive

**Files:**
- Create: `backend/app/services/memory/service.py`, `backend/app/api/memory.py`
- Create: `backend/tests/test_memory.py`

**Interfaces:**
- Produces `MemoryService.save`, `list`, `prune_expired`, `archive_state_events` with tenant scoping.
- Redis working memory uses TTL; PostgreSQL persists structured memory; archive adapter writes JSON to MinIO.

- [ ] Write tests for tenant isolation, expiration pruning, non-expiring persistent memory, and archive manifest generation.
- [ ] Verify RED.
- [ ] Implement service and routes with infrastructure adapters.
- [ ] Run tests.
- [ ] Commit `feat: add tiered memory and pruning`.

### Task 9: OpenAI tool layer and logical agents

**Files:**
- Create: `backend/app/llm/client.py`, `tools.py`, `schemas.py`, `backend/app/agents/service.py`, `backend/app/api/agents.py`
- Create: `backend/tests/test_agents.py`

**Interfaces:**
- Produces `LLMClient.chat(...)` that is disabled cleanly without a key, plus strict tool registry for approved backend tools only.
- Produces `AgentService.chat(tenant_id, customer_id, message)` and persists run/events.

- [ ] Write tests proving no-key mode returns an explicit disabled response, tool registry has only approved tools, fabricated SKU output cannot bypass backend recommendation/inventory results.
- [ ] Verify RED.
- [ ] Implement OpenAI Responses API adapter, tool schemas/dispatch, logical Supervisor/Recommendation/Inventory/Research roles, run/event persistence.
- [ ] Run tests.
- [ ] Commit `feat: add OpenAI tool-driven agent layer`.

### Task 10: Temporal workflows and worker

**Files:**
- Create: `backend/app/workflows/recommendation.py`, `research.py`, `agent.py`, `backend/app/workers/main.py`
- Create: `backend/tests/test_workflows.py`

**Interfaces:**
- Produces Temporal workflow classes and activities wrapping existing deterministic services.
- API can fall back to in-process service execution if Temporal is unavailable in unit-test mode; Compose uses Temporal.

- [ ] Write workflow tests using Temporal test environment or activity-unit boundaries for retry/fallback ordering.
- [ ] Verify RED.
- [ ] Implement workflows, activities, worker startup, Compose wiring.
- [ ] Run tests.
- [ ] Commit `feat: add durable Temporal workflows`.

### Task 11: Demo scenarios and stats API

**Files:**
- Modify: `backend/app/api/demo.py`
- Create: `backend/app/services/demo/service.py`, `tests/demo_scenarios/test_demo_api.py`

**Interfaces:**
- Produces endpoints `/demo/inventory-race`, `/demo/state-conflict`, `/demo/external-failure`, `/demo/recommendation`, `/demo/memory-prune`, `/demo/stats`.

- [ ] Write API tests for each scenario with compact test parameters and deterministic result payloads.
- [ ] Verify RED.
- [ ] Implement scenario orchestrator using real service code, not duplicate demo-only algorithms.
- [ ] Run tests.
- [ ] Commit `feat: add executable demo scenarios`.

### Task 12: Streamlit control console

**Files:**
- Create: `ui/api/client.py`, `ui/components/cards.py`, `ui/pages/1_AI_Assistant.py`, `2_Recommendation_Explorer.py`, `3_Agent_Runs.py`, `4_Demo_Control.py`
- Modify: `ui/app.py`

**Interfaces:**
- UI consumes only FastAPI HTTP endpoints via `ApiClient`.
- No direct PostgreSQL/Redis/MinIO/Temporal imports are permitted in UI package.

- [ ] Write lightweight client tests proving tenant headers/IDs are forwarded and API errors render safely.
- [ ] Verify RED.
- [ ] Implement Streamlit pages for assistant, recommendations, agent runs, and all demo controls.
- [ ] Run UI tests.
- [ ] Commit `feat: add Streamlit demo console`.

### Task 13: End-to-end bootstrapping, smoke tests, documentation, and verification

**Files:**
- Modify: `docker-compose.yml`, `README.md`, `.env.example`
- Create: `scripts/wait_for_services.py`, `tests/integration/test_smoke.py`

**Interfaces:**
- Produces one-command `docker compose up --build` stack and documented seed/demo commands.

- [ ] Write smoke test expectations for health, tenants, seeded recommendation, demo scenario endpoints.
- [ ] Verify RED against incomplete bootstrap.
- [ ] Add migration/seed/bucket startup commands and healthchecks; finish README with exact local commands and OpenAI-key instructions.
- [ ] Run full Python tests, compile checks, Compose config validation, build stack, migrations, seed, smoke requests, and concurrency demos.
- [ ] Commit `chore: finish local demo bootstrap and docs`.

### Task 14: PPO shadow source-selection experiment

**Files:**
- Create: `backend/app/experiments/source_selection_ppo.py`
- Create: `backend/tests/test_ppo_shadow.py`
- Modify: `backend/app/api/demo.py`
- Modify: `ui/pages/4_Demo_Control.py`

**Interfaces:**
- Produces a non-authoritative PPO source-selection experiment exposed at `POST /demo/ppo-shadow`.
- Deterministic credibility/source rules remain the authoritative action regardless of PPO output.

- [x] Write RED tests proving PPO training improves reward/accuracy and cannot replace the deterministic authoritative action.
- [x] Implement a lightweight NumPy clipped-PPO actor/critic over six source-selection actions and six reproducible scenarios.
- [x] Add the `/demo/ppo-shadow` endpoint and Streamlit control.
- [x] Run focused PPO tests and the backend suite.
