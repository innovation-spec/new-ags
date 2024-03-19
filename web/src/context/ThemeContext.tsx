import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

type Theme = 'dark' | 'light' | 'system'
type ThemeContextValue = { theme: Theme; resolvedTheme: 'dark' | 'light'; setTheme: (theme: Theme) => void }
const ThemeContext = createContext<ThemeContextValue | null>(null)
const STORAGE_KEY = 'agasthya.theme'

function systemTheme(): 'dark' | 'light' { return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light' }

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => (localStorage.getItem(STORAGE_KEY) as Theme | null) || 'dark')
  const [system, setSystem] = useState<'dark' | 'light'>(() => systemTheme())
  const resolvedTheme = theme === 'system' ? system : theme
  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
