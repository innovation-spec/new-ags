# Final Functional Review — React + shadcn/ui Console

## Scope delivered

The web console is a React 18 + TypeScript + Vite single-page application served by Nginx. It uses local shadcn/ui-style component source and keeps FastAPI as the only browser data boundary. PostgreSQL/pgvector, Redis/Redis Streams, Temporal, MinIO and optional OpenAI remain behind the backend exactly as in the local architecture.

## Functional coverage

| Area | User-visible functionality | Backing system |
|---|---|---|
| Overview | Tenant KPIs, service state, phase coverage, navigation shortcuts | FastAPI stats/system APIs |
| AI Assistant | Customer selection, prompt submission, grounded recommendation response, agent run creation | OpenAI when configured + deterministic backend fallback |
| Recommendations | Generate/reload Top-K, customer context, model/version and scores | Recommendation service + local DB/model registry |
| Catalog & Inventory | Search/filter, inspect SKU, current stock/version, reserve quantity, ledger history | PostgreSQL transactional inventory service |
| Agent Runs | Run list, selection and ordered event/tool timeline | Agent run/event tables + Temporal-backed execution when enabled |
| Shared State Lab | Load state, submit versioned patch, inspect events, run conflict stress scenario | State coordinator + optimistic concurrency/merge rules |
| Resilience & PPO | Timeout/429/malformed/conflict provider simulations and non-authoritative PPO shadow evaluation | External-data service + PPO experiment module |
| Memory | List/save/prune working, episodic and semantic entries | Redis/PostgreSQL/pgvector/MinIO memory tiers |
| Models & Schemas | Model versions, activation mutation, typed schema registry | PostgreSQL metadata + MinIO artifacts + Pydantic contracts |
| Daily Operations | 24-hour metrics, agent/state/stock anomaly signals | Local application tables; no LLM-generated metrics |
| R&D Coverage | P1–P9 capability/ticket/hour mapping and deep links | Static traceability derived from supplied workbook |
| Demo Lab | Inventory race, state conflict, external fallback, recommendation, memory prune and PPO scenarios with explicit evidence | Real demo endpoints |

## shadcn/ui integration

The UI source is centralized under `web/src/components/ui/` and includes Button, Card, Badge, Input, Textarea, Label, NativeSelect, Table, Skeleton, Alert, Separator, Progress, Sheet, Tabs, Slider and Sonner. Theme tokens are CSS variables in `web/src/styles.css`; `components.json` is configured for the `new-york` style and Vite aliases.

Application pages no longer declare raw `<button>`, `<input>`, `<select>` or `<textarea>` controls directly. They consume the shared UI primitives, preserving consistent accessibility states, disabled states, keyboard focus treatment and theming.

## Mutation behavior checked in source

- Inventory reservation refreshes stock, inventory rows and ledger data.
