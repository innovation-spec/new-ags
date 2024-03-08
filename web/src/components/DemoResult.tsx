import { CheckCircle2, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

type DemoKind = 'inventory' | 'state' | 'generic'
function number(value: unknown): number { return typeof value === 'number' ? value : Number(value ?? 0) }
export function demoPassed(kind: DemoKind, result: Record<string, unknown>): boolean | null {
  if (kind === 'inventory') { const initial = number(result.initial_stock); const successful = number(result.successful); const finalStock = (result.final_stock ?? {}) as Record<string, unknown>; const available = number(finalStock.available); return successful <= initial && available >= 0 && successful + number(result.rejected) === number(result.attempts) }
