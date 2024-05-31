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
6. Demo Lab must retain explicit invariant PASS/FAIL interpretation.
7. State conflict and inventory race demos must remain directly runnable.
8. Add dark/light/system theme support without changing application data.
9. Add responsive desktop/tablet/mobile navigation behavior.
10. Use shadcn/ui primitives for actions, cards, badges, inputs, native selects, textareas, tables, tabs/sheets where applicable, loading states and toast feedback.

## UX requirements
- Dense engineering-console information hierarchy without visual clutter.
- Sidebar navigation, sticky top context bar, active tenant visibility and runtime health.
- Accessible labels, focus rings, disabled states and keyboard-operable interactive elements.
- Loading, empty and error states remain explicit rather than silently blank.
- Destructive or state-changing actions provide immediate visual confirmation.

## Out of scope
- Backend architecture redesign.
- New cloud infrastructure.
- Authentication/RBAC implementation.
- Kafka/Kubernetes/observability stacks.
- Replacing the deterministic recommendation/state/inventory authority with the LLM.
