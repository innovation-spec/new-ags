# Agasthya React Demo Console Design

## Goal
Replace the demo's primary Streamlit presentation layer with a polished React/TypeScript web console that exercises the existing local FastAPI/PostgreSQL system end-to-end and visibly demonstrates the nine 2024 engineering workstreams from the supplied workbook.

## Constraints
- Local-first only; Docker Compose is the deployment surface.
- PostgreSQL/pgvector remains the source of truth. React never accesses the database directly.
- FastAPI remains the only application API boundary.
- Redis/Redis Streams, Temporal, MinIO and OpenAI API remain as already designed.
- OpenAI uses an API key only; default demo model is `gpt-4o-mini`.
- No Kubernetes, Kafka, cloud deployment, Grafana/Prometheus/OpenTelemetry, or local LLM.
- Existing deterministic rules continue to own tenant isolation, inventory, recommendation scores, state versions, credibility and merge decisions.

## Frontend Architecture
A Vite React + TypeScript single-page application is built into an Nginx container. Nginx serves the static SPA and reverse-proxies `/api/*` to FastAPI, so browser traffic is same-origin and no broad CORS policy is required.

Core frontend libraries:
- React + TypeScript + Vite
