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
    {runs.isLoading ? <Loading /> : runs.error ? <ErrorState error={runs.error} /> : !runs.data?.length ? <Card><CardContent className="empty-state"><Bot /><h3>No runs yet</h3><p>Use AI Assistant to create an agent run.</p></CardContent></Card> : <div className="split-browser">
      <Card className="run-list"><CardContent className="p-2">{runs.data.map(run => <Button key={run.id} variant="ghost" onClick={() => setRunId(run.id)} className={cn('h-auto w-full justify-between whitespace-normal rounded-lg border-b px-3 py-3 text-left', run.id === runId && 'bg-primary/10 text-primary')}><div className="min-w-0"><StatusBadge status={run.status} /><strong className="mt-1.5 block truncate text-foreground">{run.input_text || 'Agent request'}</strong><small className="block truncate text-muted-foreground">{run.id}</small></div><Route className="size-4 shrink-0" /></Button>)}</CardContent></Card>
      <Card className="run-detail">{detail.isLoading ? <CardContent className="p-5"><Loading /></CardContent> : detail.error ? <CardContent className="p-5"><ErrorState error={detail.error} /></CardContent> : detail.data && <><CardHeader className="flex-row items-start justify-between gap-4 space-y-0"><div><p className="eyebrow">Run {detail.data.id.slice(0, 8)}</p><CardTitle className="mt-1">{detail.data.input_text || 'Agent run'}</CardTitle></div><StatusBadge status={detail.data.status} /></CardHeader><CardContent>{detail.data.output_text && <div className="answer-card"><Bot className="size-4" /><p>{detail.data.output_text}</p></div>}<div className="event-timeline">{detail.data.events.map((event, index) => <div className="event-node" key={`${event.created_at}-${index}`}><div className="event-rail"><span>{index + 1}</span></div><div className="event-card"><div className="event-head"><div><strong>{event.event_type}</strong><small>{event.agent}</small></div><span><Clock3 className="size-3" />{new Date(event.created_at).toLocaleTimeString()}</span></div>{Object.keys(event.payload || {}).length > 0 && <pre className="json-block compact">{JSON.stringify(event.payload, null, 2)}</pre>}</div></div>)}</div></CardContent></>}</Card>
    </div>}
  </>
}
