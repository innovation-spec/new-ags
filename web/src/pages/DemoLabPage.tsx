import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Boxes, BrainCircuit, FlaskConical, GitBranch, Play, RefreshCw, ShieldCheck, Sparkles } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { DemoResult } from '../components/DemoResult'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

type ResultEntry = { id: string; title: string; kind: 'inventory' | 'state' | 'generic'; result: Record<string, unknown> }

export function DemoLabPage() {
  const { tenantId } = useTenant()
