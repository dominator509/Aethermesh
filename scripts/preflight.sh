#!/usr/bin/env sh
set -eu

cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
[ -f AGENTS.md ]      || { echo "ERROR: AGENTS.md missing"      >&2; exit 1; }
[ -f COMMANDS.md ]    || { echo "ERROR: COMMANDS.md missing"    >&2; exit 1; }
[ -f pyproject.toml ] || { echo "ERROR: pyproject.toml missing (run from repo root)" >&2; exit 1; }
command -v uv >/dev/null 2>&1 || {
  echo "ERROR: 'uv' not installed. See COMMANDS.md." >&2; exit 1; }
for s in scripts/lint.sh scripts/format-check.sh scripts/typecheck.sh \
         scripts/test-unit.sh scripts/test-integration.sh scripts/test-e2e.sh \
         scripts/build.sh scripts/security-check.sh scripts/dependency-audit.sh \
         scripts/smoke-test.sh scripts/verify.sh \
         scripts/production-readiness-check.sh scripts/install.sh; do
  [ -x "$s" ] || { echo "ERROR: $s missing or not executable" >&2; exit 1; }
done
echo "preflight: ok" 
