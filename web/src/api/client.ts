import type {
  AgentRun, AgentRunDetail, ChatResult, Customer, DailyReport, InventoryRow, LedgerRow, MemoryEntry,
  ModelGroup, Product, Recommendation, SchemaRegistry, StateEvent, StateValue, Stats, SystemStatus, Tenant,
} from './types'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

export class ApiError extends Error {
  status: number
  payload: unknown
  constructor(status: number, message: string, payload?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

function query(params: Record<string, string | number | boolean | undefined | null>) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  })
  const suffix = search.toString()
  return suffix ? `?${suffix}` : ''
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body && !headers.has('content-type')) headers.set('content-type', 'application/json')
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const isJson = response.headers.get('content-type')?.includes('application/json')
  const payload = isJson ? await response.json() : await response.text()
  if (!response.ok) {
    const message = typeof payload === 'object' && payload && 'detail' in payload
      ? String((payload as { detail: unknown }).detail)
      : typeof payload === 'string' ? payload : `Request failed (${response.status})`
    throw new ApiError(response.status, message, payload)
  }
  return payload as T
}

const post = <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) })

export const api = {
  health: () => request<{ status: string; service: string; openai_enabled: boolean }>('/health'),
  system: {
    status: () => request<SystemStatus>('/system/status'),
    schemas: () => request<SchemaRegistry>('/schemas'),
  },
  tenants: {
    list: () => request<Tenant[]>('/tenants'),
    customers: (tenantId: string, limit = 100) => request<Customer[]>(`/tenants/${encodeURIComponent(tenantId)}/customers${query({ limit })}`),
  },
  catalog: {
    products: (tenantId: string, options: { limit?: number; category?: string } = {}) =>
      request<Product[]>(`/catalog/products${query({ tenant_id: tenantId, limit: options.limit ?? 100, category: options.category })}`),
  },
  inventory: {
    list: (tenantId: string, options: { limit?: number; search?: string; category?: string } = {}) =>
      request<InventoryRow[]>(`/inventory${query({ tenant_id: tenantId, limit: options.limit ?? 200, search: options.search, category: options.category })}`),
    stock: (tenantId: string, skuId: string) => request<Record<string, unknown>>(`/inventory/${encodeURIComponent(skuId)}${query({ tenant_id: tenantId })}`),
    ledger: (tenantId: string, skuId: string, limit = 100) => request<LedgerRow[]>(`/inventory/${encodeURIComponent(skuId)}/ledger${query({ tenant_id: tenantId, limit })}`),
    reserve: (body: { tenant_id: string; sku_id: string; quantity: number; idempotency_key: string }) => post<Record<string, unknown>>('/inventory/reserve', body),
  },
  recommendations: {
    generate: (tenantId: string, customerId: string, limit = 10) => post<Recommendation>(`/recommendations/${encodeURIComponent(customerId)}`, { tenant_id: tenantId, limit }),
    latest: (tenantId: string, customerId: string) => request<Recommendation>(`/recommendations/${encodeURIComponent(customerId)}/latest${query({ tenant_id: tenantId })}`),
  },
  agents: {
    chat: (tenantId: string, customerId: string, message: string) => post<ChatResult>('/agents/chat', { tenant_id: tenantId, customer_id: customerId, message }),
    runs: (tenantId: string, limit = 50) => request<AgentRun[]>(`/agents/runs${query({ tenant_id: tenantId, limit })}`),
    run: (tenantId: string, runId: string) => request<AgentRunDetail>(`/agents/runs/${encodeURIComponent(runId)}${query({ tenant_id: tenantId })}`),
  },
  state: {
    get: (tenantId: string, entityType: string, entityId: string) => request<StateValue>(`/state/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}${query({ tenant_id: tenantId })}`),
    events: (tenantId: string, entityType: string, entityId: string) => request<StateEvent[]>(`/state/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/events${query({ tenant_id: tenantId })}`),
    patch: (entityType: string, entityId: string, body: { tenant_id: string; agent_id: string; operation_id: string; base_version: number; patch: Record<string, unknown>; merge_policy: string }) =>
      post<Record<string, unknown>>(`/state/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/patch`, body),
  },
  memory: {
    list: (tenantId: string, ownerType?: string, ownerId?: string) => request<MemoryEntry[]>(`/memory${query({ tenant_id: tenantId, owner_type: ownerType, owner_id: ownerId })}`),
    save: (body: { tenant_id: string; owner_type: string; owner_id: string; memory_type: string; content: Record<string, unknown>; importance: number; source?: string; ttl_seconds?: number }) => post<MemoryEntry>('/memory', body),
    prune: (tenantId: string) => post<Record<string, unknown>>(`/memory/prune${query({ tenant_id: tenantId })}`),
  },
  models: {
    list: () => request<ModelGroup[]>('/models'),
    activate: (name: string, version: string) => post<Record<string, unknown>>(`/models/${encodeURIComponent(name)}/${encodeURIComponent(version)}/activate`),
  },
  operations: {
    daily: (tenantId: string) => request<DailyReport>(`/operations/daily-report${query({ tenant_id: tenantId })}`),
  },
  demo: {
    stats: (tenantId: string) => request<Stats>(`/demo/stats${query({ tenant_id: tenantId })}`),
    inventoryRace: (tenantId: string, stock = 5, attempts = 100) => post<Record<string, unknown>>(`/demo/inventory-race${query({ tenant_id: tenantId, stock, attempts })}`),
    stateConflict: (tenantId: string, operations = 100) => post<Record<string, unknown>>(`/demo/state-conflict${query({ tenant_id: tenantId, operations })}`),
    externalFailure: (tenantId: string, scenario: string, value = 'DEMO-SKU') => post<Record<string, unknown>>(`/demo/external-failure${query({ tenant_id: tenantId, query: value, scenario })}`),
    recommendation: (tenantId: string, customerId: string, limit = 10) => post<Recommendation>(`/demo/recommendation${query({ tenant_id: tenantId, customer_id: customerId, limit })}`),
    memoryPrune: (tenantId: string) => post<Record<string, unknown>>(`/demo/memory-prune${query({ tenant_id: tenantId })}`),
    ppo: (iterations = 60, seed = 42) => post<Record<string, unknown>>(`/demo/ppo-shadow${query({ iterations, seed })}`),
  },
}
