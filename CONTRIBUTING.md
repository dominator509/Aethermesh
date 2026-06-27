# CONTRIBUTING

## Setup
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo>
cd aethermesh
uv sync --all-extras --dev
./scripts/preflight.sh
```

## Branch Rules
- Short-lived branches off `main`: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`, `docs/<slug>`.
- One ExecPlan per branch.
- Rebase, do not merge `main` into the working branch.

## Coding Standards
- `ruff` (strict) for lint + format.
- `mypy --strict` for typing.
- Public APIs typed with concrete return types; no `Any` in protocol code.
- Module-level docstrings tie back to a SPEC section.

## Test Requirements
Per AGENTS.md § 10:
- New behavior ships with a fail-before / pass-after test.
- Coverage thresholds enforced in CI.
- No deleted passing tests in a fix without a Decision Log entry.

## Documentation Requirements
Per AGENTS.md § 11:
- Public contract change → relevant SPEC updated in the same commit.
- Architectural change → ARCHITECTURE.md + new ADR in the same commit.
- Command behavior change → COMMANDS.md updated in the same commit.

## Commit Guidance — Conventional Commits
```
feat(L4): add aep_capability_envelope MLS extension wiring
fix(L5): reject discharge whose binding_nonce is empty
docs(L1): clarify q-mix CID rotation cadence
chore(deps): bump cryptography 42.0.0 -> 42.0.5
test(L3): add regression for attestation report_data binding
```
Footer `BREAKING CHANGE:` triggers a major bump.

## Pull Request Checklist
- [ ] `./scripts/verify.sh` passes locally.
- [ ] `./scripts/security-check.sh` passes if crypto touched.
- [ ] No secrets in diff.
- [ ] No file outside ExecPlan's "Files to Change" (or justified in Decision Log).
- [ ] SPEC + ADR updated if architectural / public-contract change.
- [ ] CHANGELOG.md entry under `## Unreleased`.

## Code Review Checklist
- [ ] Layer import rules upheld (ARCHITECTURE.md § Dependency Rules).
- [ ] Hybrid PQ at every new cryptographic call site.
- [ ] No new FORBIDDEN_LOG_KEYS occurrence; redaction test still passes.
- [ ] Per-layer error taxonomy honored.
- [ ] Test coverage for new branches.
- [ ] No `TODO` / `FIXME` in `aethermesh/L*/`.

## Agent-Specific Contribution Rules
Coding agents must follow `AGENTS.md`. In particular:
- Use only commands from `COMMANDS.md`.
- Implement only the active ExecPlan's Scope.
- Stop only for STOP conditions in `AGENTS.md` § 4.
- Update Progress, Surprises & Discoveries, Decision Log, Outcomes & Retrospective as you work.
- Final response per `AGENTS.md` § 15.
