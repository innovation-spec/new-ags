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
      else if (id === 'recommendation') { title = 'Inventory-aware recommendation'; if (!firstCustomer) throw new Error('No seeded customer available'); result = await api.demo.recommendation(tenantId, firstCustomer, 10) as unknown as Record<string, unknown> }
      else throw new Error(`Unknown scenario ${id}`)
      setResults(prev => [{ id, title, kind, result }, ...prev.filter(item => item.id !== id)])
      toast.success(`${title} completed`)
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      setResults(prev => [{ id, title: id, kind: 'generic', result: { error: message } }, ...prev.filter(item => item.id !== id)])
      toast.error(`Scenario ${id} failed`, { description: message })
    } finally { setRunning('') }
  }

  async function runAll() { for (const id of ['inventory', 'state', 'resilience', 'recommendation', 'memory', 'ppo']) await runOne(id) }

  const scenarios = [
    { id: 'inventory', title: 'Inventory race', copy: '100 reservation attempts against five units.', icon: Boxes },
    { id: 'state', title: 'State conflict', copy: '100 stale-base additive patches.', icon: GitBranch },
    { id: 'resilience', title: 'External fallback', copy: 'Timeout, retry and provider fallback.', icon: ShieldCheck },
    { id: 'recommendation', title: 'Recommendation', copy: 'Generate an inventory-aware ranked set.', icon: Sparkles },
    { id: 'memory', title: 'Memory pruning', copy: 'Create then remove an expired working memory.', icon: BrainCircuit },
    { id: 'ppo', title: 'PPO shadow', copy: 'Train/evaluate the source-selection shadow policy.', icon: FlaskConical },
  ]

  return <>
    <PageHeader eyebrow="Interactive verification" title="Demo lab" description="Run the technical scenarios directly from the website and inspect the returned invariants." actions={<><Button variant="outline" onClick={() => setResults([])}><RefreshCw />Clear</Button><Button onClick={runAll} disabled={Boolean(running)}><Play />Run full demo suite</Button></>} />
    <div className="scenario-cards">{scenarios.map(({ id, title, copy, icon: Icon }) => <Card key={id}><CardContent className="grid grid-cols-[auto_1fr_auto] items-center gap-3 p-4"><div className="scenario-icon"><Icon /></div><div><h3 className="font-semibold">{title}</h3><p className="mt-1 text-xs text-muted-foreground">{copy}</p></div><Button size="sm" variant="outline" onClick={() => runOne(id)} disabled={Boolean(running)}>{running === id ? 'Running…' : 'Run'}</Button></CardContent></Card>)}</div>
    <div className="result-list">{results.map(entry => <DemoResult key={entry.id} title={entry.title} kind={entry.kind} result={entry.result} />)}{!results.length && <Card><CardContent className="empty-state"><FlaskConical /><h3>No scenarios run yet</h3><p>Run one scenario or execute the complete suite.</p></CardContent></Card>}</div>
  </>
}
