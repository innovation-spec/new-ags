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
