import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { App } from './App'
import { TenantProvider } from './context/TenantContext'
import { ThemeProvider } from './context/ThemeContext'
import { Toaster } from './components/ui/sonner'
import './styles.css'

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 10_000, refetchOnWindowFocus: false }, mutations: { retry: 0 } } })

