import { describe, expect, it, vi } from 'vitest'
import { ApiError, api } from './client'

describe('api client', () => {
  it('prefixes requests with /api and returns json', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
