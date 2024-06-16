import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi, it, expect } from 'vitest'
import { TenantProvider, useTenant } from './TenantContext'

vi.mock('../api/client', () => ({
  api: { tenants: { list: vi.fn().mockResolvedValue([{ id: 'tenant-a', name: 'North Shop' }, { id: 'tenant-b', name: 'South Shop' }]) } },
}))

function Consumer() {
  const { tenantId, tenants, setTenantId } = useTenant()
  return <div><span data-testid="tenant">{tenantId}</span>{tenants.map(t => <button key={t.id} onClick={() => setTenantId(t.id)}>{t.name}</button>)}</div>
}

it('loads tenants, selects the first tenant, and allows changing tenant', async () => {
  localStorage.clear()
  render(<QueryClientProvider client={new QueryClient()}><TenantProvider><Consumer /></TenantProvider></QueryClientProvider>)
  expect(await screen.findByText('North Shop')).toBeInTheDocument()
  expect(screen.getByTestId('tenant')).toHaveTextContent('tenant-a')
  await userEvent.click(screen.getByText('South Shop'))
  expect(screen.getByTestId('tenant')).toHaveTextContent('tenant-b')
  expect(localStorage.getItem('agasthya.tenant')).toBe('tenant-b')
})
