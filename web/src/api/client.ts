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
