# Agasthya shadcn/ui React Console Implementation Plan

**Goal:** Migrate the existing functional React console to shadcn/ui while preserving every real FastAPI-backed workflow.

**Architecture:** Keep the existing API/context/query architecture and replace presentation primitives with local shadcn/ui components. Retain existing page-level business logic, adding mutation feedback and query refreshes where necessary.
