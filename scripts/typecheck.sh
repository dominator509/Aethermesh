#!/usr/bin/env sh
set -eu

uv run mypy aethermesh tests
echo "typecheck: ok" 
