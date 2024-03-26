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

Open:

- **React console:** http://localhost:13000
- **FastAPI direct:** http://localhost:18000
- **FastAPI Swagger:** http://localhost:18000/docs
- **Temporal UI:** http://localhost:18080
- **MinIO API:** http://localhost:19000
- **MinIO console:** http://localhost:19001 (`agasthya` / `agasthya-demo-secret`)

The non-default host ports intentionally avoid common local conflicts while Docker services continue to use their normal internal ports.

## React + shadcn/ui console

The primary web interface uses local shadcn/ui-style component source with the `new-york` design language, Tailwind CSS variables, Lucide icons, Radix primitives for accessible Sheet/Tabs/Slider behavior, Sonner toasts, and light/dark/system themes. The browser remains a thin client over FastAPI; no business truth is moved into the frontend.

### Features

- **Overview** — live tenant KPIs, system component status and 2024 phase coverage.
- **AI Assistant** — optional OpenAI-powered explanation/tool selection grounded by deterministic recommendations.
- **Recommendations** — Top-K generation, profile features, score visualization and model/version display.
- **Catalog & Inventory** — searchable local stock, reservation mutation and ledger history.
- **Agent Runs** — ordered supervisor/tool execution timeline.
- **Shared State Lab** — versioned patches, event lineage and 100-operation conflict test.
- **Resilience & PPO** — timeout/429/malformed/conflict simulations plus PPO shadow evaluation.
- **Memory** — save/list/prune working/episodic/semantic memory.
- **Models & Schemas** — MinIO-backed model versions and versioned Pydantic contract registry.
- **Daily Operations** — 24-hour application report with agent/state/low-inventory anomaly rules.
- **R&D Coverage** — mapping of all nine workbook phases to working demo features.
- **Demo Lab** — one-click technical scenarios with explicit invariant interpretation.

The previous Streamlit source remains under `ui/` as legacy reference, but Docker Compose now serves the React UI.

## OpenAI

Only an API key is needed. The default small demo model is:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

With no key, `/health` reports `openai_enabled: false`; recommendations, inventory, state, external-data, PPO, memory and operations demos continue to work.

The LLM never owns inventory quantities, tenant isolation, state versions, merge rules, recommendation scores or credibility arbitration.

## Useful commands

Run the complete local verification helper (it installs frontend dependencies if needed):

```bash
./scripts/verify_project.sh
```

Or run individual checks:

```bash
# Backend + scenario tests
PYTHONPATH=backend pytest -q backend/tests tests/demo_scenarios tests/concurrency

# React tests (requires npm dependencies)
npm --prefix web install
npm --prefix web test
npm --prefix web run typecheck
npm --prefix web run build

# Validate Compose
# docker compose config

# Re-run deterministic bootstrap
docker compose run --rm bootstrap

# Stop but keep local data
docker compose down
