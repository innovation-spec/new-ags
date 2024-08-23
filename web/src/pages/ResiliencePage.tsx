import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { FlaskConical, Play, ShieldCheck } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ErrorState } from '../components/AsyncState'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { cn } from '@/lib/utils'
import { Slider } from '@/components/ui/slider'

const scenarios = [
  { value: 'timeout', label: 'Timeout', description: 'Primary provider times out; retry/fallback path should recover.' },
  { value: 'rate_limit', label: 'Rate limit / 429', description: 'Exercises throttling-aware retry behavior.' },
  { value: 'malformed', label: 'Malformed response', description: 'Invalid provider payload should not silently become authoritative.' },
  { value: 'conflict', label: 'Conflicting sources', description: 'Queries two sources and applies deterministic credibility selection.' },
  { value: 'normal', label: 'Normal', description: 'Healthy provider response baseline.' },
]

export function ResiliencePage() {
  const { tenantId } = useTenant()
  const [scenario, setScenario] = useState('timeout')
  const [queryText, setQueryText] = useState('DEMO-SKU')
  const [external, setExternal] = useState<Record<string, unknown> | null>(null)
  const [iterations, setIterations] = useState(60)
  const [ppo, setPpo] = useState<Record<string, any> | null>(null)
  const externalMutation = useMutation({ mutationFn: () => api.demo.externalFailure(tenantId, scenario, queryText), onSuccess: data => { setExternal(data); toast.success('External-data flow completed') }, onError: error => toast.error('External-data flow failed', { description: error instanceof Error ? error.message : String(error) }) })
  const ppoMutation = useMutation({ mutationFn: () => api.demo.ppo(iterations, 42), onSuccess: data => { setPpo(data); toast.success('PPO shadow evaluation completed') }, onError: error => toast.error('PPO evaluation failed', { description: error instanceof Error ? error.message : String(error) }) })
  const ppoChart = ppo ? [{ stage: 'Before', accuracy: Number(ppo.before?.accuracy ?? 0), reward: Number(ppo.before?.average_reward ?? 0) }, { stage: 'After', accuracy: Number(ppo.after?.accuracy ?? 0), reward: Number(ppo.after?.average_reward ?? 0) }] : []

  return <>
    <PageHeader eyebrow="Phases 5 + 6" title="Resilience & PPO research" description="Exercise external-data failures, inspect fallback/provenance, and evaluate PPO only in shadow mode." />
    <div className="two-column">
      <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">External retrieval</p><CardTitle className="mt-1">Failure simulator</CardTitle></div><ShieldCheck className="size-5 text-primary" /></CardHeader><CardContent><div className="scenario-grid">{scenarios.map(item => <Button key={item.value} type="button" variant="outline" className={cn("h-auto items-start justify-start whitespace-normal p-3 text-left", scenario === item.value && "border-primary bg-primary/10 text-primary")} onClick={() => setScenario(item.value)}><span><strong className="block text-sm">{item.label}</strong><span className="mt-1 block text-xs font-normal text-muted-foreground">{item.description}</span></span></Button>)}</div><div className="space-y-2"><label className="text-xs font-medium text-muted-foreground">Lookup key</label><Input value={queryText} onChange={e => setQueryText(e.target.value)} /></div><Button className="mt-4" onClick={() => externalMutation.mutate()} disabled={externalMutation.isPending}><Play />{externalMutation.isPending ? 'Running…' : 'Run external-data flow'}</Button>{externalMutation.error && <div className="mt-4"><ErrorState error={externalMutation.error} /></div>}{external && <><div className="result-summary"><div><span>Fallback used</span><strong>{String(external.fallback_used)}</strong></div><div><span>Attempts</span><strong>{Array.isArray(external.attempts) ? external.attempts.length : 0}</strong></div><div><span>Candidates</span><strong>{Array.isArray(external.candidates) ? external.candidates.length : 0}</strong></div></div><h3>Selected result</h3><pre className="json-block">{JSON.stringify(external.selected ?? null, null, 2)}</pre><details><summary>Attempts & provenance</summary><pre className="json-block compact">{JSON.stringify({ attempts: external.attempts, candidates: external.candidates }, null, 2)}</pre></details></>}</CardContent></Card>
      <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Shadow experiment</p><CardTitle className="mt-1">PPO source selection</CardTitle></div><FlaskConical className="size-5 text-primary" /></CardHeader><CardContent><Alert><AlertTitle>Safety boundary</AlertTitle><AlertDescription>The PPO policy never becomes authoritative here. Deterministic credibility rules continue to choose production truth.</AlertDescription></Alert><div className="mt-4 space-y-2"><div className="flex justify-between text-xs font-medium text-muted-foreground"><span>Training iterations</span><span>{iterations}</span></div><Slider min={10} max={120} step={10} value={[iterations]} onValueChange={([value]) => setIterations(value)} /></div><Button className="mt-4" onClick={() => ppoMutation.mutate()} disabled={ppoMutation.isPending}><Play />{ppoMutation.isPending ? 'Training shadow policy…' : 'Run PPO shadow evaluation'}</Button>{ppoMutation.error && <div className="mt-4"><ErrorState error={ppoMutation.error} /></div>}{ppo && <><div className="chart-box short"><ResponsiveContainer width="100%" height="100%"><BarChart data={ppoChart}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="stage" /><YAxis domain={[-0.5, 1]} /><Tooltip /><Legend /><Bar dataKey="accuracy" fill="hsl(var(--primary))" radius={[5,5,0,0]} /><Bar dataKey="reward" fill="#4f8cff" radius={[5,5,0,0]} /></BarChart></ResponsiveContainer></div><div className="result-summary"><div><span>Before accuracy</span><strong>{(Number(ppo.before?.accuracy ?? 0) * 100).toFixed(1)}%</strong></div><div><span>After accuracy</span><strong>{(Number(ppo.after?.accuracy ?? 0) * 100).toFixed(1)}%</strong></div><div><span>Mode</span><strong>{ppo.mode}</strong></div></div><details><summary>Shadow decisions</summary><pre className="json-block compact">{JSON.stringify(ppo.decisions, null, 2)}</pre></details></>}</CardContent></Card>
    </div>
  </>
}
