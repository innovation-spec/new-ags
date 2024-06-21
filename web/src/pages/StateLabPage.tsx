import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { GitBranch, Play, PlusCircle } from 'lucide-react'
import { toast } from 'sonner'
import { api, ApiError } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { DemoResult } from '../components/DemoResult'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'

export function StateLabPage() {
  const { tenantId } = useTenant()
  const qc = useQueryClient()
  const [entityType, setEntityType] = useState('customer')
  const [entityId, setEntityId] = useState('demo-customer-state')
  const [patchText, setPatchText] = useState('{\n  "interests": ["running"]\n}')
  const [policy, setPolicy] = useState('replace')
  const [lastPatch, setLastPatch] = useState<Record<string, unknown> | null>(null)
  const [race, setRace] = useState<Record<string, unknown> | null>(null)

  const state = useQuery({ queryKey: ['state', tenantId, entityType, entityId], queryFn: async () => { try { return await api.state.get(tenantId, entityType, entityId) } catch (error) { if (error instanceof ApiError && error.status === 404) return null; throw error } }, enabled: Boolean(tenantId && entityType && entityId) })
  const events = useQuery({ queryKey: ['state-events', tenantId, entityType, entityId], queryFn: () => api.state.events(tenantId, entityType, entityId), enabled: Boolean(tenantId && entityType && entityId) })
  const patch = useMutation({
    mutationFn: async () => { const parsed = JSON.parse(patchText) as Record<string, unknown>; return api.state.patch(entityType, entityId, { tenant_id: tenantId, agent_id: 'react-console', operation_id: `web-${Date.now()}`, base_version: state.data?.version ?? 0, patch: parsed, merge_policy: policy }) },
    onSuccess: async result => { setLastPatch(result); await qc.invalidateQueries({ queryKey: ['state'] }); await qc.invalidateQueries({ queryKey: ['state-events'] }); toast.success('State patch applied') },
    onError: error => toast.error('State patch failed', { description: error instanceof Error ? error.message : String(error) }),
  })
  const conflict = useMutation({ mutationFn: () => api.demo.stateConflict(tenantId, 100), onSuccess: result => { setRace(result); toast.success('Conflict scenario completed') }, onError: error => toast.error('Conflict scenario failed', { description: error instanceof Error ? error.message : String(error) }) })

  return <>
    <PageHeader eyebrow="Concurrency research" title="Shared state lab" description="Create versioned patches, inspect merge outcomes and run the 100-operation conflict demonstration." actions={<Button onClick={() => conflict.mutate()} disabled={conflict.isPending}><Play />{conflict.isPending ? 'Running…' : 'Run 100-patch conflict test'}</Button>} />
    {race && <DemoResult title="Shared-state conflict invariant" kind="state" result={race} />}
    <div className="two-column wide-left">
      <Card><CardContent className="p-5"><div className="mb-5 grid gap-3 sm:grid-cols-2"><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Entity type</label><Input value={entityType} onChange={e => setEntityType(e.target.value)} /></div><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Entity ID</label><Input value={entityId} onChange={e => setEntityId(e.target.value)} /></div></div><div className="panel-header"><div><p className="eyebrow">Current snapshot</p><h2>{entityType}/{entityId}</h2></div><span className="version-badge">v{state.data?.version ?? 0}</span></div>{state.isLoading ? <Loading /> : state.error ? <ErrorState error={state.error} /> : <pre className="json-block">{JSON.stringify(state.data?.state ?? {}, null, 2)}</pre>}<h3>Event lineage</h3><div className="timeline">{events.data?.map(event => <div className="timeline-item" key={event.id}><span className="timeline-dot" /><div><div className="timeline-title"><strong>{event.operation_id}</strong><StatusBadge status={event.status} /></div><small>v{event.base_version} → v{event.resulting_version} · {event.merge_policy}</small><pre className="json-block compact">{JSON.stringify(event.patch, null, 2)}</pre></div></div>)}{!events.data?.length && <p className="muted">No state events yet. Submit the first patch with base version 0.</p>}</div></CardContent></Card>
      <Card className="sticky-panel"><CardHeader><p className="eyebrow">State command</p><CardTitle>Submit typed patch</CardTitle></CardHeader><CardContent className="space-y-4"><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Merge policy</label><NativeSelect value={policy} onChange={e => setPolicy(e.target.value)}><NativeSelectOption value="replace">replace</NativeSelectOption><NativeSelectOption value="additive">additive</NativeSelectOption><NativeSelectOption value="weighted_union">weighted_union</NativeSelectOption><NativeSelectOption value="append">append</NativeSelectOption></NativeSelect></div><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Patch JSON</label><Textarea className="code-input min-h-[230px]" value={patchText} onChange={e => setPatchText(e.target.value)} /></div><Button className="w-full" onClick={() => patch.mutate()} disabled={patch.isPending}><PlusCircle />Submit against v{state.data?.version ?? 0}</Button>{patch.error && <div className="inline-error">{patch.error instanceof Error ? patch.error.message : String(patch.error)}</div>}{lastPatch && <pre className="json-block compact">{JSON.stringify(lastPatch, null, 2)}</pre>}</CardContent></Card>
    </div>
  </>
}
