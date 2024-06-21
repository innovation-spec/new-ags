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
    const handler = () => setSystem(media.matches ? 'dark' : 'light')
    media.addEventListener('change', handler)
    return () => media.removeEventListener('change', handler)
  }, [])
  useEffect(() => {
    document.documentElement.classList.toggle('dark', resolvedTheme === 'dark')
    document.documentElement.style.colorScheme = resolvedTheme
  }, [resolvedTheme])
  const setTheme = (next: Theme) => { setThemeState(next); localStorage.setItem(STORAGE_KEY, next) }
  const value = useMemo(() => ({ theme, resolvedTheme, setTheme }), [theme, resolvedTheme])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() { const value = useContext(ThemeContext); if (!value) throw new Error('useTheme must be used inside ThemeProvider'); return value }
