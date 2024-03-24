import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Boxes, BrainCircuit, FlaskConical, GitBranch, Play, RefreshCw, ShieldCheck, Sparkles } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { DemoResult } from '../components/DemoResult'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

type ResultEntry = { id: string; title: string; kind: 'inventory' | 'state' | 'generic'; result: Record<string, unknown> }

export function DemoLabPage() {
  const { tenantId } = useTenant()
  const customers = useQuery({ queryKey: ['customers', tenantId], queryFn: () => api.tenants.customers(tenantId, 20), enabled: Boolean(tenantId) })
  const [results, setResults] = useState<ResultEntry[]>([])
  const [running, setRunning] = useState('')
  const firstCustomer = customers.data?.[0]?.id

  async function runOne(id: string) {
    setRunning(id)
    try {
      let title = id, kind: ResultEntry['kind'] = 'generic', result: Record<string, unknown>
      if (id === 'inventory') { title = 'Inventory oversell prevention'; kind = 'inventory'; result = await api.demo.inventoryRace(tenantId, 5, 100) }
      else if (id === 'state') { title = 'Shared-state conflict handling'; kind = 'state'; result = await api.demo.stateConflict(tenantId, 100) }
      else if (id === 'resilience') { title = 'External timeout/fallback'; result = await api.demo.externalFailure(tenantId, 'timeout') }
      else if (id === 'memory') { title = 'Memory pruning'; result = await api.demo.memoryPrune(tenantId) }
      else if (id === 'ppo') { title = 'PPO shadow evaluation'; result = await api.demo.ppo(40, 42) }
