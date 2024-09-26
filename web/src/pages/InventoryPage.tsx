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
