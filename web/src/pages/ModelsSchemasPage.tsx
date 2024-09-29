import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Box, Braces, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../api/client'
import { PageHeader } from '../components/PageHeader'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function ModelsSchemasPage() {
  const qc = useQueryClient()
  const models = useQuery({ queryKey: ['models'], queryFn: api.models.list })
