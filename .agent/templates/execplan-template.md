# EP-NNN — <Title>

- **Status:** Draft / In Progress / Complete
- **Owner:** <name>
- **Linked Phase:** <Phase N>
- **Linked Specs:** <SPEC-XXX>
- **Related ADRs:** <ADR-NNNN if any>

## 1. Purpose / Big Picture
<Why this ExecPlan; what user outcome or production-readiness gate it advances.>

## 2. Scope
- <module / behavior / file>

## 3. Non-Goals
- <thing this plan does NOT touch>

## 4. Context and Orientation
<One paragraph on prior repo state relevant to this plan.>

## 5. Files to Read First
1. `AGENTS.md`
2. `COMMANDS.md`
3. `.agent/PLANS.md`
4. `<spec or architecture file>`
5. `<existing repo file>`
6. `<test file>`

## 6. Files to Change
- `aethermesh/<layer>/<module>.py`
- `tests/unit/<layer>/test_<module>.py`

## 7. Interfaces and Contracts
<New/modified public APIs, wire fields, env vars, CLI commands. Cite SPEC sections.>

## 8. Milestones
### Milestone 1 — <Title>
- **Goal:** <one sentence>
- **Files to Read:** <≤ 5>
- **Files to Change:** <exact>
- **Exact Edits Expected:** <bullets>
- **Validation Command:** `<exact command from COMMANDS.md>`
- **Expected Result:** `<exact string / exit code>`
- **Recovery Instruction:** Per AGENTS.md § 7. On 3rd same-root failure, record + STOP.

### Milestone 2 — <Title>
<same structure>

## 9. Concrete Steps
<Numbered steps per milestone with exact edits.>

## 10. Validation and Acceptance
### Per-Milestone
<table mirroring § 8>

### Acceptance Criteria (cumulative)
- [ ] <observable criterion>
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
<How to resume; what is safe to re-run.>

## 12. Progress
- [ ] Milestone 1 — <Title>
- [ ] Milestone 2 — <Title>
- [ ] Final review

## 13. Surprises & Discoveries
<Filled as work proceeds.>

## 14. Decision Log
- **Decision:** <decision>
  - **Context:** <context>
  - **Alternatives:** <alts>
  - **Consequences:** <consequences>
  - **References:** <ADR-NNNN or SPEC section>

## 15. Outcomes & Retrospective
<Filled at completion.>
- **What landed:**
- **What changed versus the plan:**
- **Remaining risks:**
- **Production-readiness impact:**
