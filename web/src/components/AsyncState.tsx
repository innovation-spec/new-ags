import { AlertTriangle, LoaderCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

export function Loading({ label = 'Loading local data…' }: { label?: string }) {
  return <div className="space-y-3 rounded-xl border bg-card p-5"><div className="flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" />{label}</div><Skeleton className="h-4 w-3/4" /><Skeleton className="h-20 w-full" /></div>
}
export function ErrorState({ error }: { error: unknown }) {
  return <Alert variant="destructive"><AlertTriangle className="size-4" /><AlertTitle>Request failed</AlertTitle><AlertDescription>{error instanceof Error ? error.message : String(error)}</AlertDescription></Alert>
}
