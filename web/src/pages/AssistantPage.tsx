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

