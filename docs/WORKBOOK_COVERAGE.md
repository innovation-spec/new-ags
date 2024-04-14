# 2024 Engineering Workbook Coverage

This local demo maps the supplied Agasthya 2024 engineering workbook into executable product surfaces. The workbook records **403 tickets** and **13,936.52 reconstructed engineering hours** across nine phases. The mapping below is intended to make the technical work demonstrable; it is not a substitute for contemporaneous source-control, Jira/ADO, deployment, or test evidence.

| Phase | Workbook focus | Tickets | Hours | Demo implementation | React surface |
|---|---|---:|---:|---|---|
| P1 | Sequential state processing | 50 | 1,715.18 | Versioned shared state, operation IDs, deterministic patches | Shared State Lab |
| P2 | Synchronization & locking | 67 | 2,423.62 | Transactional reservations, optimistic/version conflict handling | Inventory, Shared State Lab, Demo Lab |
| P3 | Graph/state logging | 55 | 2,002.46 | Agent run/event lineage and state-event history | Agent Runs, Shared State Lab |
| P4 | Memory control | 40 | 1,361.16 | Working/persistent memory, TTL pruning, archive hooks | Memory |
| P5 | API resilience | 52 | 1,869.61 | Retry/backoff/fallback provider simulations | Resilience & PPO |
| P6 | Conflict priority / PPO | 49 | 1,784.90 | Credibility arbitration plus non-authoritative PPO shadow evaluation | Resilience & PPO |
| P7 | Monitoring / daily activity | 32 | 1,034.36 | Application-level 24-hour report and anomaly rules | Overview, Daily Operations |
| P8 | Schema consistency | 24 | 592.58 | Pydantic contract registry with registry version | Models & Schemas |
| P9 | CI/CD & scale | 34 | 1,152.65 | Docker Compose, deterministic bootstrap, concurrency/scenario tests | Demo Lab + verification scripts |

## What is deliberately local/demo scope

- Docker Compose rather than Kubernetes/EKS.
- Redis Streams rather than Kafka.
- MinIO rather than managed S3.
- Application-level status and daily reports rather than Prometheus/Grafana/OpenTelemetry.
- OpenAI API key only; no local model-serving infrastructure.
- React/Nginx UI over FastAPI; the browser never connects directly to PostgreSQL.

## Recommended next additions for a production-oriented phase

1. **Authentication and RBAC** — real identity provider, tenant membership, scoped roles, server-side authorization tests.
