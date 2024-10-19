# React Demo Acceptance Checklist

Use this after:

```bash
cp .env.example .env
# optionally set OPENAI_API_KEY
docker compose up --build
```

Open `http://localhost:13000`.

## 0. shadcn/ui shell and interaction quality

- Desktop sidebar renders all 12 application areas and can collapse/expand.
- At tablet/mobile width, the sidebar is replaced by an accessible Sheet navigation drawer.
- Theme control switches light, dark and system modes and persists the selection locally.
- Tenant selection uses the shared shadcn-styled select wrapper and switching tenants refreshes API-backed data.
- Buttons, cards, forms, tables, tabs, sheets, sliders, badges, alerts, skeletons and toast feedback use the shared `web/src/components/ui` primitives rather than page-local raw controls.
- Mutation success/failure is surfaced through Sonner toasts and relevant queries refresh after mutations.

Expected: navigation, theme, tenant switching and feedback remain usable without a page reload and do not bypass FastAPI.

## 1. Startup and tenant isolation

- Overview loads without a browser error.
- Active Tenant contains **Demo Retailer 1** and **Demo Retailer 2**.
- Switching tenants changes KPI/data queries without a page reload.
- Browser network calls go to `/api/...`; the browser never connects to PostgreSQL directly.
- Local service status shows database, Redis, MinIO, Temporal and OpenAI state.

Expected: tenant-specific data changes and no data from the previously selected tenant remains in data tables after queries refresh.

## 2. AI Assistant

With no OpenAI key:
- OpenAI badge shows disabled.
- Selecting a customer and sending a prompt still produces deterministic recommendation-backed output through the fallback path.

With an OpenAI key:
