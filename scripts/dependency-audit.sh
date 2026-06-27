#!/usr/bin/env sh
set -eu

uv run pip-audit
echo "dependency audit: ok" 
