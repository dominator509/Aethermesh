#!/usr/bin/env sh
set -eu

uv run pytest tests/unit -q
echo "unit tests: ok" 
