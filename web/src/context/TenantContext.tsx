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
