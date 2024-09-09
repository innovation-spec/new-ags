import type { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'
export function MetricCard({ label, value, note, icon }: { label: string; value: ReactNode; note?: string; icon?: ReactNode }) {
  return <Card className="metric-card"><CardContent className="flex w-full items-center gap-3 p-4"><div className="metric-icon">{icon}</div><div className="min-w-0"><span>{label}</span><strong>{value}</strong>{note && <small>{note}</small>}</div></CardContent></Card>
