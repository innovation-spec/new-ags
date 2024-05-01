import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Bot, CornerDownLeft, Sparkles, UserRound } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import type { ChatResult } from '../api/types'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { ProductCard } from '../components/ProductCard'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'

type Message = { role: 'user' | 'assistant'; text: string; result?: ChatResult }
const suggestions = ['Recommend products that fit this customer', 'Show me good running products under $150', 'What should I recommend based on this customer profile?']

export function AssistantPage() {
  const { tenantId } = useTenant()
  const customers = useQuery({ queryKey: ['customers', tenantId], queryFn: () => api.tenants.customers(tenantId, 100), enabled: Boolean(tenantId) })
  const [customerId, setCustomerId] = useState('')
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const effectiveCustomer = customerId || customers.data?.[0]?.id || ''

  const chat = useMutation({
    mutationFn: (text: string) => api.agents.chat(tenantId, effectiveCustomer, text),
    onSuccess: (result) => {
      setMessages(prev => [...prev, { role: 'assistant', text: result.answer, result }])
      toast.success('Agent run completed', { description: `Run ${result.run.id.slice(0, 8)} is available in Agent Runs.` })
    },
    onError: (error) => {
      const text = error instanceof Error ? error.message : String(error)
      setMessages(prev => [...prev, { role: 'assistant', text }])
      toast.error('Assistant request failed', { description: text })
    },
  })

  const selectedCustomer = useMemo(() => customers.data?.find(c => c.id === effectiveCustomer), [customers.data, effectiveCustomer])
  const send = (text = input) => {
    const clean = text.trim()
    if (!clean || !effectiveCustomer || chat.isPending) return
    setMessages(prev => [...prev, { role: 'user', text: clean }])
    setInput('')
    chat.mutate(clean)
  }

  return <>
    <PageHeader eyebrow="OpenAI + deterministic tools" title="AI retail assistant" description="The LLM explains and selects tools; backend recommendation scores, inventory and tenant state remain authoritative." />
    {customers.isLoading ? <Loading /> : customers.error ? <ErrorState error={customers.error} /> : <div className="assistant-layout">
      <Card className="assistant-context">
        <CardContent className="p-5">
          <p className="eyebrow">Customer context</p>
          <div className="mt-4 space-y-2"><label className="text-xs font-medium text-muted-foreground">Customer</label><NativeSelect value={effectiveCustomer} onChange={e => setCustomerId(e.target.value)}>{customers.data?.map(customer => <NativeSelectOption key={customer.id} value={customer.id}>{customer.name}</NativeSelectOption>)}</NativeSelect></div>
          {selectedCustomer && <div className="profile-card"><div className="avatar"><UserRound /></div><h3>{selectedCustomer.name}</h3><StatusBadge status={selectedCustomer.segment || 'unsegmented'} /><small>{selectedCustomer.id}</small><pre className="json-block compact">{JSON.stringify(selectedCustomer.preferences, null, 2)}</pre></div>}
          <div className="context-note"><Sparkles className="size-4" /><span>Responses are grounded in products returned by the recommendation service.</span></div>
