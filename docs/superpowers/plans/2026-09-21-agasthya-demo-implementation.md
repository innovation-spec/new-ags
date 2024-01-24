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
