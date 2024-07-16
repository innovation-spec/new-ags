import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BrainCircuit, Plus, Scissors } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Slider } from '@/components/ui/slider'

export function MemoryPage() {
  const { tenantId } = useTenant()
  const qc = useQueryClient()
  const [ownerType, setOwnerType] = useState('customer')
  const [ownerId, setOwnerId] = useState('demo-customer')
  const [memoryType, setMemoryType] = useState('working')
  const [importance, setImportance] = useState(0.6)
  const [ttl, setTtl] = useState(3600)
  const [content, setContent] = useState('{\n  "note": "Customer prefers running products"\n}')
  const memories = useQuery({ queryKey: ['memory', tenantId], queryFn: () => api.memory.list(tenantId), enabled: Boolean(tenantId) })
  const save = useMutation({ mutationFn: () => api.memory.save({ tenant_id: tenantId, owner_type: ownerType, owner_id: ownerId, memory_type: memoryType, content: JSON.parse(content), importance, source: 'react-console', ttl_seconds: memoryType === 'working' ? ttl : undefined }), onSuccess: async () => { await qc.invalidateQueries({ queryKey: ['memory'] }); toast.success('Memory saved') }, onError: error => toast.error('Memory save failed', { description: error instanceof Error ? error.message : String(error) }) })
  const prune = useMutation({ mutationFn: () => api.memory.prune(tenantId), onSuccess: async data => { await qc.invalidateQueries({ queryKey: ['memory'] }); toast.success(`Pruned ${String(data.deleted ?? 0)} expired record(s)`) }, onError: error => toast.error('Memory prune failed', { description: error instanceof Error ? error.message : String(error) }) })

  return <>
    <PageHeader eyebrow="Phase 4" title="Memory control" description="Inspect persistent memory, create TTL-based working memory and prune expired records." actions={<Button variant="outline" onClick={() => prune.mutate()} disabled={prune.isPending}><Scissors />{prune.isPending ? 'Pruning…' : 'Prune expired'}</Button>} />
    <div className="two-column wide-left">
      <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Persistent records</p><CardTitle className="mt-1">{memories.data?.length ?? 0} memory entries</CardTitle></div><BrainCircuit className="size-5 text-primary" /></CardHeader><CardContent>{memories.isLoading ? <Loading /> : memories.error ? <ErrorState error={memories.error} /> : <div className="memory-grid">{memories.data?.map(memory => <Card key={memory.id}><CardContent className="p-4"><div className="memory-head"><StatusBadge status={memory.memory_type} /><span>importance {memory.importance.toFixed(2)}</span></div><strong>{memory.owner_type}/{memory.owner_id}</strong><pre className="json-block compact">{JSON.stringify(memory.content, null, 2)}</pre><small>{memory.expires_at ? `Expires ${new Date(memory.expires_at).toLocaleString()}` : 'Durable'} · {memory.source}</small></CardContent></Card>)}{!memories.data?.length && <div className="empty-state"><BrainCircuit /><p>No memory records yet.</p></div>}</div>}</CardContent></Card>
      <Card className="sticky-panel"><CardHeader><p className="eyebrow">New memory</p><CardTitle>Store context</CardTitle></CardHeader><CardContent className="space-y-4"><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Owner type</label><Input value={ownerType} onChange={e => setOwnerType(e.target.value)} /></div><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Owner ID</label><Input value={ownerId} onChange={e => setOwnerId(e.target.value)} /></div><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Memory type</label><NativeSelect value={memoryType} onChange={e => setMemoryType(e.target.value)}><NativeSelectOption value="working">working</NativeSelectOption><NativeSelectOption value="episodic">episodic</NativeSelectOption><NativeSelectOption value="semantic">semantic</NativeSelectOption></NativeSelect></div><div className="space-y-2"><div className="flex items-center justify-between text-xs font-medium text-muted-foreground"><span>Importance</span><span>{importance.toFixed(1)}</span></div><Slider min={0} max={1} step={0.1} value={[importance]} onValueChange={([value]) => setImportance(value)} /></div>{memoryType === 'working' && <div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">TTL seconds</label><Input type="number" min={1} value={ttl} onChange={e => setTtl(Math.max(1, Number(e.target.value)))} /></div>}<div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Content JSON</label><Textarea className="code-input min-h-[190px]" value={content} onChange={e => setContent(e.target.value)} /></div><Button className="w-full" onClick={() => save.mutate()} disabled={save.isPending}><Plus />{save.isPending ? 'Saving…' : 'Save memory'}</Button>{save.error && <div className="inline-error">{save.error instanceof Error ? save.error.message : String(save.error)}</div>}{prune.data && <div className="inline-success">Pruned {String(prune.data.deleted ?? 0)} expired record(s).</div>}</CardContent></Card>
    </div>
  </>
}
