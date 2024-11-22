#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

printf '\n== Backend, scenario and concurrency tests ==\n'
PYTHONPATH=backend pytest -q backend/tests tests/demo_scenarios tests/concurrency

printf '\n== Python compile check ==\n'
python -m compileall -q backend/app backend/tests tests scripts

printf '\n== React tests/typecheck/build ==\n'
if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required for React verification" >&2
  exit 1
fi
if [ ! -d web/node_modules ]; then
  npm --prefix web install
fi
npm --prefix web test
npm --prefix web run typecheck
npm --prefix web run build

printf '\n== Docker Compose config ==\n'
if command -v docker >/dev/null 2>&1; then
  docker compose config >/dev/null
  echo "docker compose config: OK"
else
  echo "Docker not installed; skipped Compose runtime validation."
fi

printf '\nAll available project checks completed.\n'
printf 'For live checks after docker compose up --build:\n'
printf '  RUN_INFRA_TESTS=1 PYTHONPATH=backend pytest -q tests/integration/test_infrastructure.py\n'
printf '  SMOKE_BASE_URL=http://localhost:18000 PYTHONPATH=backend pytest -q tests/integration/test_smoke.py\n'
printf '  WEB_BASE_URL=http://localhost:13000 PYTHONPATH=backend pytest -q tests/integration/test_web_console.py\n'
