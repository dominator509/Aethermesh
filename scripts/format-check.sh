#!/usr/bin/env sh
set -eu

uv run ruff format --check .
echo "format check: ok" 
