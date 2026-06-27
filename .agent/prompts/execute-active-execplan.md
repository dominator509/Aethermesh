# Prompt — Execute Active ExecPlan

You are a coding agent. Execute the active ExecPlan to completion.

## Placeholders
- `[EXECPLAN_PATH]` — e.g. `.agent/execplans/EP-001-foundation.md`.
- `[OPTIONAL_USER_REQUEST]` — additional instruction; ignore if empty.

## Instructions
1. Read `AGENTS.md` in full.
2. Read `COMMANDS.md` in full.
3. Read `.agent/PLANS.md` in full.
4. Read `[EXECPLAN_PATH]` in full.
5. Run `./scripts/preflight.sh`. Confirm `preflight: ok`. Fix any blocker before proceeding.
6. For each milestone, in numeric order:
   a. Read the milestone's "Files to Read."
   b. Make exactly the edits in "Exact Edits Expected."
   c. Run the milestone's "Validation Command."
   d. Confirm the "Expected Result."
   e. Tick the Progress checkbox in `[EXECPLAN_PATH]`.
   f. Update Surprises & Discoveries / Decision Log if relevant.
7. After last milestone: run `./scripts/verify.sh` and confirm `verify: ok`.
8. Run `.agent/prompts/final-review.md`.
9. Produce final response per `AGENTS.md` § 15.

## Do Not
- Do not ask the user for next steps.
- Do not implement from `ROADMAP.md` directly.
- Do not broaden scope beyond the active ExecPlan.
- Do not invent commands; use only `COMMANDS.md`.
- Do not add a dependency without an ADR.
- Do not stop unless a STOP condition in `AGENTS.md` § 4 applies.

## On Validation Failure
Follow anti-fixation rule (AGENTS.md § 7).

## On STOP Condition
Stop and report per AGENTS.md § 15 stop format.

[OPTIONAL_USER_REQUEST]
