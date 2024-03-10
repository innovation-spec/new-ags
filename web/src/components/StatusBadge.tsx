import { Badge } from '@/components/ui/badge'
export function StatusBadge({ status }: { status?: string }) {
  const value = (status || 'unknown').toLowerCase()
  const variant = ['ok', 'enabled', 'completed', 'active', 'healthy', 'applied', 'merged'].includes(value)
    ? 'success' as const
