#!/usr/bin/env sh
set -eu

uv run pytest tests/integration -q
echo "integration tests: ok" 
