#!/usr/bin/env sh
set -eu

uv run bandit -r aethermesh -ll -q
uv run pytest tests/security -q
echo "security check: ok" 
