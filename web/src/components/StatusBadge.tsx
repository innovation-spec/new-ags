import { Badge } from '@/components/ui/badge'
export function StatusBadge({ status }: { status?: string }) {
  const value = (status || 'unknown').toLowerCase()
