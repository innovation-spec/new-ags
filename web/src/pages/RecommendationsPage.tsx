import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { RefreshCw, Sparkles } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import type { Recommendation } from '../api/types'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ProductCard } from '../components/ProductCard'
import { ErrorState, Loading } from '../components/AsyncState'
import { MetricCard } from '../components/MetricCard'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'

export function RecommendationsPage() {
  const { tenantId } = useTenant()
  const customers = useQuery({ queryKey: ['customers', tenantId], queryFn: () => api.tenants.customers(tenantId, 100), enabled: Boolean(tenantId) })
  const [customerId, setCustomerId] = useState('')
  const [limit, setLimit] = useState(10)
  const [result, setResult] = useState<Recommendation | null>(null)
  const activeCustomer = customerId || customers.data?.[0]?.id || ''
  const generate = useMutation({ mutationFn: () => api.recommendations.generate(tenantId, activeCustomer, limit), onSuccess: data => { setResult(data); toast.success(`Generated ${data.items.length} recommendations`) }, onError: error => toast.error('Recommendation generation failed', { description: error instanceof Error ? error.message : String(error) }) })
  const latest = useMutation({ mutationFn: () => api.recommendations.latest(tenantId, activeCustomer), onSuccess: data => { setResult(data); toast.success('Loaded latest recommendation set') }, onError: error => toast.error('No latest recommendation available', { description: error instanceof Error ? error.message : String(error) }) })

  if (customers.isLoading) return <><PageHeader title="Recommendation explorer" description="Inventory-aware candidate generation and deterministic ranking." /><Loading /></>
  if (customers.error) return <ErrorState error={customers.error} />

  return <>
    <PageHeader eyebrow="Inventory-aware ML pipeline" title="Recommendation explorer" description="Generate ranked products, inspect customer features, model version and scoring reasons." />
    <Card className="mb-5"><CardContent className="flex flex-wrap items-end gap-3 p-4"><div className="min-w-[260px] flex-1 space-y-2"><label className="text-xs font-medium text-muted-foreground">Customer</label><NativeSelect value={activeCustomer} onChange={e => setCustomerId(e.target.value)}>{customers.data?.map(c => <NativeSelectOption key={c.id} value={c.id}>{c.name} · {c.segment || 'no segment'}</NativeSelectOption>)}</NativeSelect></div><div className="w-28 space-y-2"><label className="text-xs font-medium text-muted-foreground">Top K</label><Input type="number" min={1} max={20} value={limit} onChange={e => setLimit(Math.max(1, Math.min(20, Number(e.target.value))))} /></div><Button onClick={() => generate.mutate()} disabled={!activeCustomer || generate.isPending}><Sparkles />{generate.isPending ? 'Generating…' : 'Generate'}</Button><Button variant="outline" onClick={() => latest.mutate()} disabled={!activeCustomer || latest.isPending}><RefreshCw />Load latest</Button></CardContent></Card>
    {(generate.error || latest.error) && <ErrorState error={generate.error || latest.error} />}
    {result ? <>
      <div className="metric-grid three"><MetricCard label="Model" value={result.model_name} note="authoritative ranker" /><MetricCard label="Version" value={result.model_version} note="MinIO-backed registry" /><MetricCard label="Returned" value={result.items.length} note="inventory eligible" /></div>
      <div className="two-column wide-left">
        <Card><CardHeader><p className="eyebrow">Ranking</p><CardTitle>Top recommendation scores</CardTitle></CardHeader><CardContent><div className="chart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={result.items.slice(0, 10)} margin={{ left: 8, right: 12 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" hide /><YAxis domain={[0, 1]} /><Tooltip /><Bar dataKey="score" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} /></BarChart></ResponsiveContainer></div><div className="product-stack">{result.items.map(item => <ProductCard key={item.product_id} item={item} />)}</div></CardContent></Card>
        <Card className="sticky-panel"><CardHeader><p className="eyebrow">Feature snapshot</p><CardTitle>Customer profile</CardTitle></CardHeader><CardContent><pre className="json-block mt-0">{JSON.stringify(result.profile ?? { note: 'Latest persisted recommendations do not include the transient profile snapshot.' }, null, 2)}</pre></CardContent></Card>
      </div>
    </> : <Card><CardContent className="empty-state"><Sparkles /><h3>No recommendation loaded</h3><p>Choose a customer and generate or load their latest recommendation set.</p></CardContent></Card>}
  </>
}
