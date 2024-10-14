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
    <PageHeader eyebrow="Phase 8" title="Models & schema consistency" description="Inspect MinIO-backed model versions and the normalized Pydantic contracts exchanged by agents and services." />
    <div className="two-column">
      <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Model registry</p><CardTitle className="mt-1">Artifacts & activation</CardTitle></div><Box className="size-5 text-primary" /></CardHeader><CardContent>{models.isLoading ? <Loading /> : models.error ? <ErrorState error={models.error} /> : <div className="model-list">{models.data?.map(model => <div key={model.name} className="model-group"><h3>{model.name}</h3>{model.versions.map(version => <Card key={version.version}><CardContent className="grid grid-cols-[1fr_auto] gap-2 p-4"><div><strong>{version.version}</strong><small className="block text-muted-foreground">{version.algorithm} · {version.object_path}</small></div><div>{version.active ? <StatusBadge status="active" /> : <Button size="sm" variant="outline" disabled={activate.isPending} onClick={() => activate.mutate({ name: model.name, version: version.version })}>Activate</Button>}</div><pre className="json-block compact col-span-2">{JSON.stringify(version.metrics, null, 2)}</pre></CardContent></Card>)}</div>)}{!models.data?.length && <div className="empty-state"><Box /><p>No registered models. Run the bootstrap/training script.</p></div>}</div>}</CardContent></Card>
      <Card><CardHeader className="flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Schema registry {schemas.data?.registry_version}</p><CardTitle className="mt-1">Unified contracts</CardTitle></div><Braces className="size-5 text-primary" /></CardHeader><CardContent>{schemas.isLoading ? <Loading /> : schemas.error ? <ErrorState error={schemas.error} /> : <>{names.length > 0 && <Tabs value={activeSchema} onValueChange={setSchemaName}><TabsList className="mb-3 h-auto max-w-full flex-wrap justify-start">{names.map(name => <TabsTrigger key={name} value={name}>{name}</TabsTrigger>)}</TabsList></Tabs>}{activeSchema && <><div className="inline-success"><CheckCircle2 className="size-4" />Versioned API contract available from FastAPI/Pydantic.</div><pre className="json-block schema-block">{JSON.stringify(schemas.data?.schemas[activeSchema], null, 2)}</pre></>}</>}</CardContent></Card>
    </div>
  </>
}
