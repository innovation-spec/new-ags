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
