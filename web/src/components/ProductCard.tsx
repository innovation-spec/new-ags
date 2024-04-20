import { Boxes, Sparkles } from 'lucide-react'
import type { RecommendationItem } from '../api/types'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

export function ProductCard({ item }: { item: RecommendationItem }) {
  const score = Number(item.score || 0)
