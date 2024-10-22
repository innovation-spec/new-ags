#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

printf '\n== Backend, scenario and concurrency tests ==\n'
PYTHONPATH=backend pytest -q backend/tests tests/demo_scenarios tests/concurrency

printf '\n== Python compile check ==\n'
