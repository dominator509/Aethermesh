#!/usr/bin/env sh
set -eu

uv run pytest tests/e2e -q
echo "e2e tests: ok" 
