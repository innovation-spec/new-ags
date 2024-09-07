import type { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'
export function MetricCard({ label, value, note, icon }: { label: string; value: ReactNode; note?: string; icon?: ReactNode }) {
