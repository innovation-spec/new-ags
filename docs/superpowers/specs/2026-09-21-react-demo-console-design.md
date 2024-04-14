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
- React Router for page routing
- TanStack Query for API state/cache/refetch
- Recharts for recommendation/PPO/operations visualizations
- Lucide React for icons
- Vitest + Testing Library for frontend tests

## UX Structure
Persistent left navigation and top context bar. Tenant selection is global and remembered in browser localStorage only as a UI preference; all business data stays in PostgreSQL.

Pages:
1. **Overview** — service health, tenant KPIs, implementation coverage, quick actions.
2. **AI Assistant** — customer-aware chat, recommendation cards, run metadata, OpenAI on/off state.
3. **Recommendations** — customer selector, Top-K control, model/version details, score chart, profile snapshot, latest result.
4. **Catalog & Inventory** — searchable/filterable products with SKU/warehouse stock, availability, reservation form and inventory ledger.
5. **Agent Runs** — run list and event timeline with structured payload inspection.
6. **Shared State Lab** — state viewer, manual patch form, merge-policy controls, event lineage and conflict stress demo.
7. **Resilience & PPO** — timeout/rate-limit/malformed/conflict scenarios, source provenance/credibility output, PPO shadow before/after metrics.
8. **Memory** — list/save/prune memory records with TTL and importance controls.
9. **Models & Schemas** — MinIO-backed model registry activation plus API/schema consistency registry.
10. **Daily Operations** — application-level daily report and anomaly summaries (no observability stack).
11. **R&D Coverage** — nine workbook phases mapped to implemented modules, demo controls and evidence-oriented tests.
12. **Demo Lab** — one-click concurrency, recommendation, resilience, memory and PPO scenarios with explicit pass/fail interpretation.

## Backend Additions
Existing APIs are reused wherever possible. Add only demo/UI gaps:
- `GET /inventory` — tenant-scoped inventory browse rows joined with SKU/product/warehouse information.
- `GET /inventory/{sku_id}/ledger` — tenant-scoped ledger history.
- `GET /operations/daily-report` — derived counts, recent agent status summary and anomaly signals from local database state.
- `GET /schemas` — schema/version registry derived from Pydantic models and event contracts.
- `GET /system/status` — database/Redis/MinIO/Temporal/OpenAI capability status suitable for the local demo dashboard.

## Workbook Coverage
The supplied engineering workbook identifies nine phases. The React console must visibly cover each:
- P1 sequential state processing → Shared State Lab / state versioning
- P2 synchronization & locking → concurrency demo / transactional inventory
- P3 graph/state logging → agent and state event timelines
- P4 memory control → Memory page/pruning
- P5 API resilience → Resilience page
