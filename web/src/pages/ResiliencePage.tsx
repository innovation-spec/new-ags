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
