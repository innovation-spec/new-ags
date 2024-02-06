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

