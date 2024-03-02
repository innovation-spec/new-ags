# Agasthya React Demo Console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a tested React/TypeScript web console that exercises the local Agasthya FastAPI/PostgreSQL demo and visibly covers the nine workbook engineering phases.

**Architecture:** Add a Vite SPA served by Nginx with `/api` reverse proxy to the existing FastAPI modular monolith. Extend FastAPI only where the existing Streamlit UI lacks browse/operations/schema/status APIs; keep PostgreSQL as the source of truth and reuse all existing deterministic services.

**Tech Stack:** React, TypeScript, Vite, React Router, TanStack Query, Recharts, Lucide React, Vitest, Testing Library, FastAPI, SQLAlchemy, PostgreSQL/pgvector, Redis Streams, Temporal, MinIO, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-09-21-react-demo-console-design.md`

## Global Constraints
- Docker Compose only.
- React must never connect directly to PostgreSQL.
- No new cloud/Kubernetes/Kafka/observability infrastructure.
- OpenAI API key only, default model `gpt-4o-mini`.
- Tenant scope is required on all tenant-owned browse/mutation APIs.
- Existing deterministic ownership boundaries remain unchanged.

## Review Focus
- Tenant A must never see inventory, ledger, state, memory or run data from Tenant B.
- Browser/API routing must work both in Vite dev mode and Nginx Compose mode.
- API failures must render usable error states rather than blank pages.
- Demo scenario results must not claim PASS unless returned values satisfy explicit invariants.
- Final ZIP must not contain `.env` or secret values.

---

### Task 1: Backend browse and operations APIs
**Files:** create/modify `backend/app/api/inventory.py`, `backend/app/api/operations.py`, `backend/app/api/system.py`, `backend/app/services/operations/service.py`, `backend/app/main.py`; add tests.
- [ ] Write failing tests for inventory list/ledger tenant scoping, daily report, schemas and system status.
- [ ] Run targeted tests and confirm expected failures.
