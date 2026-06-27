# Prompt — Final Review

You are performing final review at the end of an ExecPlan.

## Placeholder
- `[EXECPLAN_PATH]` — the ExecPlan being reviewed.

## Instructions
1. Run `./scripts/verify.sh`. Confirm `verify: ok`.
2. If the ExecPlan claims production-readiness impact, run `./scripts/production-readiness-check.sh`. Confirm `production readiness: ok` (or record which gate did not pass).
3. Run `git diff --name-only`. Compare against `[EXECPLAN_PATH]`'s "Files to Change." Extras justified in Decision Log.
4. Walk every Acceptance Criterion. Record per-criterion pass/fail in Outcomes & Retrospective.
5. Update **Outcomes & Retrospective**:
   - What landed.
   - What changed versus the plan.
   - Remaining risks (from Surprises & Discoveries).
6. If FORBIDDEN_LOG_KEYS could be touched, confirm `tests/security/test_log_redaction.py` still passes.
7. Produce final report per `AGENTS.md` § 15.

## Final Report Template (per AGENTS.md § 15)
```
1. ExecPlan completed: <path> — full / partial / stopped
2. Changed files: <git diff --name-only output>
3. Commands run: <ordered list with exit codes>
4. Command results: <key outputs>
5. Acceptance criteria status: <per criterion pass/fail>
6. Decisions made: <new Decision Log entries>
7. Assumptions confirmed/changed: <ASSUMPTIONS.md updates>
8. Remaining risks: <from Surprises & Discoveries>
9. Production-readiness status: <which gates pass/fail now>
```
If stopped at STOP condition, append:
```
Stopped at: <STOP condition>
Exact blocker: <one sentence>
Evidence: <terminal output or file excerpt>
Smallest decision needed: <one sentence>
Recommended default: <one sentence>
```
