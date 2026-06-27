# Prompt — Debug a Failing Validation Command

You are investigating a failing validation command. Goal: smallest fix that makes the command return its expected result.

## Placeholders
- `[FAILING_COMMAND]` — command that failed.
- `[EXPECTED_RESULT]` — what it should have returned.
- `[OBSERVED_OUTPUT]` — what it actually returned.
- `[EXECPLAN_PATH]` — active ExecPlan.

## Instructions
1. Read `AGENTS.md` § 7 (Anti-Fixation Rules) before doing anything.
2. **Do not** rewrite unrelated code.
3. Capture exact failing command and exact error output in ExecPlan's Surprises & Discoveries.
4. Form **one** hypothesis for root cause. Write it in Surprises & Discoveries.
5. Make smallest targeted fix consistent with the hypothesis.
6. Rerun a narrow form of the command (`pytest -k <one test>`).
7. Rerun the full validation command. Confirm `[EXPECTED_RESULT]`.

## Failure Counting
- **First same-root failure** — read error, smallest fix.
- **Second same-root failure** — narrower diagnostic; isolate.
- **Third same-root failure** — stop this approach. Record all failed hypotheses. Choose simpler implementation path. Update Decision Log.

After three same-root failures with no simpler path: STOP condition.

## Do Not
- Patch the test to make it pass.
- Weaken a SPEC contract to make the test pass.
- Silence the validation gate (e.g., skip the test) without a Decision Log entry.

## On Resolution
Resume the active ExecPlan's milestone flow.
