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
