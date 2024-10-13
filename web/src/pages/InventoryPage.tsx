import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Boxes, Check, Search, ShoppingBag } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import type { InventoryRow } from '../api/types'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export function InventoryPage() {
  const { tenantId } = useTenant()
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [selected, setSelected] = useState<InventoryRow | null>(null)
  const [quantity, setQuantity] = useState(1)
  const inventory = useQuery({ queryKey: ['inventory', tenantId, search, category], queryFn: () => api.inventory.list(tenantId, { search, category, limit: 300 }), enabled: Boolean(tenantId) })
  const categories = useMemo(() => Array.from(new Set((inventory.data ?? []).map(row => row.category))).sort(), [inventory.data])
  const ledger = useQuery({ queryKey: ['ledger', tenantId, selected?.sku_id], queryFn: () => api.inventory.ledger(tenantId, selected!.sku_id), enabled: Boolean(selected?.sku_id) })
  useEffect(() => {
    if (!selected || !inventory.data) return
    const fresh = inventory.data.find(row => row.inventory_id === selected.inventory_id)
    if (fresh && (fresh.version !== selected.version || fresh.available !== selected.available)) setSelected(fresh)
  }, [inventory.data, selected])

  const reserve = useMutation({
    mutationFn: () => api.inventory.reserve({ tenant_id: tenantId, sku_id: selected!.sku_id, quantity, idempotency_key: `web-${selected!.sku_id}-${Date.now()}` }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['inventory'] })
      await qc.invalidateQueries({ queryKey: ['ledger'] })
      toast.success('Reservation accepted', { description: `${quantity} unit${quantity === 1 ? '' : 's'} reserved and the ledger was updated.` })
    },
    onError: error => toast.error('Reservation failed', { description: error instanceof Error ? error.message : String(error) }),
  })

  return <>
    <PageHeader eyebrow="Transactional inventory" title="Catalog & inventory" description="Browse local PostgreSQL stock, inspect ledger history and exercise idempotent reservation behavior." />
    <Card className="mb-5"><CardContent className="flex flex-wrap items-end gap-3 p-4"><div className="relative min-w-[280px] flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search product, brand or SKU" className="pl-9" /></div><div className="min-w-[190px]"><NativeSelect value={category} onChange={e => setCategory(e.target.value)}><NativeSelectOption value="">All categories</NativeSelectOption>{categories.map(c => <NativeSelectOption value={c} key={c}>{c}</NativeSelectOption>)}</NativeSelect></div><span className="ml-auto text-sm text-muted-foreground">{inventory.data?.length ?? 0} stock rows</span></CardContent></Card>
    {inventory.isLoading ? <Loading /> : inventory.error ? <ErrorState error={inventory.error} /> : <Card className="overflow-hidden"><Table><TableHeader><TableRow><TableHead>Product</TableHead><TableHead>SKU</TableHead><TableHead>Warehouse</TableHead><TableHead>Price</TableHead><TableHead>On hand</TableHead><TableHead>Reserved</TableHead><TableHead>Available</TableHead><TableHead>State</TableHead><TableHead /></TableRow></TableHeader><TableBody>{inventory.data?.map(row => <TableRow key={row.inventory_id}><TableCell><strong className="block">{row.product_name}</strong><small className="text-muted-foreground">{row.brand} · {row.category}</small></TableCell><TableCell><code>{row.sku_code}</code></TableCell><TableCell>{row.warehouse_name}</TableCell><TableCell>${row.price.toFixed(2)}</TableCell><TableCell>{row.on_hand}</TableCell><TableCell>{row.reserved}</TableCell><TableCell className="font-semibold">{row.available}</TableCell><TableCell><StatusBadge status={row.available === 0 ? 'unavailable' : row.available <= 2 ? 'low stock' : 'ok'} /></TableCell><TableCell><Button variant="outline" size="sm" onClick={() => { setSelected(row); setQuantity(1); reserve.reset() }}>Inspect</Button></TableCell></TableRow>)}</TableBody></Table></Card>}

    <Sheet open={Boolean(selected)} onOpenChange={(open) => { if (!open) setSelected(null) }}>
      <SheetContent className="overflow-y-auto sm:max-w-xl">{selected && <>
        <SheetHeader><p className="eyebrow">Inventory detail</p><SheetTitle>{selected.product_name}</SheetTitle><SheetDescription>{selected.sku_code} · {selected.warehouse_name}</SheetDescription></SheetHeader>
        <div className="stock-summary"><div><span>On hand</span><strong>{selected.on_hand}</strong></div><div><span>Reserved</span><strong>{selected.reserved}</strong></div><div><span>Available</span><strong>{selected.available}</strong></div><div><span>Version</span><strong>v{selected.version}</strong></div></div>
        <Card className="mb-5"><CardContent className="p-4"><div className="mb-3 flex items-center gap-2 font-semibold"><ShoppingBag className="size-4" />Reserve stock</div><label className="space-y-2 text-sm"><span className="text-muted-foreground">Quantity</span><Input type="number" min={1} max={Math.max(1, selected.available)} value={quantity} onChange={e => setQuantity(Math.max(1, Number(e.target.value)))} /></label><Button className="mt-3 w-full" disabled={reserve.isPending || selected.available < quantity} onClick={() => reserve.mutate()}>{reserve.isPending ? 'Reserving…' : 'Create reservation'}</Button>{reserve.isSuccess && <div className="inline-success"><Check className="size-4" />Reservation accepted and ledger updated.</div>}{reserve.error && <div className="inline-error">{reserve.error instanceof Error ? reserve.error.message : String(reserve.error)}</div>}</CardContent></Card>
        <div className="flex items-center justify-between"><h3 className="font-semibold">Ledger</h3><span className="text-xs text-muted-foreground">{ledger.data?.length ?? 0} events</span></div>{ledger.isLoading ? <Loading /> : <div className="timeline mt-4">{ledger.data?.map(event => <div className="timeline-item" key={event.id}><span className="timeline-dot" /><div><strong>{event.event_type}</strong><small>{event.created_at ? new Date(event.created_at).toLocaleString() : 'time unavailable'}</small><p>{event.quantity_delta > 0 ? '+' : ''}{event.quantity_delta} · {event.reference_id || 'no reference'}</p></div></div>)}{!ledger.data?.length && <div className="empty-state"><Boxes /><p>No ledger events for this SKU yet.</p></div>}</div>}
      </>}</SheetContent>
    </Sheet>
  </>
}
