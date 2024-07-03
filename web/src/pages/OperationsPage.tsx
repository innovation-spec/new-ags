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
