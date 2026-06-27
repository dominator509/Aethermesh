# .agent/PLANS.md — ExecPlan Standard

An ExecPlan is a self-contained implementation document for one feature or system change. **A new agent with no prior conversation must be able to continue from the ExecPlan alone.**

## Required Sections (in order)
1. **Purpose / Big Picture**
2. **Scope**
3. **Non-goals**
4. **Context and Orientation**
5. **Files to Read First** (≤ 8 paths)
6. **Files to Change** (exact paths)
7. **Interfaces and Contracts**
8. **Milestones**
9. **Concrete Steps**
10. **Validation and Acceptance**
11. **Idempotence and Recovery**
12. **Progress** (checkbox list)
13. **Surprises & Discoveries**
14. **Decision Log**
15. **Outcomes & Retrospective**

## Milestone Structure
Every milestone has:
- **Goal** — one sentence.
- **Files to Read** — ≤ 5 paths.
- **Files to Change** — exact paths.
- **Exact Edits Expected** — bullet list.
- **Validation Command** — exact command from `COMMANDS.md`.
- **Expected Result** — string / exit code that signals success.
- **Recovery Instruction** — anti-fixation per AGENTS.md § 7.

## Execution Rules
- Implement milestones in numeric order.
- After every milestone: run validation, confirm result, tick Progress, update Surprises & Discoveries / Decision Log if relevant.
- Continue autonomously to next milestone unless STOP condition applies.

## Validation Rules
- Every milestone validation command must exist in `COMMANDS.md`.
- Validation may be a test, a script, or a verification command.
- Manual inspection is not acceptable.

## Acceptance Rules
- Cumulative Acceptance Criteria define completion.
- Each item is observable (exit code, log line, metric value).

## Idempotence Rules
- Same edit twice yields same result.
- Tests are safe to re-run.
- DB migrations are idempotent.

## Recovery Rules
- Anti-fixation per AGENTS.md § 7.
- Three same-root failures with no simpler path → STOP.

## Progress Update Rules
- `- [ ]` / `- [x]` markers.
- Never tick a box before its validation command returned the expected result.
- Never delete a Progress entry; reorders / skips go in Decision Log.

## Decision Log Rules
- One entry per non-trivial choice (renamed file, added dep, deviated from spec).
- Each entry: context, decision, alternatives, consequences, ADR reference if architectural.

## Completion Rules
ExecPlan complete when **all**:
- Every Progress checkbox ticked.
- Every Acceptance Criterion verified.
- `./scripts/verify.sh` returns `verify: ok`.
- `git diff --name-only` matches Files to Change (extras justified).
- Outcomes & Retrospective filled.
- Surprises & Discoveries reflects current state.
