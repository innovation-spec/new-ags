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
