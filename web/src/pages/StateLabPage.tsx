import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { GitBranch, Play, PlusCircle } from 'lucide-react'
import { toast } from 'sonner'
import { api, ApiError } from '../api/client'
import { useTenant } from '../context/TenantContext'
import { PageHeader } from '../components/PageHeader'
import { DemoResult } from '../components/DemoResult'
import { ErrorState, Loading } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'

export function StateLabPage() {
  const { tenantId } = useTenant()
  const qc = useQueryClient()
  const [entityType, setEntityType] = useState('customer')
  const [entityId, setEntityId] = useState('demo-customer-state')
  const [patchText, setPatchText] = useState('{\n  "interests": ["running"]\n}')
