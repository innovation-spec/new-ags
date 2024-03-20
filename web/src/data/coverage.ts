export type CoveragePhase = {
  id: string
  title: string
  tickets: number
  hours: number
  objective: string
  implementation: string
  route: string
  evidence: string[]
}

export const coveragePhases: CoveragePhase[] = [
  { id: 'P1', title: 'Sequential State Processing', tickets: 50, hours: 1715.18, objective: 'Establish controlled shared-state updates and traceable sequential task status.', implementation: 'Versioned SharedState + StateEvent coordinator with idempotent operations.', route: '/state', evidence: ['State version viewer', 'Manual patching', 'Conflict stress scenario'] },
  { id: 'P2', title: 'Synchronization & Locking', tickets: 67, hours: 2423.62, objective: 'Synchronize agent and inventory changes without uncontrolled parallel writes.', implementation: 'Transactional inventory reservations and merge-safe state updates.', route: '/inventory', evidence: ['Oversell prevention', 'Row locking', 'Idempotency'] },
  { id: 'P3', title: 'Graph / State Logging', tickets: 55, hours: 2002.46, objective: 'Make agent/model state transitions replayable and auditable.', implementation: 'AgentEvent and StateEvent lineage timelines exposed in the console.', route: '/agents', evidence: ['Run timeline', 'Tool events', 'State event lineage'] },
