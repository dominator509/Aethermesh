#!/usr/bin/env sh
set -eu

uv run python -m aethermesh.tools.smoke
echo "smoke test: ok" 
