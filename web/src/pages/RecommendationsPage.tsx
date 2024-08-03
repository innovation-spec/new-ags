import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { RefreshCw, Sparkles } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import type { Recommendation } from '../api/types'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ProductCard } from '../components/ProductCard'
import { ErrorState, Loading } from '../components/AsyncState'
import { MetricCard } from '../components/MetricCard'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'

export function RecommendationsPage() {
  const { tenantId } = useTenant()
  const customers = useQuery({ queryKey: ['customers', tenantId], queryFn: () => api.tenants.customers(tenantId, 100), enabled: Boolean(tenantId) })
  const [customerId, setCustomerId] = useState('')
  const [limit, setLimit] = useState(10)
