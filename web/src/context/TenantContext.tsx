import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Tenant } from '../api/types'

type TenantContextValue = {
  tenantId: string
  tenant?: Tenant
  tenants: Tenant[]
  setTenantId: (id: string) => void
  isLoading: boolean
  error: Error | null
}

const TenantContext = createContext<TenantContextValue | null>(null)
const STORAGE_KEY = 'agasthya.tenant'

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenantId, setTenantIdState] = useState(() => localStorage.getItem(STORAGE_KEY) || '')
  const tenantsQuery = useQuery({ queryKey: ['tenants'], queryFn: api.tenants.list, staleTime: 60_000 })
  const tenants = tenantsQuery.data ?? []

  useEffect(() => {
    if (!tenants.length) return
    const valid = tenants.some((item) => item.id === tenantId)
    if (!valid) {
      const next = tenants[0].id
      setTenantIdState(next)
      localStorage.setItem(STORAGE_KEY, next)
    }
  }, [tenants, tenantId])

  const setTenantId = (id: string) => {
    setTenantIdState(id)
    localStorage.setItem(STORAGE_KEY, id)
  }

  const value = useMemo<TenantContextValue>(() => ({
    tenantId,
    tenant: tenants.find((item) => item.id === tenantId),
    tenants,
    setTenantId,
    isLoading: tenantsQuery.isLoading,
    error: tenantsQuery.error instanceof Error ? tenantsQuery.error : null,
  }), [tenantId, tenants, tenantsQuery.isLoading, tenantsQuery.error])

  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>
}

export function useTenant() {
  const value = useContext(TenantContext)
  if (!value) throw new Error('useTenant must be used inside TenantProvider')
  return value
}
