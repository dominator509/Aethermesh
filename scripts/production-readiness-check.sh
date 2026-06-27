#!/usr/bin/env sh
set -eu

cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
fail() { echo "production readiness: FAIL — $1" >&2; exit 1; }

echo "Gate 1: verify.sh"
./scripts/verify.sh || fail "verify.sh did not pass"

echo "Gate 2: placeholder PQ rejected in prod"
AEP_PQ_BACKEND=placeholder uv run python -m aethermesh.tools.smoke --prod 2>/dev/null \
  && fail "placeholder PQ was accepted in --prod mode" || true

echo "Gate 3: liboqs PQ accepted"
AEP_PQ_BACKEND=liboqs uv run python -m aethermesh.tools.smoke --prod \
  || fail "liboqs PQ smoke did not succeed"

echo "Gate 4: interop matrix"
uv run pytest tests/interop --slow -q || fail "interop matrix failed"

echo "Gate 5: performance baseline"
uv run pytest tests/perf --benchmark-only --benchmark-compare-fail=mean:10% \
  || fail "performance regression > 10%"

echo "Gate 6: security tests"
uv run pytest tests/security -q || fail "security tests failed"

echo "Gate 7: dependency audit"
uv run pip-audit || fail "pip-audit reported advisories"

echo "Gate 8: extended dependency audit"
./scripts/dependency-audit.sh || fail "dependency-audit.sh failed"

echo "Gate 9: log redaction"
uv run pytest tests/security/test_log_redaction.py -q || fail "log redaction test failed"

echo "Gate 10: node health"
uv run aethermesh node health >/dev/null 2>&1 \
  || fail "aethermesh node health did not return ok"

echo "Gate 11: no TODO/FIXME in protocol code"
git grep -nE "TODO|FIXME" aethermesh/L1_sphinx aethermesh/L2_dht \
  aethermesh/L3_handshake aethermesh/L4_ratchet aethermesh/L5_captokens \
  && fail "TODO/FIXME remain in protocol code" || true

echo "Gate 12: audit DB migrations sane"
uv run python -m aethermesh.tools.audit_db migrate --check \
  || fail "audit DB migration check failed"

echo "Gate 13: dashboards parse"
for d in ops/dashboards/*.json; do
  python -m json.tool < "$d" >/dev/null \
    || fail "dashboard $d does not parse as JSON"
done

echo "Gate 14: alert rules parse"
command -v promtool >/dev/null 2>&1 || fail "promtool not installed"
promtool check rules ops/alerts/aethermesh.rules.yml \
  || fail "promtool failed on alert rules"

echo "Gate 15: RELEASE_NOTES.md non-empty"
[ -s RELEASE_NOTES.md ] || fail "RELEASE_NOTES.md is missing or empty"

echo "Gate 16: ADR-0010 Accepted"
grep -q "^| ADR-0010 | Accepted" DECISIONS.md \
  || fail "ADR-0010 (security sign-off) is not marked Accepted"

echo "production readiness: ok" 
