import { render, screen } from '@testing-library/react'
import { it, expect } from 'vitest'
import { DemoResult } from './DemoResult'

it('marks inventory race as passed only when successful reservations do not exceed stock and availability stays non-negative', () => {
  render(<DemoResult title="Oversell" kind="inventory" result={{ initial_stock: 5, successful: 5, rejected: 95, final_stock: { available: 0 } }} />)
  expect(screen.getByText('PASS')).toBeInTheDocument()
})

it('marks a broken state conflict result as failed', () => {
