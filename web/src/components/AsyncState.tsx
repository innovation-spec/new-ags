import { AlertTriangle, LoaderCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

export function Loading({ label = 'Loading local data…' }: { label?: string }) {
