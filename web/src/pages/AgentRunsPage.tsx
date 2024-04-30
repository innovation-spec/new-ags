import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bot, Clock3, Route } from 'lucide-react'
import { api } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export function AgentRunsPage() {
  const { tenantId } = useTenant()
  const [runId, setRunId] = useState('')
  const runs = useQuery({ queryKey: ['runs', tenantId], queryFn: () => api.agents.runs(tenantId, 100), enabled: Boolean(tenantId), refetchInterval: 10_000 })
  useEffect(() => { if (runs.data?.length && !runs.data.some(run => run.id === runId)) setRunId(runs.data[0].id) }, [runs.data, runId])
  const detail = useQuery({ queryKey: ['run', tenantId, runId], queryFn: () => api.agents.run(tenantId, runId), enabled: Boolean(tenantId && runId) })

  return <>
    <PageHeader eyebrow="Graph-like execution evidence" title="Agent runs" description="Inspect supervisor/tool execution as an ordered event timeline backed by AgentRun and AgentEvent records." />
