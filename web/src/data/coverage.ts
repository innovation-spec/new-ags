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
  { id: 'P4', title: 'Memory Control', tickets: 40, hours: 1361.16, objective: 'Retain useful context while pruning expired or reconstructible memory.', implementation: 'Redis working memory + PostgreSQL memory entries + TTL pruning + MinIO archives.', route: '/memory', evidence: ['TTL save', 'Prune action', 'Persistent memory list'] },
  { id: 'P5', title: 'API Resilience', tickets: 52, hours: 1869.61, objective: 'Recover from rate limits, timeouts and malformed external responses.', implementation: 'Retry/backoff and fallback-provider demo with persisted provenance.', route: '/resilience', evidence: ['Timeout scenario', '429 scenario', 'Fallback attempts'] },
  { id: 'P6', title: 'Conflict Priority & PPO', tickets: 49, hours: 1784.90, objective: 'Resolve conflicting sources using credibility and test PPO source selection safely.', implementation: 'Deterministic credibility remains authoritative; PPO runs in shadow mode.', route: '/resilience', evidence: ['Credibility selection', 'Source provenance', 'PPO before/after evaluation'] },
  { id: 'P7', title: 'Daily Monitoring', tickets: 32, hours: 1034.36, objective: 'Surface anomalous activity and failures from daily application records.', implementation: 'Daily operations report with agent failure, conflict and low-stock anomaly signals.', route: '/operations', evidence: ['24h report', 'Anomaly cards', 'Agent status chart'] },
  { id: 'P8', title: 'Schema Consistency', tickets: 24, hours: 592.58, objective: 'Normalize API, agent and event structures using stable contracts.', implementation: 'Versioned schema registry exposes the Pydantic contracts used by the API.', route: '/models', evidence: ['Schema version', 'JSON schema explorer', 'Model version registry'] },
  { id: 'P9', title: 'Containerization & Scale Validation', tickets: 34, hours: 1152.65, objective: 'Package the integrated system repeatably and exercise end-to-end scale/concurrency behavior.', implementation: 'Docker Compose local stack + automated test suites + interactive Demo Lab.', route: '/demo-lab', evidence: ['Compose stack', 'Concurrency tests', 'One-click demo suite'] },
]

export const workbookControls = {
  tickets: 403,
  hours: 13936.52,
  employeeTickets: 280,
  contractorTickets: 123,
}
