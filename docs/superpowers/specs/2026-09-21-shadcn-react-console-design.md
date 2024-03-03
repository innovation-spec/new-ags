# Agasthya React Console — shadcn/ui Functional Redesign

## Goal
Refactor the existing React/Vite systems console onto a reusable shadcn/ui component system while preserving all backend-driven workflows and improving interaction feedback, accessibility, responsive behavior, and demo readiness.

## Locked architecture
- FastAPI remains the only browser data boundary.
- PostgreSQL/pgvector, Redis/Redis Streams, Temporal, MinIO and OpenAI remain unchanged.
- Docker Compose remains the local deployment method.
- React Router and TanStack Query remain the client routing/data layer.
- shadcn/ui local component source is added under `web/src/components/ui` with `new-york` styling, CSS variables, Lucide icons and the `@/*` alias.
- React stays on 18.x; no framework migration is required.

## Functional requirements
1. Preserve all existing screens and API calls: Overview, Assistant, Recommendations, Inventory, Agent Runs, Shared State, Resilience/PPO, Memory, Models/Schemas, Operations, R&D Coverage and Demo Lab.
2. Preserve tenant switching and local persistence.
3. All mutations must expose pending/success/error feedback and invalidate/refetch affected queries.
4. Inventory reservations must refresh displayed stock and ledger state.
5. AI Assistant must remain useful with or without an OpenAI key.
