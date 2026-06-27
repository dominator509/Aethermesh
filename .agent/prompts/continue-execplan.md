# Prompt — Continue a Partially Completed ExecPlan

You are a coding agent resuming an ExecPlan started by another agent (or in a prior session).

## Placeholder
- `[EXECPLAN_PATH]` — the ExecPlan to resume.

## Instructions
1. Read `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`, and `[EXECPLAN_PATH]` in full.
2. Inspect `[EXECPLAN_PATH]`'s **Progress** section. Identify the first incomplete milestone (`- [ ]`).
3. Inspect **Surprises & Discoveries**. Take prior surprises into account.
4. Inspect the **Decision Log**. Honor prior decisions; if a decision is now wrong, add a new entry overriding it.
5. Run `./scripts/preflight.sh`. Confirm `preflight: ok`.
6. Re-validate any prior milestones whose ticks lack evidence in Decision Log. If a tick can't be re-justified, un-tick and re-execute.
7. Resume at first incomplete milestone. Follow `.agent/prompts/execute-active-execplan.md`.

## Do Not
- Restart from milestone 1 if existing progress is sound.
- Roll back completed milestones without a Decision Log entry.
- Ask the user for next steps unless a STOP condition applies.

## Final Response
Per `AGENTS.md` § 15.
