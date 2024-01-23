# Agasthya React Console — shadcn/ui Functional Redesign

## Goal
Refactor the existing React/Vite systems console onto a reusable shadcn/ui component system while preserving all backend-driven workflows and improving interaction feedback, accessibility, responsive behavior, and demo readiness.

## Locked architecture
- FastAPI remains the only browser data boundary.
- PostgreSQL/pgvector, Redis/Redis Streams, Temporal, MinIO and OpenAI remain unchanged.
- Docker Compose remains the local deployment method.
- React Router and TanStack Query remain the client routing/data layer.
