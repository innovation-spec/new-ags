import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

type Theme = 'dark' | 'light' | 'system'
type ThemeContextValue = { theme: Theme; resolvedTheme: 'dark' | 'light'; setTheme: (theme: Theme) => void }
const ThemeContext = createContext<ThemeContextValue | null>(null)
const STORAGE_KEY = 'agasthya.theme'

function systemTheme(): 'dark' | 'light' { return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light' }
