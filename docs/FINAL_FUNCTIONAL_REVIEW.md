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
