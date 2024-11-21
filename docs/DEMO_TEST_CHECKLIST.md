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
- OpenAI badge shows enabled.
- Sending a prompt creates an agent run and returns an explanation grounded in backend tools.
- Recommended product cards contain actual backend product IDs/scores rather than invented catalog rows.

## 3. Recommendations

- Choose a customer and generate Top-K recommendations.
- Items show score/rank and model/version.
- Inventory-ineligible products are not returned as normal available recommendations.
- Change tenant/customer and regenerate.

Expected: results are persisted and are visible through the latest recommendation API for that customer.

## 4. Catalog & Inventory

- Search by product/brand/SKU.
- Filter by category.
- Click **Inspect** to open the stock drawer.
- Reserve one available unit.
- Available stock and version refresh in the open drawer.
- Ledger shows a new `RESERVED` event.
- Attempting to reserve more than available is blocked or returns the backend conflict message.

Expected: stock never becomes negative and reservations are tenant-scoped.

## 5. Agent Runs

- Create activity from AI Assistant.
- Open Agent Runs and select the new run.
- Status, input/output and ordered agent/tool events render.

Expected: event history corresponds to the selected run and tenant.

## 6. Shared State Lab

- Load a customer/entity state.
- Apply a patch using the displayed base version.
- Confirm state version increments and event history records the operation.
- Run the 100-operation conflict scenario.

Expected: the demo result is **PASS** only when all operations are accounted for and the final count matches applied + merged changes.

## 7. Resilience & PPO

Run each external-data scenario:
- timeout,
- rate limiting / 429,
- malformed data,
- source conflict.

Then run PPO shadow evaluation.

Expected: provider failures are represented without crashing the page; deterministic credibility arbitration remains authoritative and PPO is reported as shadow/non-authoritative.

## 8. Memory

- Create a working/episodic memory record.
- Verify it appears in the tenant list.
- Run prune.

Expected: expired eligible records are removed while active records remain.

## 9. Models & Schemas

- Model versions load from registry metadata.
- Activate a model version and refresh.
- Open schema definitions.

Expected: one active model version is shown for a model group and schema registry reports version `1.0` with typed request/event contracts.

## 10. Daily Operations

- Open Daily Operations.
- Refresh the 24-hour report.
- Inspect agent status distribution, state conflict totals, low-stock rows and anomaly signals.

Expected: no LLM-generated operational facts; values come from local application tables.

## 11. R&D Coverage

- Confirm P1–P9 all render.
- Each phase links to the page demonstrating that capability.
- Ticket/hour totals show **403 tickets** and **13,936.52 reconstructed hours**.

Expected: coverage is presented as demo traceability, not as proof that this source tree is the original 2024 codebase.

## 12. Demo Lab

Run individually, then **Run full demo suite**:
- Inventory race
- State conflict
- External fallback
- Recommendation
- Memory pruning
- PPO shadow

Expected:
- Inventory race is **PASS** only when successful reservations do not exceed initial stock and available stock is non-negative.
- State conflict is **PASS** only when all operations are accounted for and final state is correct.
- Other scenarios render their returned evidence/error explicitly.

## Automated verification

```bash
./scripts/verify_project.sh
```

After the stack is running:

```bash
RUN_INFRA_TESTS=1 PYTHONPATH=backend pytest -q tests/integration/test_infrastructure.py
SMOKE_BASE_URL=http://localhost:18000 PYTHONPATH=backend pytest -q tests/integration/test_smoke.py
WEB_BASE_URL=http://localhost:13000 PYTHONPATH=backend pytest -q tests/integration/test_web_console.py
```

For the local Compose host ports, the infrastructure tests default to:

- Redis `localhost:16379`
- MinIO `localhost:19000`
- Temporal `localhost:17233`
