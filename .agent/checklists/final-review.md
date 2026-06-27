# Checklist — Final Review

End of every ExecPlan:

- [ ] Every Acceptance Criterion observably met.
- [ ] `./scripts/verify.sh` returns `verify: ok`.
- [ ] If applicable: `./scripts/production-readiness-check.sh` exits 0.
- [ ] `git diff --name-only` reconciles with Files to Change.
- [ ] Every file outside that list justified in Decision Log.
- [ ] Touched SPECs updated in same commit set.
- [ ] No secrets in diff.
- [ ] No production data changes (`/var/lib/aethermesh/`, `~/.aethermesh/`).
- [ ] Remaining risks recorded in Surprises & Discoveries.
- [ ] Outcomes & Retrospective filled.
- [ ] Final response composed per AGENTS.md § 15.
