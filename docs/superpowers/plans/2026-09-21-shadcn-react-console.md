# Agasthya shadcn/ui React Console Implementation Plan

**Goal:** Migrate the existing functional React console to shadcn/ui while preserving every real FastAPI-backed workflow.

**Architecture:** Keep the existing API/context/query architecture and replace presentation primitives with local shadcn/ui components. Retain existing page-level business logic, adding mutation feedback and query refreshes where necessary.

**Tech Stack:** React 18, TypeScript, Vite, React Router, TanStack Query, shadcn/ui patterns, Tailwind CSS 3, Radix primitives, Sonner, Lucide, Recharts.

**Spec:** `docs/superpowers/specs/2026-09-21-shadcn-react-console-design.md`

## Tasks
- [x] Add shadcn configuration, aliases, Tailwind and local UI primitives.
- [x] Add theme provider/toasts and migrate the app shell.
- [x] Migrate common shared components to shadcn primitives.
- [x] Migrate all page actions/forms/tables/panels while preserving API behavior.
- [x] Add mutation success feedback and relevant query invalidation.
- [x] Update documentation and acceptance checks.
- [ ] Run backend suites, frontend static/type checks available in the environment, source audits and package the clean project ZIP.
