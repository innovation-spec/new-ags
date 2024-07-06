import { useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Activity, AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react'
import { api } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { MetricCard } from '../components/MetricCard'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export function OperationsPage() {
  const { tenantId } = useTenant()
  const report = useQuery({ queryKey: ['daily-report', tenantId], queryFn: () => api.operations.daily(tenantId), enabled: Boolean(tenantId) })
  const statusData = Object.entries(report.data?.agent_status ?? {}).map(([status, count]) => ({ status, count }))
  return <>
    <PageHeader eyebrow="Phase 7" title="Daily operations" description="Application-level activity report and anomaly detection from local database records—no external observability stack required." actions={<Button variant="outline" onClick={() => report.refetch()} disabled={report.isFetching}><RefreshCw className={report.isFetching ? 'animate-spin' : ''} />Refresh</Button>} />
    {report.isLoading ? <Loading /> : report.error ? <ErrorState error={report.error} /> : report.data && <>
      <Alert variant={report.data.healthy ? 'success' : 'destructive'} className="mb-5">{report.data.healthy ? <CheckCircle2 className="size-4" /> : <AlertTriangle className="size-4" />}<AlertTitle>{report.data.healthy ? 'Operational report healthy' : 'High-severity signal detected'}</AlertTitle><AlertDescription>Generated {new Date(report.data.generated_at).toLocaleString()} · trailing {report.data.window_hours} hours</AlertDescription></Alert>
      <div className="metric-grid four"><MetricCard label="Agent failures" value={report.data.agent_status.FAILED ?? 0} /><MetricCard label="Rejected conflicts" value={report.data.state_conflicts.rejected} /><MetricCard label="Merged conflicts" value={report.data.state_conflicts.merged} /><MetricCard label="Low-stock rows" value={report.data.low_inventory_rows} /></div>
      <div className="two-column">
        <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Agent activity</p><CardTitle className="mt-1">Status distribution</CardTitle></div><Activity className="size-5 text-primary" /></CardHeader><CardContent>{statusData.length ? <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={statusData}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="status" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="count" fill="hsl(var(--primary))" radius={[5,5,0,0]} /></BarChart></ResponsiveContainer></div> : <div className="empty-state"><Activity /><p>No agent runs in the reporting window.</p></div>}</CardContent></Card>
        <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Anomaly rules</p><CardTitle className="mt-1">Signals</CardTitle></div><AlertTriangle className="size-5 text-primary" /></CardHeader><CardContent><div className="anomaly-list">{report.data.anomalies.map(anomaly => <article key={anomaly.code}><StatusBadge status={anomaly.severity} /><div><strong>{anomaly.code.replaceAll('_', ' ')}</strong><p>{anomaly.message}</p></div><span>{anomaly.value}</span></article>)}{!report.data.anomalies.length && <div className="empty-state"><CheckCircle2 /><p>No anomaly rule fired.</p></div>}</div></CardContent></Card>
      </div>
      <Card><CardHeader><p className="eyebrow">Tenant totals</p><CardTitle>Current local dataset</CardTitle></CardHeader><CardContent><pre className="json-block compact mt-0">{JSON.stringify(report.data.stats, null, 2)}</pre></CardContent></Card>
    </>}
  </>
}
