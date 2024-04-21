import { Badge } from '@/components/ui/badge'
export function StatusBadge({ status }: { status?: string }) {
  const value = (status || 'unknown').toLowerCase()
  const variant = ['ok', 'enabled', 'completed', 'active', 'healthy', 'applied', 'merged'].includes(value)
    ? 'success' as const
    : ['failed', 'unavailable', 'rejected_conflict', 'error'].includes(value) ? 'destructive' as const
      : ['disabled', 'created', 'planning', 'running', 'waiting_tool', 'validating', 'low stock', 'medium'].includes(value) ? 'warning' as const : 'outline' as const
