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
