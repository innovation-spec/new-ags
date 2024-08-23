import { describe, expect, it, vi } from 'vitest'
import { ApiError, api } from './client'

describe('api client', () => {
  it('prefixes requests with /api and returns json', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ status: 'ok' }),
    }))
    await expect(api.health()).resolves.toEqual({ status: 'ok' })
    expect(fetch).toHaveBeenCalledWith('/api/health', expect.objectContaining({ headers: expect.any(Headers) }))
  })

  it('throws a typed ApiError for backend detail responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ detail: 'not enough stock' }),
    }))
    await expect(api.inventory.reserve({ tenant_id: 't', sku_id: 's', quantity: 2, idempotency_key: 'x' }))
      .rejects.toEqual(expect.objectContaining({ status: 409, message: 'not enough stock' }))
  })
})
