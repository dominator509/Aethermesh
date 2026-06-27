#!/usr/bin/env sh
set -eu

uv run ruff check .
echo "lint: ok" 
