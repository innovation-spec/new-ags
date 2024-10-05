import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Box, Braces, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import { PageHeader } from '../components/PageHeader'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function ModelsSchemasPage() {
  const qc = useQueryClient()
  const models = useQuery({ queryKey: ['models'], queryFn: api.models.list })
  const schemas = useQuery({ queryKey: ['schemas'], queryFn: api.system.schemas })
  const [schemaName, setSchemaName] = useState('')
  const activate = useMutation({ mutationFn: ({ name, version }: { name: string; version: string }) => api.models.activate(name, version), onSuccess: async (_, vars) => { await qc.invalidateQueries({ queryKey: ['models'] }); toast.success(`${vars.name} ${vars.version} activated`) }, onError: error => toast.error('Model activation failed', { description: error instanceof Error ? error.message : String(error) }) })
  const names = Object.keys(schemas.data?.schemas ?? {})
  const activeSchema = schemaName || names[0] || ''

  return <>
