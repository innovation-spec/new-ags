import { Boxes, Sparkles } from 'lucide-react'
import type { RecommendationItem } from '../api/types'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

export function ProductCard({ item }: { item: RecommendationItem }) {
  const score = Number(item.score || 0)
  return <Card className="overflow-hidden"><CardContent className="p-4"><div className="flex gap-4"><div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-primary/10 text-sm font-bold text-primary">#{item.rank}</div><div className="min-w-0 flex-1"><div className="flex items-start justify-between gap-4"><div><p className="eyebrow">{item.brand || item.category || 'Recommended item'}</p><h3 className="mt-1 font-semibold">{item.name}</h3></div>{item.price !== undefined && <strong className="text-lg">${item.price.toFixed(2)}</strong>}</div><Progress value={score * 100} className="my-3" /><div className="flex flex-wrap gap-3 text-xs text-muted-foreground"><span className="inline-flex items-center gap-1"><Sparkles className="size-3.5" />Score {score.toFixed(3)}</span>{item.available !== undefined && <span className="inline-flex items-center gap-1"><Boxes className="size-3.5" />{item.available} available</span>}</div>{item.reasons && <div className="mt-3 flex flex-wrap gap-1.5">{Object.entries(item.reasons).slice(0, 4).map(([key, value]) => <Badge variant="secondary" key={key}>{key.replaceAll('_', ' ')}: {typeof value === 'number' ? value.toFixed(2) : String(value)}</Badge>)}</div>}</div></div></CardContent></Card>
}
